# Copyright (C) 2026 Advanced Micro Devices, Inc. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

#!/usr/bin/env python3
"""emo_v2.py - Reachy Mini Chat with Piper-TTS (Offline)

    ┌───────────────────────────────────────────────────────────────┐
    │  LAB EDIT?  Jump to the "# >>> TRY ME <<<" block below          │
    │  (press Ctrl+F, search: TRY ME) to tweak the persona, voice,    │
    │  or switch on voice chat. Save, then re-run.                    │
    └───────────────────────────────────────────────────────────────┘

Replaces Edge-TTS with Piper-TTS for fully offline operation.

Usage:
  python lab/emo_v2.py --piper-model  models/en-us-blizzard_lessac-medium.onnx  # Run with specific Piper model
  python lab/emo_v2.py --asr                                                    # Enable ASR
  python lab/emo_v2.py --model qwen3.5:0.8b                                     # Set Ollama model
"""

import os
import sys
import time
import json
import logging
import argparse
import threading
import asyncio
from typing import Optional, Tuple
from contextlib import suppress

# Import from existing modules
# Add this file's dir (for sibling emo_v*.py) and the repo root (for `utils/`),
# so the script works when run as `python lab/emo_v2.py` from the repo root.
_here = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_here)
sys.path.append(os.path.dirname(_here))

from emo_v1 import EmotionControllerV6, strip_emojis


# Silence the Reachy SDK's intentionally-unused media subsystem (see the detailed
# note in emo_v1.py). Repeated here so the suppression still applies when this
# script is run directly. Idempotent; runs before the robot connects.
def _drop_audio_not_initialized(record: logging.LogRecord) -> bool:
    return "Audio system is not initialized." not in record.getMessage()


logging.getLogger("reachy_mini.media.media_manager").addFilter(
    _drop_audio_not_initialized
)
logging.getLogger("reachy_mini.media").setLevel(logging.ERROR)


# ============================================================================
# >>> TRY ME <<<  Mini-lab Task 2
# Everything in this task runs 100% offline on the AMD machine: the LLM
# (Ollama), the voice (Piper), and the speech recognition (faster-whisper).
# Edit below, then re-run `python lab/emo_v2.py --chat`. To prove it's offline,
# unplug the network and keep chatting — Reachy won't miss a beat.
# ============================================================================

# 1) Reachy's personality (sent to the local LLM as a system prompt).
#    The "one or two short sentences" instruction keeps replies snappy — great
#    for a busy booth, and faster to speak. Lengthen it if you want more chat.
ROBOT_PERSONA = (
    "respond like a pirate"
    "You are a cute desktop robot assistant. Respond with enthusiasm and warmth, "
    "in two or three short sentences. Keep it brief and conversational. "
    "Always respond in the same language as the user's message."
)

# 2) The offline Piper voice used by default. Swap to another .onnx in models/
#    (e.g. models/zh_CN-huayan-medium.onnx for Chinese).
DEFAULT_PIPER_MODEL = "models/en-us-blizzard_lessac-medium.onnx"

# 3) Talk to Reachy with your VOICE instead of typing.
#    Set to True to use the microphone (offline faster-whisper speech recognition),
#    then just run `python lab/emo_v2.py` — no extra flags needed.
USE_VOICE_CHAT = False

# 4) Language for voice chat (only used when USE_VOICE_CHAT = True).
#    Valid values: "auto" (auto-detect), "en" (English), "zh" (Chinese).
VOICE_CHAT_LANG = "auto"
# ============================================================================


def check_runtime_dependencies(require_reachy: bool = False) -> bool:
    """Check that optional runtime deps are importable."""
    missing = []
    try:
        import aiohttp  # noqa: F401
    except Exception:
        missing.append("aiohttp")
    if require_reachy:
        try:
            import reachy_mini  # noqa: F401
        except Exception:
            missing.append("reachy-mini")
    if missing:
        print(f"❌ Missing runtime dependencies: {', '.join(missing)}")
        print("   Install: pip install -r requirements.txt")
        if "reachy-mini" in missing:
            print("   For robot: pip install 'reachy-mini[mujoco]'")
        return False
    return True


# Optional faster-whisper ASR engine
try:
    from utils.asr import FasterWhisperASREngine
except Exception:
    try:
        from .utils.asr import FasterWhisperASREngine
    except Exception:
        FasterWhisperASREngine = None


class PiperTTSEngine:
    """Piper-TTS engine wrapper for offline speech synthesis."""

    def __init__(
        self,
        model_path: str,
        config_path: str = None,
        speaker_id: int = 0,
        debug: bool = False,
    ):
        self.debug = debug
        self.model_path = model_path
        self.config_path = config_path
        self.speaker_id = speaker_id
        self.voice = None

        try:
            from piper import PiperVoice, PiperConfig

            # Import SynthesisConfig if available, else use default dict
            try:
                from piper import SynthesisConfig

                self.SynthesisConfig = SynthesisConfig
            except ImportError:
                self.SynthesisConfig = None

            import onnxruntime

            self.PiperVoice = PiperVoice
            self.PiperConfig = PiperConfig
            self.onnxruntime = onnxruntime
        except ImportError:
            print("❌ piper-tts not installed. Install with: pip install piper-tts")
            return

        if not os.path.exists(model_path):
            print(f"❌ Piper model not found at: {model_path}")

            # Try to find any onnx model in models/ or current directory
            print("🔍 Searching for available models...")
            found_models = []
            for search_dir in [".", "models"]:
                if os.path.exists(search_dir):
                    for f in os.listdir(search_dir):
                        if f.endswith(".onnx"):
                            found_models.append(os.path.join(search_dir, f))

            if found_models:
                print(f"💡 Found available models:")
                for m in found_models:
                    print(f"   --piper-model {m}")
                print(
                    f"\nExample: python lab/emo_v2.py --piper-model {found_models[0]}"
                )
            else:
                print(
                    "⚠️ No .onnx models found. Please download one from https://github.com/rhasspy/piper/releases/tag/v0.0.2"
                )

            self.voice = None
            return

        try:
            # If config path not provided, assume .json with same name as .onnx
            if not config_path:
                potential_config = model_path + ".json"
                if os.path.exists(potential_config):
                    self.config_path = potential_config

            print(f"🎙️ Loading Piper model: {model_path}")

            # Manually load config to fix legacy phoneme_type issue
            with open(
                self.config_path or (model_path + ".json"), "r", encoding="utf-8"
            ) as f:
                config_dict = json.load(f)

            # FIX: Replace legacy "PhonemeType.ESPEAK" string with "espeak"
            if config_dict.get("phoneme_type") == "PhonemeType.ESPEAK":
                print("🔧 Fixing legacy phoneme_type in config...")
                config_dict["phoneme_type"] = "espeak"

            # Create config object
            config = self.PiperConfig.from_dict(config_dict)

            # Create ONNX session
            session = self.onnxruntime.InferenceSession(
                str(model_path),
                sess_options=self.onnxruntime.SessionOptions(),
                providers=["CPUExecutionProvider"],
            )

            # Initialize voice manually
            self.voice = self.PiperVoice(session=session, config=config)

            print(f"✅ Piper TTS initialized")

        except Exception as e:
            print(f"❌ Failed to load Piper model: {e}")
            self.voice = None

    def speak_with_emotion(self, text: str, emotion: str = "neutral"):
        """Speak text using Piper (blocking)."""
        text = strip_emojis(text)
        if not text.strip():
            return

        if not self.voice:
            print(f"⚠️ Piper voice not loaded. Skipping speech: '{text[:20]}...'")
            return

        try:
            import tempfile
            import wave
            import numpy as np
            import soundfile as sf
            import sounddevice as sd

            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            # Synthesize to file
            with wave.open(tmp_path, "wb") as wav_file:
                # Use synthesize_wav which handles wave header automatically
                syn_config = None
                if self.SynthesisConfig and self.speaker_id is not None:
                    syn_config = self.SynthesisConfig(speaker_id=self.speaker_id)

                self.voice.synthesize_wav(text, wav_file, syn_config=syn_config)

            # Read and play
            data, sr = sf.read(tmp_path, dtype="float32")
            if data.size > 0:
                sd.play(data, samplerate=sr)
                sd.wait()

            # Cleanup
            try:
                os.remove(tmp_path)
            except Exception:
                pass

        except Exception as e:
            print(f"⚠️ Piper TTS error: {e}")

    async def speak_with_emotion_async(self, text: str, emotion: str = "neutral"):
        """Async version of speak_with_emotion (runs in thread)."""
        import asyncio

        # Piper synthesis is CPU bound, so run in a separate thread
        await asyncio.to_thread(self.speak_with_emotion, text, emotion)


class EmotionControllerV71(EmotionControllerV6):
    """Emotion controller using Piper-TTS instead of Edge-TTS."""

    def __init__(
        self,
        reachy,
        piper_model: str,
        piper_config: str = None,
        speaker_id: int = 0,
        debug: bool = False,
        gentle_mode: bool = False,
    ):
        # Initialize parent with gentle_mode support
        super().__init__(reachy, debug=debug, gentle_mode=gentle_mode)

        # Override TTS engine
        self.tts_engine = PiperTTSEngine(piper_model, piper_config, speaker_id, debug)


class ChatAppWithPiper:
    def __init__(
        self,
        model: str = "qwen3.5:0.8b",
        ollama_url: str = "http://127.0.0.1:11434",
        piper_model: str = "en_US-libritts_r-medium.onnx",
        piper_config: str = None,
        speaker_id: int = 0,
        debug: bool = False,
        use_asr: str = None,
        gentle: bool = False,
    ):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.use_asr = use_asr is not None
        self.asr = use_asr
        self.gentle = gentle
        self.piper_model = piper_model
        self.piper_config = piper_config
        self.speaker_id = speaker_id

        self.controller = None
        self.asr_engine = None

    async def check_ollama_model(self, session) -> bool:
        """Check if the requested model is available in Ollama."""
        try:
            print(f"🔍 Checking Ollama model '{self.model}'...")
            async with session.get(
                f"{self.ollama_url}/api/tags", timeout=5
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    # Check for exact match or match without tag (e.g. 'qwen2.5:0.5b' vs 'qwen2.5:0.5b-instruct')
                    # Ollama models usually have tags.
                    if self.model in models:
                        print(f"✅ Model '{self.model}' found.")
                        return True
                    # Check if 'latest' tag is implied
                    if f"{self.model}:latest" in models:
                        print(f"✅ Model '{self.model}:latest' found.")
                        return True

                    print(f"⚠️ Model '{self.model}' not found in Ollama list.")
                    print(f"   Available models: {', '.join(models)}")
                    print(
                        "   Attempting to use it anyway (Ollama might pull it or error)..."
                    )
                    return False
        except Exception as e:
            print(f"⚠️ Could not check available models: {e}")
        return True  # Assume it might work

    async def _get_ollama_response_async(self, prompt: str, session) -> Optional[str]:
        """Get response from Ollama (streaming) using /api/chat."""
        import aiohttp

        try:
            if self.debug:
                print(f"\nDEBUG: Sending request to {self.ollama_url}/api/chat")
                print(f"DEBUG: Model: {self.model}")

            # Increase timeout significantly as loading a model can take time
            timeout_seconds = 300

            # Use chat endpoint which is more robust for modern models
            messages = [
                {"role": "system", "content": ROBOT_PERSONA},
                {"role": "user", "content": prompt},
            ]

            async with session.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    # Some thinking-capable models can emit only `message.thinking`.
                    # Ask for direct answer text in `message.content`.
                    "think": False,
                    # keep_alive: keep the model resident so the *next* reply
                    # doesn't pay a cold reload — snappier back-to-back at a booth.
                    "keep_alive": "30m",
                    # num_predict caps reply length. Short = faster to generate
                    # and to speak. Paired with the "2-3 sentences" persona above.
                    "options": {"temperature": 0.8, "num_predict": 120},
                },
                timeout=aiohttp.ClientTimeout(total=timeout_seconds),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"\n⚠️ Ollama error ({response.status}): {error_text}")
                    return None

                if self.debug:
                    print(
                        f"DEBUG: Response received (Status {response.status}). Streaming content..."
                    )

                full_response = ""
                thinking_response = ""
                chunk_count = 0

                while True:
                    line = await response.content.readline()
                    if not line:
                        break
                    if line:
                        try:
                            decoded = line.decode("utf-8")
                            chunk = json.loads(decoded)
                            chunk_count += 1

                            if self.debug and chunk_count <= 3:
                                print(f"DEBUG Chunk {chunk_count}: {decoded.strip()}")

                            if chunk.get("error"):
                                print(f"\n⚠️ Ollama error: {chunk['error']}")
                                return None

                            content = ""
                            # Handle /api/chat response format
                            if "message" in chunk and "content" in chunk["message"]:
                                content = chunk["message"]["content"]
                                thinking_response += chunk["message"].get(
                                    "thinking", ""
                                )
                            # Fallback for /api/generate format (just in case)
                            elif "response" in chunk:
                                content = chunk["response"]

                            if content:
                                print(content, end="", flush=True)
                                full_response += content

                            if chunk.get("done"):
                                if self.debug:
                                    print(
                                        f"\nDEBUG: Generation complete. Total stats: {chunk.get('total_duration', 0)/1e9:.2f}s"
                                    )

                        except Exception as e:
                            if self.debug:
                                print(f"\nDEBUG: JSON parse error: {e}")
                            continue

                if not full_response and thinking_response:
                    # Fallback for servers/models that still stream into `thinking`.
                    print(thinking_response, end="", flush=True)
                    full_response = thinking_response
                    if self.debug:
                        print("\nDEBUG: Used thinking stream as fallback response.")

                print()
                if not full_response and self.debug:
                    print("DEBUG: Warning - Empty response received from Ollama")

                return full_response

        except asyncio.TimeoutError:
            print(f"\n⚠️ Ollama request timed out after {timeout_seconds}s")
            return None
        except Exception as e:
            print(f"\n⚠️ Ollama async error: {e}")
            if self.debug:
                import traceback

                traceback.print_exc()
            return None

    async def _show_thinking_animation(self, reachy, duration: float = 5.0):
        """Show robot 'thinking' animation."""
        import math
        import asyncio
        from reachy_mini.utils import create_head_pose as _chp

        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                angle = math.sin((time.time() - start_time) * 3) * 0.1
                pose = _chp(roll=angle)
                reachy.goto_target(head=pose, duration=0.3)
                await asyncio.sleep(0.1)

                if hasattr(reachy, "l_antenna") and hasattr(reachy, "r_antenna"):
                    reachy.l_antenna.goto_position(angle * 0.5, duration=0.2)
                    reachy.r_antenna.goto_position(-angle * 0.5, duration=0.2)

                await asyncio.sleep(0.2)
        finally:
            reachy.goto_target(head=_chp(), duration=0.5)

    async def start_chat_async(self):
        import asyncio
        import aiohttp
        from reachy_mini import ReachyMini
        from reachy_mini.utils import create_head_pose as _chp

        print("=" * 60)
        print("🤖 Reachy Mini Chat v8 with Piper-TTS (Offline)")
        print("=" * 60)
        print(f"Ollama Model: {self.model}")
        print(f"Ollama URL: {self.ollama_url}")
        print(f"Piper Model: {self.piper_model}")
        print("💡 Need more voices? Download .onnx models from:")
        print("   https://github.com/rhasspy/piper/releases/tag/v0.0.2")

        try:
            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")

                # Initialize controller with Piper
                self.controller = EmotionControllerV71(
                    reachy,
                    self.piper_model,
                    self.piper_config,
                    self.speaker_id,
                    self.debug,
                    gentle_mode=self.gentle,
                )

                reachy.goto_target(head=_chp(), duration=1.0)
                await asyncio.sleep(1.0)

                if self.use_asr:
                    if FasterWhisperASREngine is None:
                        print(
                            "❌ ASR requested but FasterWhisperASREngine not available."
                        )
                        return

                    print("Initializing ASR engine...")
                    try:
                        self.asr_engine = FasterWhisperASREngine(
                            model_name="small", device="cpu"
                        )
                    except Exception as e:
                        print(f"❌ Failed to initialize ASR engine: {e}")
                        return

                    print("\n🎤 VAD ASR + Async mode: press Ctrl-C to stop")

                    async with aiohttp.ClientSession() as session:
                        # Check model once
                        await self.check_ollama_model(session)

                        while True:
                            try:
                                print("\n🎙️ Speak now...")
                                start_time = time.time()
                                asr_lang = self.asr if self.asr != "auto" else None
                                transcription = self.asr_engine.transcribe_from_mic_vad(
                                    max_duration=4.0,
                                    silence_threshold=1.5,
                                    language=asr_lang,
                                )

                                if not transcription:
                                    continue

                                print(f"📝 You: {transcription}")
                                print("\n🤖 Reachy Mini: ", end="", flush=True)

                                llm_start = time.time()
                                thinking_task = asyncio.create_task(
                                    self._show_thinking_animation(reachy, 10.0)
                                )
                                llm_task = asyncio.create_task(
                                    self._get_ollama_response_async(
                                        transcription, session
                                    )
                                )

                                response = await llm_task
                                thinking_task.cancel()
                                with suppress(asyncio.CancelledError):
                                    await thinking_task

                                if response and self.controller:
                                    emotion, intensity, emotion_level = (
                                        self.controller.analyze_emotion(response)
                                    )
                                    await (
                                        self.controller.speak_with_expression_parallel(
                                            response, emotion, intensity, emotion_level
                                        )
                                    )

                            except KeyboardInterrupt:
                                # Match the text-chat path: force an immediate exit.
                                # A plain `break` can hang here because Ctrl-C often
                                # lands inside the blocking mic/VAD recording, leaving
                                # non-daemon ASR/audio threads that stall a clean shutdown.
                                print("\n👋 Interrupted by user, exiting chat.")
                                import os

                                os._exit(0)
                            except Exception as e:
                                print(f"⚠️ Error: {e}")
                                await asyncio.sleep(1.0)

                else:
                    print("\n💬 Start chatting (type 'quit' to exit)")
                    async with aiohttp.ClientSession() as session:
                        # Check model once
                        await self.check_ollama_model(session)

                        eof_count = 0
                        while True:
                            try:
                                user_input = input("\n🧑 You: ").strip()
                                if user_input.lower() in ["quit", "exit", "q"]:
                                    break
                                if not user_input:
                                    continue
                                eof_count = 0

                                print("\n🤖 Reachy Mini: ", end="", flush=True)

                                thinking_task = asyncio.create_task(
                                    self._show_thinking_animation(reachy, 10.0)
                                )
                                llm_task = asyncio.create_task(
                                    self._get_ollama_response_async(user_input, session)
                                )

                                response = await llm_task
                                thinking_task.cancel()
                                with suppress(asyncio.CancelledError):
                                    await thinking_task

                                if response and self.controller:
                                    emotion, intensity, emotion_level = (
                                        self.controller.analyze_emotion(response)
                                    )
                                    try:
                                        await self.controller.speak_with_expression_parallel(
                                            response, emotion, intensity, emotion_level
                                        )
                                    except asyncio.CancelledError:
                                        # User requested interrupt (Ctrl-C) during speech; stop gracefully
                                        print(
                                            "\n👋 Interrupted during speech, stopping."
                                        )
                                        # Attempt best-effort controller cleanup
                                        try:
                                            if hasattr(self.controller, "stop_all"):
                                                self.controller.stop_all()
                                        except Exception:
                                            pass
                                        # Force immediate exit to avoid hanging on non-daemon threads
                                        import os

                                        os._exit(0)

                            except EOFError:
                                eof_count += 1
                                if eof_count >= 3:
                                    print("\n👋 EOF received, exiting chat.")
                                    break
                                print("\n⚠️ Empty input (EOF). Type 'quit' to exit.")
                                continue
                            except KeyboardInterrupt:
                                print("\n👋 Interrupted by user, exiting chat.")
                                import os

                                os._exit(0)
                            except Exception as e:
                                print(f"\n⚠️ Error: {e}")

        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            self._tts_only_mode()

    def start_chat(self):
        import asyncio

        try:
            asyncio.run(self.start_chat_async())
        except KeyboardInterrupt:
            print("\n👋 Keyboard interrupt received, exiting.")
            import os

            os._exit(0)

    def _tts_only_mode(self):
        print("\n📻 Running in TTS-only mode (no robot)")
        print("💡 Need more voices? Download .onnx models from:")
        print("   https://github.com/rhasspy/piper/releases/tag/v0.0.2")
        tts = PiperTTSEngine(
            self.piper_model, self.piper_config, self.speaker_id, self.debug
        )
        tts.speak_with_emotion("Hello! Piper TTS is working.", "neutral")


def main():
    parser = argparse.ArgumentParser(description="Reachy Mini Chat v8 with Piper-TTS")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat")
    parser.add_argument(
        "--asr",
        nargs="?",
        const="auto",
        default=None,
        choices=["auto", "zh", "en"],
        help="Use microphone ASR input. Optional language: auto (default), zh, en",
    )
    parser.add_argument(
        "--model", default="qwen3.5:0.8b", help="Ollama model name (e.g., qwen3.5:0.8b)"
    )
    parser.add_argument("--url", default="http://127.0.0.1:11434", help="Ollama URL")
    parser.add_argument(
        "--piper-model", default=DEFAULT_PIPER_MODEL, help="Path to Piper .onnx model"
    )
    parser.add_argument(
        "--piper-config", default=None, help="Path to Piper .json config"
    )
    parser.add_argument(
        "--speaker", type=int, default=0, help="Speaker ID for multi-speaker models"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument(
        "--gentle", action="store_true", help="Enable gentle_mode for subtle emotions"
    )
    parser.add_argument(
        "--persona",
        default=None,
        help="Override Reachy's system-prompt personality (otherwise uses the TRY ME block)",
    )

    args = parser.parse_args()

    # CLI flag overrides the TRY ME default for coders who'd rather pass an arg.
    if args.persona:
        global ROBOT_PERSONA
        ROBOT_PERSONA = args.persona

    if not (args.chat or args.asr or USE_VOICE_CHAT):
        parser.print_help()
        return

    if not check_runtime_dependencies(require_reachy=True):
        return

    # The TRY ME toggle re-exposes the existing --asr code path as an easy switch.
    # When USE_VOICE_CHAT is on, use VOICE_CHAT_LANG; otherwise fall back to the
    # --asr CLI flag so it keeps working exactly as before.
    effective_asr = VOICE_CHAT_LANG if USE_VOICE_CHAT else args.asr
    if USE_VOICE_CHAT:
        print(
            f"🎤 Voice chat enabled (TRY ME: USE_VOICE_CHAT=True, lang={VOICE_CHAT_LANG})"
        )

    app = ChatAppWithPiper(
        model=args.model,
        ollama_url=args.url,
        piper_model=args.piper_model,
        piper_config=args.piper_config,
        speaker_id=args.speaker,
        debug=args.debug,
        use_asr=effective_asr,
        gentle=args.gentle,
    )

    app.start_chat()


if __name__ == "__main__":
    main()
