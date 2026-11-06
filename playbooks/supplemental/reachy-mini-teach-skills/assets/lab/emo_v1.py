# Copyright (C) 2026 Advanced Micro Devices, Inc. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

#!/usr/bin/env python3
"""
emo_v1.py - Reachy Mini Advanced Emotion Controller with Edge-TTS

    ┌───────────────────────────────────────────────────────────────┐
    │  LAB EDIT?  Jump to the "# >>> TRY ME <<<" block below          │
    │  (press Ctrl+F, search: TRY ME) to give Reachy a new persona    │
    │  or cloud voice. Save, then re-run.                             │
    └───────────────────────────────────────────────────────────────┘

A comprehensive emotion controller for Reachy Mini robot featuring:

1. Edge-TTS Integration: Microsoft Azure voices with emotional parameters
2. Advanced Emotion Analysis: Multi-language emotion detection with intensity levels
3. Combined Action Sequences: Synchronized head, antenna, eye, and body movements
4. Lip-Sync System: Dynamic antenna/eye movements during speech
5. Recorded Moves Library: Integration with Pollen Robotics dance moves
6. Ollama Chat Interface: Interactive conversation with emotional responses
7. Command-Line Testing: Multiple test modes for TTS, actions, and chat

Features sophisticated combined movements including:
- Nod with blink synchronization
- Shake with body yaw and eye movements
- Antenna wiggle with blinking
- Complex emotion sequences (excited, sad, curious, etc.)
- Individual component testing

Command-line usage:
- --chat: Interactive chat mode
- --test-tts: Test Edge-TTS functionality
- --test-actions: Test robot action sequences
- --debug: Enable detailed logging
"""

import re
import sys
import time
import json
import logging
import threading
import numpy as np
from typing import Dict, List, Tuple, Optional


# The Reachy SDK's media subsystem (SDK audio + camera) is intentionally unused
# in this lab: speech plays via sounddevice and the camera is read via ffmpeg.
# We construct the robot with media_backend="no_media", so any SDK call into the
# audio backend early-returns after logging a "Audio system is not initialized."
# warning (e.g. play_move() playing a move's bundled sound, or the SDK's
# wake_up/go_sleep chimes).
#
# A plain setLevel() on "reachy_mini.media" does NOT silence these: the real
# emitter is the child logger "reachy_mini.media.media_manager", and MediaManager
# resets its own level to INFO in __init__ (when the robot connects), overriding
# any level we set here. So we attach a Filter that drops this one message —
# filters survive the SDK's setLevel() and keep genuine errors visible.
def _drop_audio_not_initialized(record: logging.LogRecord) -> bool:
    return "Audio system is not initialized." not in record.getMessage()


logging.getLogger("reachy_mini.media.media_manager").addFilter(
    _drop_audio_not_initialized
)
logging.getLogger("reachy_mini.media").setLevel(logging.ERROR)


# Emoji / pictograph ranges. Small chat LLMs love to add emojis, but TTS engines
# (Edge-TTS, Piper) try to *pronounce* them ("smiling face..."), which sounds
# broken. We strip them from text right before speaking, so speech stays clean
# while the on-screen text can keep them.
_EMOJI_RE = re.compile(
    "["
    "\U00002190-\U000021ff"  # arrows
    "\U00002300-\U000023ff"  # misc technical (⌚ ⏰ ⏳)
    "\U00002600-\U000027bf"  # misc symbols + dingbats (☀ ✅ ❤ ✨)
    "\U00002b00-\U00002bff"  # misc symbols and arrows
    "\U0000fe00-\U0000fe0f"  # variation selectors
    "\U0000200d"  # zero-width joiner (emoji sequences)
    "\U000020e3"  # combining keycap
    "\U0001f000-\U0001faff"  # emoticons, pictographs, transport, flags, etc.
    "]+",
    flags=re.UNICODE,
)


# Small chat LLMs love Markdown emphasis: *waves*, **hello**, _psst_, `code`,
# ~strike~. TTS engines read those symbols literally ("asterisk waves asterisk"),
# so we strip the formatting markers while KEEPING the words between them. We only
# target the Markdown chars, never apostrophes/hyphens inside real words.
_MARKDOWN_MARKS_RE = re.compile(r"[*_`~]+")


def strip_emojis(text: str) -> str:
    """Clean text for TTS: drop emojis/pictographs and Markdown emphasis markers
    (``*``, ``_``, `` ` ``, ``~``) so the voice doesn't pronounce them, while
    keeping the actual words. Named for backwards compatibility (imported by
    emo_v2)."""
    if not text:
        return text
    cleaned = _EMOJI_RE.sub("", text)
    cleaned = _MARKDOWN_MARKS_RE.sub("", cleaned)
    # Collapse whitespace the removed symbols may have left behind.
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def _create_head_pose(*args, **kwargs):
    from reachy_mini.utils import create_head_pose as _chp

    return _chp(*args, **kwargs)


def check_runtime_dependencies(require_reachy: bool = False) -> bool:
    """Check that optional runtime deps are importable."""
    missing = []
    try:
        import requests  # noqa: F401
    except Exception:
        missing.append("requests")
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


# ============================================================================
# >>> TRY ME <<<  Mini-lab Task 1
# Give Reachy a new personality and a new cloud voice, then re-run
# `python lab/emo_v1.py --chat`. The voice is generated by Microsoft Edge-TTS
# (a cloud service) — keep this in mind for Task 2, where it goes offline.
# ============================================================================

# 1) Reachy's personality (sent to the LLM as a system prompt).
#    The "one or two short sentences" instruction keeps replies snappy — great
#    for a busy booth, and faster to speak. Lengthen it if you want more chat.
ROBOT_PERSONA = (
    "You are a cute desktop robot assistant. Respond with enthusiasm and warmth, "
    "in two or three short sentences. Keep it brief and conversational."
)

# 2) Reachy's cloud voice. A few fun ones to try:
#    en-US-AnaNeural   (child)      en-GB-RyanNeural  (British)
#    en-US-GuyNeural   (deep)       en-AU-NatashaNeural (Australian)
#    Discover more with: python utils/test_edge_tts_voices.py
DEFAULT_VOICE = "en-US-JennyNeural"
# ============================================================================


# Emotion mapping and presets (copied from ReachyClaw for richer expressions)
_EMOTION_CATEGORY_MAP: Dict[str, str] = {
    # positive
    "amazed1": "positive",
    "cheerful1": "positive",
    "dance1": "positive",
    "dance2": "positive",
    "dance3": "positive",
    "enthusiastic1": "positive",
    "enthusiastic2": "positive",
    "grateful1": "positive",
    "helpful1": "positive",
    "helpful2": "positive",
    "laughing1": "positive",
    "laughing2": "positive",
    "loving1": "positive",
    "proud1": "positive",
    "proud2": "positive",
    "proud3": "positive",
    "relief1": "positive",
    "relief2": "positive",
    "success1": "positive",
    "success2": "positive",
    "welcoming1": "positive",
    "welcoming2": "positive",
    "yes1": "positive",
    "understanding2": "positive",
    "electric1": "positive",
    # negative
    "anxiety1": "negative",
    "boredom1": "negative",
    "boredom2": "negative",
    "contempt1": "negative",
    "displeased1": "negative",
    "displeased2": "negative",
    "downcast1": "negative",
    "disgusted1": "negative",
    "dying1": "negative",
    "exhausted1": "negative",
    "fear1": "negative",
    "frustrated1": "negative",
    "furious1": "negative",
    "go_away1": "negative",
    "impatient1": "negative",
    "impatient2": "negative",
    "irritated1": "negative",
    "irritated2": "negative",
    "lonely1": "negative",
    "no1": "negative",
    "no_sad1": "negative",
    "rage1": "negative",
    "sad1": "negative",
    "sad2": "negative",
    "scared1": "negative",
    "tired1": "negative",
    "reprimand1": "negative",
    "reprimand2": "negative",
    "reprimand3": "negative",
    "calming1": "negative",
    "yes_sad1": "negative",
    "resigned1": "negative",
    # question
    "confused1": "question",
    "curious1": "question",
    "incomprehensible2": "question",
    "inquiring1": "question",
    "inquiring2": "question",
    "inquiring3": "question",
    "lost1": "question",
    "thoughtful1": "question",
    "thoughtful2": "question",
    "uncertain1": "question",
    "uncomfortable1": "question",
    # activity
    "no_excited1": "activity",
    "serenity1": "activity",
    # neutral
    "attentive1": "neutral",
    "attentive2": "neutral",
    "come1": "neutral",
    "indifferent1": "neutral",
    "understanding1": "neutral",
    "oops1": "neutral",
    "oops2": "neutral",
    "shy1": "neutral",
    "sleep1": "neutral",
    "proud1": "neutral",
    "surprised1": "neutral",
    "surprised2": "neutral",
}

_GENTLE_EMOTIONS = {
    "attentive1",
    "attentive2",
    "understanding1",
    "understanding2",
    "shy1",
    "come1",
    "indifferent1",
    "grateful1",
    "helpful1",
    "helpful2",
    "relief1",
    "relief2",
    "yes1",
    "welcoming1",
    "thoughtful1",
    "thoughtful2",
    "curious1",
    "inquiring1",
    "serenity1",
    "calming1",
}

_BIG_EMOTIONS = {
    "dance1",
    "dance2",
    "dance3",
    "enthusiastic1",
    "enthusiastic2",
    "laughing1",
    "laughing2",
    "proud1",
    "proud2",
    "proud3",
    "amazed1",
    "electric1",
    "furious1",
    "rage1",
}

_CARTOON_EMOTIONS = {
    "enthusiastic1",
    "enthusiastic2",
    "dance1",
    "dance2",
    "dance3",
    "cheerful1",
    "laughing1",
    "laughing2",
    "electric1",
    "success1",
    "success2",
    "proud3",
    "no_excited1",
    "amazed1",
    "surprised1",
    "surprised2",
    "scared1",
    "furious1",
    "rage1",
}

_WELCOME_EMOTIONS = ["welcoming1", "welcoming2", "enthusiastic2", "cheerful1"]
_FAREWELL_EMOTIONS = ["grateful1", "loving1", "welcoming2"]


class EdgeTTSEngine:
    """Edge-TTS engine with emotional voice selection"""

    def __init__(
        self, default_voice: str = "en-US-JennyNeural", sample_rate: int = 22050
    ):
        self.default_voice = default_voice
        self.sample_rate = sample_rate
        self.debug = True  # Force debug on for clarity
        print(f"🎙️ EdgeTTSEngine initialized")
        print(f"   - Using voice: {default_voice}")
        print(f"   - Sample rate: {sample_rate}Hz")

        # Cute cartoon voices that work!
        # self.emotion_voices = {
        #    'positive': "en-US-AnaNeural",      # CARTOON - Cute, adorable ✨
        #    'negative': "zh-CN-XiaoyiNeural",   # CARTOON - Lively, cute Chinese
        #    'question': "en-US-AnaNeural",      # CARTOON - Cute, adorable
        #    'activity': "zh-CN-XiaoyiNeural",   # CARTOON - Lively, cute Chinese
        #    'neutral': "en-US-AnaNeural",       # CARTOON - Cute, adorable
        # }

        # Emotion → voice map. WHY all entries point at the single chosen voice:
        # a booth attendee sets exactly one voice (the Task 1 `VOICE_1` knob /
        # `--voice` flag), so the speaker identity must stay fixed and NOT silently
        # switch per detected emotion. Emotional expressiveness is applied via
        # `self.voice_params` below (rate/pitch/style), so prosody still varies —
        # only the voice NAME is held constant here.
        self.emotion_voices = {
            "positive": default_voice,
            "negative": default_voice,
            "question": default_voice,
            "activity": default_voice,
            "neutral": default_voice,
        }

        # Cute voice parameters with higher pitch for childlike sound
        self.voice_params = {
            "positive": {"rate": "+5%", "pitch": "+4Hz", "style": "general"},
            "negative": {"rate": "+0%", "pitch": "+2Hz", "style": "general"},
            "question": {"rate": "+8%", "pitch": "+6Hz", "style": "general"},
            "activity": {"rate": "+12%", "pitch": "+8Hz", "style": "general"},
            "neutral": {"rate": "+3%", "pitch": "+3Hz", "style": "general"},
        }

    def _has_chinese(self, text: str) -> bool:
        """Detect presence of CJK Unified Ideographs (basic Chinese range)."""
        if not text:
            return False
        for ch in text:
            if "\u4e00" <= ch <= "\u9fff":
                return True
        return False

    async def _speak_async(
        self,
        text: str,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        style: str = "general",
    ) -> Tuple:
        """Synthesize speech to a temporary WAV file with voice parameters, read it and return (audio, samplerate).

        This avoids guessing the raw stream format and preserves the correct sample rate
        so playback via sounddevice does not introduce noise.
        """
        try:
            import tempfile
            import os
            import numpy as np
            import edge_tts
            import soundfile as sf

            # Save to a temporary WAV file using edge-tts's save helper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            # Prefer default voice for Chinese text to avoid mismatched voice failures
            prefer_default = self._has_chinese(text)
            if prefer_default:
                voice = self.default_voice

            # Create communicate with voice parameters
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            if style != "general":
                # Add style parameter if supported
                try:
                    communicate = edge_tts.Communicate(
                        text, voice, rate=rate, pitch=pitch, style=style
                    )
                except:
                    # Fallback if style not supported
                    communicate = edge_tts.Communicate(
                        text, voice, rate=rate, pitch=pitch
                    )

            # Attempt to save; on failure, retry with default voice unless text is Chinese
            try:
                try:
                    await communicate.save(tmp_path)
                except Exception as save_exc:
                    if self.debug and not prefer_default:
                        print(f"⚠️ Edge-TTS save error: {save_exc}")
                    if voice != self.default_voice and not prefer_default:
                        if self.debug and not prefer_default:
                            print("⚠️ Retrying synthesis with default voice...")
                        time.sleep(0.5)
                        try:
                            communicate = edge_tts.Communicate(
                                text, self.default_voice, rate=rate, pitch=pitch
                            )
                            await communicate.save(tmp_path)
                        except Exception as save_exc2:
                            if self.debug and not prefer_default:
                                print(f"⚠️ Retry with default voice failed: {save_exc2}")
                            raise save_exc2
                    else:
                        raise save_exc
            except Exception:
                # Ensure temp file cleaned
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass
                raise

            # If file is empty, retry with default voice (but suppress warnings for Chinese text)
            try:
                if os.path.getsize(tmp_path) == 0:
                    if voice != self.default_voice and not prefer_default:
                        if self.debug:
                            print(
                                "⚠️ Edge-TTS produced empty file; retrying with default voice..."
                            )
                        try:
                            communicate = edge_tts.Communicate(text, self.default_voice)
                            await communicate.save(tmp_path)
                        except Exception as e2:
                            if self.debug:
                                print(f"⚠️ Retry with default voice failed: {e2}")
            except OSError:
                # File might not exist yet; continue to read and let sf raise
                pass

            # Read the WAV file using soundfile to get correct dtype and samplerate
            data, sr = sf.read(tmp_path, dtype="float32")

            # Ensure mono or stereo shape is acceptable for sounddevice
            if data.ndim == 1:
                audio = data
            else:
                # sounddevice handles stereo arrays; keep as-is
                audio = data

            # Clean up temporary file
            try:
                os.remove(tmp_path)
            except Exception:
                pass

            return audio, sr

        except Exception as e:
            if self.debug:
                print(f"Edge-TTS synthesis error: {e}")
            return np.array([], dtype=np.float32), 0

    @staticmethod
    def _run_coro_blocking(coro_factory):
        """Run an async coroutine to completion and return its result, regardless
        of whether an event loop is already running on the current thread.

        WHY: this sync method is called both from plain scripts (no running loop)
        and from a Jupyter notebook (a loop is ALREADY running on the main thread).
        `asyncio.run()` raises "cannot be called from a running event loop" in the
        notebook case, and because the coroutine object would have been created and
        passed as an argument, Python also emits a "coroutine was never awaited"
        RuntimeWarning. To avoid both, we take a zero-arg `coro_factory` so the
        coroutine is only instantiated on the thread that will actually await it.
        """
        import asyncio

        try:
            asyncio.get_running_loop()
            loop_running = True
        except RuntimeError:
            loop_running = False

        if not loop_running:
            # No loop on this thread (scripts): the coroutine is created here, inside
            # asyncio.run, so it is always awaited. Preserves original behavior.
            return asyncio.run(coro_factory())

        # A loop is already running (notebook): we cannot use asyncio.run on this
        # thread, and we must keep blocking semantics for our sync callers. Run the
        # coroutine to completion on a SEPARATE thread with its own fresh event loop.
        # Creating the coroutine inside the worker guarantees it is always awaited,
        # so no un-awaited-coroutine RuntimeWarning can occur even on error paths.
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(coro_factory())).result()

    def speak_with_emotion(self, text: str, emotion: str = "neutral"):
        """Speak text with emotional voice and parameters"""
        text = strip_emojis(text)
        if not text.strip():
            return

        voice = self.emotion_voices.get(emotion, self.default_voice)
        params = self.voice_params.get(emotion, self.voice_params["neutral"])

        try:
            audio_data, sr = self._run_coro_blocking(
                lambda: self._speak_async(
                    text,
                    voice,
                    rate=params["rate"],
                    pitch=params["pitch"],
                    style=params["style"],
                )
            )

            if sr and audio_data.size:
                import sounddevice as sd

                sd.play(audio_data, samplerate=sr)
                sd.wait()
            else:
                if self.debug:
                    print("⚠️ No audio produced by Edge-TTS")
                raise RuntimeError("No audio produced")
        except Exception as e:
            print(f"⚠️ Edge-TTS error: {e}")
            self._fallback_tts(text, emotion)

    async def speak_with_emotion_async(self, text: str, emotion: str = "neutral"):
        """Async version of speak_with_emotion (works within existing event loop)"""
        text = strip_emojis(text)
        if not text.strip():
            return

        import asyncio

        voice = self.emotion_voices.get(emotion, self.default_voice)
        params = self.voice_params.get(emotion, self.voice_params["neutral"])

        try:
            audio_data, sr = await self._speak_async(
                text,
                voice,
                rate=params["rate"],
                pitch=params["pitch"],
                style=params["style"],
            )

            if sr and audio_data.size:
                import sounddevice as sd

                # Play with the correct samplerate returned by the file
                # Use asyncio.to_thread to run blocking sounddevice.play/wait in thread
                await asyncio.to_thread(
                    lambda: (sd.play(audio_data, samplerate=sr), sd.wait())
                )
            else:
                if self.debug:
                    print("⚠️ No audio produced by Edge-TTS (async)")
                raise RuntimeError("No audio produced")
        except Exception as e:
            print(f"⚠️ Edge-TTS async error: {e}")
            # Fallback to sync version for compatibility
            self._fallback_tts(text, emotion)

    def _fallback_tts(self, text: str, emotion: str):
        """Fallback if Edge-TTS fails"""
        import subprocess
        import platform

        system = platform.system()

        if system == "Darwin":
            try:
                subprocess.run(["say", text], check=True)
                print("✅ Using macOS 'say' as fallback")
            except:
                pass
        elif system == "Windows":
            try:
                import pyttsx3

                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                print("✅ Using pyttsx3 as fallback")
            except:
                pass


class LipSyncControllerV5:
    """Lip-sync using your antenna/eye control approach"""

    def __init__(self, reachy, debug: bool = False):
        self.reachy = reachy
        self.is_speaking = False
        self.sync_thread = None
        self.debug = debug
        if debug:
            print("✅ LipSyncControllerV5 initialized (handles antenna/eye movements)")

    def start_lip_sync(self, text: str, emotion_level: float = 0.5):
        """Start lip-sync with your approach"""
        self.is_speaking = True

        def lip_sync_animation():
            while self.is_speaking:
                try:
                    # Check if robot head exists
                    if hasattr(self.reachy, "head"):
                        self.reachy.head.r_antenna.goal_position = emotion_level * 0.8
                        self.reachy.head.l_antenna.goal_position = emotion_level * 0.8
                        self.reachy.head.r_eye.goal_position = 1 - (emotion_level * 0.3)
                        self.reachy.head.l_eye.goal_position = 1 - (emotion_level * 0.3)
                except Exception as e:
                    print(f"⚠️ Lip-sync error (robot may not support): {e}")
                    break
                time.sleep(0.1)

            # Return to neutral (with error handling)
            try:
                if hasattr(self.reachy, "head"):
                    self.reachy.head.r_antenna.goal_position = 0
                    self.reachy.head.l_antenna.goal_position = 0
                    self.reachy.head.r_eye.goal_position = 0.5
                    self.reachy.head.l_eye.goal_position = 0.5
            except:
                pass

        self.sync_thread = threading.Thread(target=lip_sync_animation, daemon=True)
        self.sync_thread.start()

    def stop_lip_sync(self):
        """Stop lip-sync"""
        self.is_speaking = False
        if self.sync_thread:
            self.sync_thread.join(timeout=0.5)


class EmotionControllerV6:
    """Emotion controller with enhanced continuous actions and combined movements"""

    def __init__(
        self,
        reachy,
        debug: bool = False,
        gentle_mode: bool = True,
        voice: str = "zh-CN-XiaoxiaoNeural",
    ):
        from reachy_mini.motion.recorded_move import RecordedMoves

        self.reachy = reachy
        self.debug = debug
        self.gentle_mode = gentle_mode
        self.is_speaking_action = False
        # TTS and lip-sync
        self.tts_engine = EdgeTTSEngine(default_voice=voice)
        self.lip_sync = LipSyncControllerV5(reachy, debug=self.debug)

        # Load both libraries for richer motions
        self.emotions_lib = RecordedMoves(
            "pollen-robotics/reachy-mini-emotions-library"
        )
        self.dances_lib = RecordedMoves("pollen-robotics/reachy-mini-dances-library")

        self._categorize_recorded_moves()

        self.simple_actions = {
            "nod": self._simple_nod,
            "shake": self._simple_shake,
            "look_curious": self._simple_look_curious,
            "look_sad": self._simple_look_sad,
            "excited_wiggle": self._simple_excited_wiggle,
            "thoughtful_tilt": self._simple_thoughtful_tilt,
        }

    def _categorize_recorded_moves(self):
        """Build emotion_to_moves from both emotions and dances libraries."""
        self.emotion_to_moves = {
            "positive": [],
            "negative": [],
            "question": [],
            "activity": [],
            "neutral": [],
        }

        # 1. Emotions library — use hardcoded map, fall back to keyword scan
        for move_name in self.emotions_lib.list_moves():
            category = _EMOTION_CATEGORY_MAP.get(move_name)
            if category is None:
                category = self._keyword_category(move_name, self.emotions_lib)
            self.emotion_to_moves[category].append(("emotions", move_name))
            if self.debug:
                print(f"🎭 emotions/{move_name} → {category}")

        # 2. Dances library — keyword scan
        for move_name in self.dances_lib.list_moves():
            category = self._keyword_category(move_name, self.dances_lib)
            self.emotion_to_moves[category].append(("dances", move_name))
            if self.debug:
                print(f"🕺 dances/{move_name} → {category}")

    def _keyword_category(self, move_name: str, lib) -> str:
        """Fallback keyword-based categorisation using move description."""
        try:
            move = lib.get(move_name)
            desc = (move.description or "").lower()
        except Exception:
            desc = move_name.lower()

        scores = {
            "positive": sum(
                1
                for w in [
                    "happy",
                    "joy",
                    "love",
                    "excited",
                    "great",
                    "awesome",
                    "good",
                    "thanks",
                    "celebrate",
                    "dance",
                    "cheer",
                    "proud",
                ]
                if w in desc
            ),
            "negative": sum(
                1
                for w in [
                    "sad",
                    "angry",
                    "sorry",
                    "disappoint",
                    "bad",
                    "wrong",
                    "hate",
                    "fear",
                    "bored",
                    "frustrat",
                    "rage",
                    "tired",
                ]
                if w in desc
            ),
            "question": sum(
                1
                for w in [
                    "what",
                    "why",
                    "how",
                    "when",
                    "curious",
                    "wonder",
                    "think",
                    "question",
                    "unsure",
                    "confused",
                ]
                if w in desc
            ),
            "activity": sum(
                1
                for w in [
                    "dance",
                    "move",
                    "action",
                    "play",
                    "energy",
                    "wiggle",
                ]
                if w in desc
            ),
        }
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "neutral"

    def analyze_emotion(self, text: str) -> Tuple[str, str, float]:
        """Analyze emotion with your level calculation"""
        text_lower = text.lower()
        emotion_level = min(len(text) / 200, 1.0)

        positive_words = [
            "开心",
            "快乐",
            "高兴",
            "喜欢",
            "爱",
            "谢谢",
            "感谢",
            "好",
            "棒",
            "完美",
            "excited",
            "happy",
            "joy",
            "love",
            "thanks",
            "good",
            "great",
            "awesome",
        ]
        negative_words = [
            "伤心",
            "难过",
            "悲伤",
            "生气",
            "失望",
            "抱歉",
            "对不起",
            "不好",
            "坏",
            "sad",
            "angry",
            "sorry",
            "disappointed",
            "bad",
            "wrong",
            "hate",
        ]
        question_words = [
            "吗",
            "？",
            "?",
            "为什么",
            "怎么",
            "如何",
            "what",
            "why",
            "how",
            "when",
        ]
        activity_words = [
            "跳舞",
            "舞蹈",
            "运动",
            "活动",
            "动起来",
            "dance",
            "move",
            "action",
            "play",
        ]

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        ques_count = sum(1 for word in question_words if word in text_lower)
        act_count = sum(1 for word in activity_words if word in text_lower)

        emoji_pos = ["😊", "😄", "😍", "👍", "🥰", "😎", "🎉", "❤️", "😂", "🤗"]
        emoji_neg = ["😢", "😭", "😡", "👎", "😔", "😞", "😤", "💔"]
        emoji_ques = ["🤔", "❓", "⁉️", "💭", "🧐", "🔍"]
        emoji_act = ["💃", "🕺", "🎵", "🎶", "⚽", "🏀", "🎮"]

        pos_count += sum(1 for emoji in emoji_pos if emoji in text)
        neg_count += sum(1 for emoji in emoji_neg if emoji in text)
        ques_count += sum(1 for emoji in emoji_ques if emoji in text)
        act_count += sum(1 for emoji in emoji_act if emoji in text)

        scores = {
            "positive": pos_count,
            "negative": neg_count,
            "question": ques_count,
            "activity": act_count,
        }

        emotion_type = max(scores, key=scores.get)
        total_score = sum(scores.values())

        if total_score >= 3:
            intensity = "high"
        elif total_score >= 1:
            intensity = "medium"
        else:
            intensity = "low"

        if emotion_type == "positive":
            emotion_level *= 1.2
        elif emotion_type == "negative":
            emotion_level *= 0.8

        return emotion_type, intensity, emotion_level

    def _get_move(self, lib_tag: str, move_name: str):
        """Return a Move object from the correct library."""
        lib = self.emotions_lib if lib_tag == "emotions" else self.dances_lib
        return lib.get(move_name)

    def execute_recorded_move(self, move, initial_goto_duration: float = 1.0):
        """Execute a recorded move. `move` can be (lib_tag, move_name) or a move_name string."""
        if isinstance(move, tuple) and len(move) == 2:
            lib_tag, move_name = move
            if self.debug:
                print(f"🎬 Playing {lib_tag}/{move_name}")
            mv = self._get_move(lib_tag, move_name)
        else:
            move_name = move
            if self.debug:
                print(f"🎬 Playing recorded move: {move_name}")
            # Try dances library first, fall back to emotions
            try:
                mv = self.dances_lib.get(move_name)
            except Exception:
                mv = self.emotions_lib.get(move_name)
        # sound=False: recorded moves can bundle an audio track that the SDK
        # would play via its media server. We run with media_backend="no_media"
        # (speech goes through sounddevice instead), so that path just logs
        # repeated "Audio system is not initialized." warnings and plays nothing.
        # Skip it entirely to keep the booth terminal clean.
        self.reachy.play_move(
            mv, initial_goto_duration=initial_goto_duration, sound=False
        )

    def _filter_gentle_emotions(self, available_moves):
        """Filter to only gentle emotions if gentle_mode is enabled."""
        if not getattr(self, "gentle_mode", False):
            return available_moves

        gentle_moves = [
            (lib, name) for lib, name in available_moves if name in _GENTLE_EMOTIONS
        ]
        if not gentle_moves:
            return available_moves
        return gentle_moves

    def execute_emotion_move(self, emotion_type: str, intensity: str = "medium"):
        """Execute a recorded move based on emotion category."""
        available = self.emotion_to_moves.get(emotion_type, [])
        if not available:
            available = self.emotion_to_moves["neutral"]

        # Filter to gentle emotions if in gentle mode
        available = self._filter_gentle_emotions(available)

        import random

        if intensity == "high" and len(available) > 1:
            lib_tag, move_name = available[-1]
        elif intensity == "low" and len(available) > 1:
            lib_tag, move_name = available[0]
        else:
            lib_tag, move_name = random.choice(available)

        duration_map = {"high": 0.8, "medium": 1.0, "low": 1.2}
        if getattr(self, "gentle_mode", False):
            duration_map = {"high": 1.0, "medium": 1.3, "low": 1.5}
        self.execute_recorded_move(
            (lib_tag, move_name), duration_map.get(intensity, 1.0)
        )

    def _continuous_emotion_action(self, emotion_type: str, intensity: str):
        """Execute continuous emotion actions during speaking."""
        available = self.emotion_to_moves.get(emotion_type, [])

        # Filter to gentle emotions if in gentle mode
        available = self._filter_gentle_emotions(available)

        if available:
            import random

            while self.is_speaking_action:
                lib_tag, move_name = random.choice(available)
                duration_map = {"high": 0.8, "medium": 1.0, "low": 1.2}
                if getattr(self, "gentle_mode", False):
                    duration_map = {"high": 1.0, "medium": 1.3, "low": 1.5}
                try:
                    self.execute_recorded_move(
                        (lib_tag, move_name), duration_map.get(intensity, 1.0)
                    )
                except Exception as e:
                    if self.debug:
                        print(f"⚠️ Move error ({lib_tag}/{move_name}): {e}")
                    time.sleep(0.5)
        else:
            self._continuous_simple_action(emotion_type, intensity)

    def _execute_simple_action(self, emotion_type: str, intensity: str):
        duration_map = {"high": 1.5, "medium": 2.0, "low": 2.5}
        duration = duration_map.get(intensity, 2.0)

        if emotion_type == "positive":
            self.simple_actions["nod"](duration)
        elif emotion_type == "negative":
            self.simple_actions["look_sad"](duration)
        elif emotion_type == "question":
            self.simple_actions["look_curious"](duration)
        elif emotion_type == "activity":
            self.simple_actions["excited_wiggle"](duration)
        else:
            self.simple_actions["nod"](duration)

    def _continuous_simple_action(self, emotion_type: str, intensity: str):
        """Execute continuous simple actions during speaking with variety and combined movements"""
        pause_map = {"high": 1.0, "medium": 1.5, "low": 2.0}
        pause = pause_map.get(intensity, 1.5)

        # Enhanced action sequences with combined head/antennas + blink + body yaw
        combined_action_sequences = {
            "positive": [
                self._combined_nod_blink,
                self._combined_shake_blink_yaw,
                self._combined_wiggle_blink,
                self._combined_happy_tilt_blink_yaw,
                self._combined_excited_sequence,
            ],
            "negative": [
                self._combined_sad_blink,
                self._combined_thoughtful_blink_yaw,
                self._combined_slow_sequence,
                self._combined_negative_gesture,
            ],
            "question": [
                self._combined_curious_blink,
                self._combined_thoughtful_blink_yaw,
                self._combined_question_sequence,
                self._combined_nod_blink,
            ],
            "activity": [
                self._combined_wiggle_blink,
                self._combined_shake_blink_yaw,
                self._combined_activity_sequence,
                self._combined_happy_tilt_blink_yaw,
            ],
            "neutral": [
                self._combined_nod_blink,
                self._combined_thoughtful_blink_yaw,
                self._combined_neutral_sequence,
                self._combined_curious_blink,
            ],
        }

        actions = combined_action_sequences.get(
            emotion_type, [self._combined_nod_blink]
        )
        action_index = 0

        while self.is_speaking_action:
            actions[action_index % len(actions)]()
            action_index += 1
            time.sleep(pause)

    def speak_with_expression(
        self,
        text: str,
        emotion: str = "neutral",
        intensity: str = "medium",
        emotion_level: float = 0.5,
    ):
        """Speak with Edge-TTS and your lip-sync"""
        if not text.strip():
            return

        if self.debug:
            print(f"🗣️ Speaking with {emotion} emotion (level: {emotion_level:.2f})")

        word_count = len(text.split())
        estimated_duration = max(1.0, word_count / 2.5)

        self.lip_sync.start_lip_sync(text, emotion_level)

        self.is_speaking_action = True
        action_thread = threading.Thread(
            target=self._continuous_emotion_action,
            args=(emotion, intensity),
            daemon=True,
        )
        action_thread.start()

        self.tts_engine.speak_with_emotion(text, emotion)

        self.is_speaking_action = False
        self.lip_sync.stop_lip_sync()

    async def speak_with_expression_async(
        self,
        text: str,
        emotion: str = "neutral",
        intensity: str = "medium",
        emotion_level: float = 0.5,
    ):
        """Async version: Speak with Edge-TTS and your lip-sync"""
        if not text.strip():
            return

        if self.debug:
            print(
                f"🗣️ Async speaking with {emotion} emotion (level: {emotion_level:.2f})"
            )

        self.lip_sync.start_lip_sync(text, emotion_level)

        self.is_speaking_action = True
        action_thread = threading.Thread(
            target=self._continuous_emotion_action,
            args=(emotion, intensity),
            daemon=True,
        )
        action_thread.start()

        # Use async TTS without creating new event loop
        await self.tts_engine.speak_with_emotion_async(text, emotion)

        self.is_speaking_action = False
        self.lip_sync.stop_lip_sync()

    async def speak_with_expression_parallel(
        self,
        text: str,
        emotion: str = "neutral",
        intensity: str = "medium",
        emotion_level: float = 0.5,
    ):
        """Parallel version: start motion + lip-sync first, then run TTS so speech
        and motion OVERLAP for the whole utterance.

        The continuous emotion-action thread and lip-sync start a beat before the
        audio (during synthesis) and are stopped as soon as playback ends. We do
        NOT play an extra recorded move before or after the audio: the pre-move
        delayed playback (and double-drove the robot alongside the action thread),
        and the post-move kept the robot moving after the speech had already
        finished — that trailing motion is the "actions lag the audio" bug.
        """
        if not text.strip():
            return

        if self.debug:
            print(
                f"🤖 PARALLEL: overlapping motion + speech for {emotion} (level: {emotion_level:.2f})"
            )

        # Start lip-sync and the continuous emotion motion immediately, so the
        # robot is already animating as (or just before) the audio begins.
        self.lip_sync.start_lip_sync(text, emotion_level)
        self.is_speaking_action = True
        action_thread = threading.Thread(
            target=self._continuous_emotion_action,
            args=(emotion, intensity),
            daemon=True,
        )
        action_thread.start()

        # Run TTS concurrently with the motion thread above: playback starts right
        # after synthesis while the robot keeps moving in parallel.
        try:
            await self.tts_engine.speak_with_emotion_async(text, emotion)
        except Exception as e:
            print(f"⚠️ TTS async error in parallel mode: {e}")

        # Audio done: stop the motion so it settles with the speech instead of
        # trailing it. Any recorded move already in flight only finishes its
        # current (single, short) cycle before the action thread exits.
        self.is_speaking_action = False
        self.lip_sync.stop_lip_sync()

    def _simple_nod(self, duration: float = 2.0):
        amplitude = 0.6
        cycles = int(duration * 2)

        for _ in range(cycles):
            self.reachy.goto_target(
                head=_create_head_pose(pitch=20 * amplitude, degrees=True),
                duration=0.25,
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=_create_head_pose(pitch=-10 * amplitude, degrees=True),
                duration=0.25,
            )
            time.sleep(0.1)

        self.reachy.goto_target(head=_create_head_pose(), duration=0.5)

    def _simple_nod_once(self):
        """Single nod cycle"""
        try:
            amplitude = 0.6
            self.reachy.goto_target(
                head=_create_head_pose(pitch=20 * amplitude, degrees=True),
                duration=0.25,
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=_create_head_pose(pitch=-10 * amplitude, degrees=True),
                duration=0.25,
            )
            time.sleep(0.1)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Nod action not supported: {e}")

    def _simple_look_sad_once(self):
        """Single sad look"""
        try:
            self.reachy.goto_target(
                head=_create_head_pose(pitch=30, degrees=True), duration=0.5
            )
            time.sleep(0.5)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Sad look action not supported: {e}")

    def _simple_look_curious_once(self):
        """Single curious look"""
        try:
            amplitude = 0.8
            self.reachy.goto_target(
                head=_create_head_pose(
                    yaw=25 * amplitude, pitch=10 * amplitude, degrees=True
                ),
                duration=0.5,
            )
            time.sleep(0.5)
            self.reachy.goto_target(
                head=_create_head_pose(
                    yaw=-25 * amplitude, pitch=10 * amplitude, degrees=True
                ),
                duration=0.5,
            )
            time.sleep(0.5)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Curious look action not supported: {e}")

    def _simple_excited_wiggle_once(self):
        """Single excited wiggle"""
        try:
            left_val = 0.7
            right_val = -0.7
            self.reachy.goto_target(antennas=[left_val, right_val], duration=0.15)
            time.sleep(0.1)
            left_val = -0.7
            right_val = 0.7
            self.reachy.goto_target(antennas=[left_val, right_val], duration=0.15)
            time.sleep(0.1)
            self.reachy.goto_target(antennas=[0, 0], duration=0.3)
        except Exception as e:
            print(f"⚠️ Excited wiggle action not supported: {e}")

    def _simple_shake_once(self):
        """Single shake cycle"""
        try:
            amplitude = 0.7
            self.reachy.goto_target(
                head=_create_head_pose(yaw=30 * amplitude, degrees=True), duration=0.3
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=_create_head_pose(yaw=-30 * amplitude, degrees=True), duration=0.3
            )
            time.sleep(0.1)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Shake action not supported: {e}")

    def _simple_thoughtful_tilt_once(self):
        """Single thoughtful tilt"""
        try:
            amplitude = 0.6
            self.reachy.goto_target(
                head=_create_head_pose(roll=15 * amplitude, degrees=True), duration=0.4
            )
            time.sleep(0.4)
            self.reachy.goto_target(
                head=_create_head_pose(roll=-15 * amplitude, degrees=True), duration=0.4
            )
            time.sleep(0.4)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Thoughtful tilt action not supported: {e}")

    def _simple_blink_once(self):
        """Single blink"""
        try:
            # Simulate blink by closing and opening eyes
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
                time.sleep(0.2)
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5
                time.sleep(0.1)
        except Exception as e:
            print(f"⚠️ Blink action not supported: {e}")

    def _simple_happy_tilt_once(self):
        """Single happy head tilt"""
        try:
            # Happy tilt - slight backward tilt with positive yaw
            self.reachy.goto_target(
                head=_create_head_pose(pitch=-15, yaw=10, degrees=True), duration=0.4
            )
            time.sleep(0.4)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.4)
        except Exception as e:
            print(f"⚠️ Happy tilt action not supported: {e}")

    def _simple_slow_shake_once(self):
        """Single slow shake"""
        try:
            amplitude = 0.5
            self.reachy.goto_target(
                head=_create_head_pose(yaw=20 * amplitude, degrees=True), duration=0.5
            )
            time.sleep(0.3)
            self.reachy.goto_target(
                head=_create_head_pose(yaw=-20 * amplitude, degrees=True), duration=0.5
            )
            time.sleep(0.3)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Slow shake action not supported: {e}")

    # Combined action methods with synchronized blinking and body yaw
    def _combined_nod_blink(self):
        """Combined nod with blink"""
        try:
            # Start blink
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1

            # Nod movement
            amplitude = 0.6
            self.reachy.goto_target(
                head=_create_head_pose(pitch=20 * amplitude, degrees=True),
                duration=0.25,
            )
            time.sleep(0.1)

            # Finish blink during nod
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            self.reachy.goto_target(
                head=_create_head_pose(pitch=-10 * amplitude, degrees=True),
                duration=0.25,
            )
            time.sleep(0.1)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Combined nod-blink action not supported: {e}")

    def _combined_shake_blink_yaw(self):
        """Combined shake with blink and body yaw"""
        try:
            # Start blink and body yaw
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
            self.reachy.set_target_body_yaw(np.deg2rad(15))

            # Shake movement
            amplitude = 0.7
            self.reachy.goto_target(
                head=_create_head_pose(yaw=30 * amplitude, degrees=True), duration=0.3
            )
            time.sleep(0.1)

            # Mid blink
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            self.reachy.goto_target(
                head=_create_head_pose(yaw=-30 * amplitude, degrees=True), duration=0.3
            )
            time.sleep(0.1)

            # Return to neutral
            self.reachy.goto_target(
                head=_create_head_pose(), body_yaw=0.0, duration=0.5
            )
        except Exception as e:
            print(f"⚠️ Combined shake-blink-yaw action not supported: {e}")

    def _combined_wiggle_blink(self):
        """Combined antenna wiggle with blink"""
        try:
            # Start blink
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1

            # Wiggle antennas
            left_val = 0.7
            right_val = -0.7
            self.reachy.goto_target(antennas=[left_val, right_val], duration=0.15)
            time.sleep(0.1)

            # Finish blink
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            left_val = -0.7
            right_val = 0.7
            self.reachy.goto_target(antennas=[left_val, right_val], duration=0.15)
            time.sleep(0.1)
            self.reachy.goto_target(antennas=[0, 0], duration=0.3)
        except Exception as e:
            print(f"⚠️ Combined wiggle-blink action not supported: {e}")

    def _combined_happy_tilt_blink_yaw(self):
        """Combined happy tilt with blink and body yaw"""
        try:
            # Start blink and opposite body yaw for emphasis
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
            self.reachy.set_target_body_yaw(np.deg2rad(-10))

            # Happy tilt
            self.reachy.goto_target(
                head=_create_head_pose(pitch=-15, yaw=10, degrees=True), duration=0.4
            )
            time.sleep(0.2)

            # Finish blink
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            time.sleep(0.2)
            # Return to neutral
            self.reachy.goto_target(
                head=_create_head_pose(), body_yaw=0.0, duration=0.4
            )
        except Exception as e:
            print(f"⚠️ Combined happy-tilt-blink-yaw action not supported: {e}")

    def _combined_sad_blink(self):
        """Combined sad look with blink"""
        try:
            # Sad head movement with blink
            self.reachy.goto_target(
                head=_create_head_pose(pitch=15, degrees=True), duration=0.3
            )
            time.sleep(0.2)

            # Blink during sad expression
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
                time.sleep(0.3)
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            # Complete sad look
            self.reachy.goto_target(
                head=_create_head_pose(pitch=30, degrees=True), duration=0.3
            )
            time.sleep(0.3)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Combined sad-blink action not supported: {e}")

    def _combined_thoughtful_blink_yaw(self):
        """Combined thoughtful tilt with blink and subtle body yaw"""
        try:
            # Subtle body yaw and blink
            self.reachy.set_target_body_yaw(np.deg2rad(5))
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1

            # Thoughtful tilt
            amplitude = 0.6
            self.reachy.goto_target(
                head=_create_head_pose(roll=15 * amplitude, degrees=True), duration=0.4
            )
            time.sleep(0.2)

            # Finish blink
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            self.reachy.goto_target(
                head=_create_head_pose(roll=-15 * amplitude, degrees=True), duration=0.4
            )
            time.sleep(0.2)

            # Return to neutral
            self.reachy.goto_target(
                head=_create_head_pose(), body_yaw=0.0, duration=0.5
            )
        except Exception as e:
            print(f"⚠️ Combined thoughtful-blink-yaw action not supported: {e}")

    def _combined_curious_blink(self):
        """Combined curious look with blink"""
        try:
            # Start with blink
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1

            # Curious head movement
            amplitude = 0.8
            self.reachy.goto_target(
                head=_create_head_pose(
                    yaw=25 * amplitude, pitch=10 * amplitude, degrees=True
                ),
                duration=0.4,
            )
            time.sleep(0.2)

            # Mid blink finish
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            self.reachy.goto_target(
                head=_create_head_pose(
                    yaw=-25 * amplitude, pitch=10 * amplitude, degrees=True
                ),
                duration=0.4,
            )
            time.sleep(0.3)
            self.reachy.goto_target(head=_create_head_pose(), duration=0.5)
        except Exception as e:
            print(f"⚠️ Combined curious-blink action not supported: {e}")

    # Complex multi-action sequences
    def _combined_excited_sequence(self):
        """Complex excited sequence with multiple synchronized movements"""
        try:
            # Quick blink + body yaw + antenna wiggle + head nod
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
            self.reachy.set_target_body_yaw(np.deg2rad(20))

            # Antenna wiggle
            self.reachy.goto_target(antennas=[0.8, -0.8], duration=0.1)
            time.sleep(0.1)

            # Head nod with blink finish
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            self.reachy.goto_target(
                head=_create_head_pose(pitch=25, degrees=True), duration=0.2
            )
            time.sleep(0.1)

            # Reset all
            self.reachy.goto_target(
                head=_create_head_pose(), antennas=[0, 0], body_yaw=0.0, duration=0.4
            )
        except Exception as e:
            print(f"⚠️ Combined excited sequence not supported: {e}")

    def _combined_slow_sequence(self):
        """Slow deliberate sequence for negative emotions"""
        try:
            # Slow blink and subtle body movement
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
            self.reachy.set_target_body_yaw(np.deg2rad(-5))

            time.sleep(0.3)
            self.reachy.goto_target(
                head=_create_head_pose(pitch=20, degrees=True), duration=0.6
            )
            time.sleep(0.2)

            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            time.sleep(0.4)
            self.reachy.goto_target(
                head=_create_head_pose(), body_yaw=0.0, duration=0.8
            )
        except Exception as e:
            print(f"⚠️ Combined slow sequence not supported: {e}")

    def _combined_question_sequence(self):
        """Question sequence with curious head and blink"""
        try:
            # Blink and slight body lean
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
            self.reachy.set_target_body_yaw(np.deg2rad(8))

            # Curious questioning movement
            self.reachy.goto_target(
                head=_create_head_pose(yaw=15, pitch=5, degrees=True), duration=0.3
            )
            time.sleep(0.2)

            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            self.reachy.goto_target(
                head=_create_head_pose(yaw=-15, pitch=5, degrees=True), duration=0.3
            )
            time.sleep(0.2)
            self.reachy.goto_target(
                head=_create_head_pose(), body_yaw=0.0, duration=0.4
            )
        except Exception as e:
            print(f"⚠️ Combined question sequence not supported: {e}")

    def _combined_activity_sequence(self):
        """Energetic activity sequence"""
        try:
            # Fast blink + body sway + antenna excitement
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
            self.reachy.set_target_body_yaw(np.deg2rad(25))

            # Quick antenna dance
            self.reachy.goto_target(antennas=[0.9, -0.9], duration=0.1)
            time.sleep(0.1)
            self.reachy.goto_target(antennas=[-0.9, 0.9], duration=0.1)
            time.sleep(0.1)

            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            # Head shake
            self.reachy.goto_target(
                head=_create_head_pose(yaw=35, degrees=True), duration=0.2
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=_create_head_pose(), antennas=[0, 0], body_yaw=0.0, duration=0.3
            )
        except Exception as e:
            print(f"⚠️ Combined activity sequence not supported: {e}")

    def _combined_neutral_sequence(self):
        """Calm neutral sequence"""
        try:
            # Subtle blink and minimal body movement
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
            self.reachy.set_target_body_yaw(np.deg2rad(3))

            time.sleep(0.2)
            self.reachy.goto_target(
                head=_create_head_pose(pitch=8, degrees=True), duration=0.4
            )

            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            time.sleep(0.3)
            self.reachy.goto_target(
                head=_create_head_pose(), body_yaw=0.0, duration=0.5
            )
        except Exception as e:
            print(f"⚠️ Combined neutral sequence not supported: {e}")

    def _combined_negative_gesture(self):
        """Complex negative gesture sequence"""
        try:
            # Slow deliberate negative expression
            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.1
                self.reachy.head.l_eye.goal_position = 0.1
            self.reachy.set_target_body_yaw(np.deg2rad(-8))

            # Sad head movement
            self.reachy.goto_target(
                head=_create_head_pose(pitch=25, roll=5, degrees=True), duration=0.5
            )
            time.sleep(0.3)

            if hasattr(self.reachy, "head"):
                self.reachy.head.r_eye.goal_position = 0.5
                self.reachy.head.l_eye.goal_position = 0.5

            # Slow head shake
            self.reachy.goto_target(
                head=_create_head_pose(pitch=25, yaw=10, roll=5, degrees=True),
                duration=0.4,
            )
            time.sleep(0.2)
            self.reachy.goto_target(
                head=_create_head_pose(pitch=25, yaw=-10, roll=5, degrees=True),
                duration=0.4,
            )
            time.sleep(0.2)

            self.reachy.goto_target(
                head=_create_head_pose(), body_yaw=0.0, duration=0.6
            )
        except Exception as e:
            print(f"⚠️ Combined negative gesture not supported: {e}")

    def _simple_shake(self, duration: float = 2.0):
        amplitude = 0.7
        cycles = int(duration * 1.5)

        for _ in range(cycles):
            self.reachy.goto_target(
                head=_create_head_pose(yaw=30 * amplitude, degrees=True), duration=0.3
            )
            time.sleep(0.1)
            self.reachy.goto_target(
                head=_create_head_pose(yaw=-30 * amplitude, degrees=True), duration=0.3
            )
            time.sleep(0.1)

        self.reachy.goto_target(head=_create_head_pose(), duration=0.5)

    def _simple_look_curious(self, duration: float = 2.0):
        amplitude = 0.8

        self.reachy.goto_target(
            head=_create_head_pose(
                yaw=25 * amplitude, pitch=10 * amplitude, degrees=True
            ),
            duration=duration / 3,
        )
        time.sleep(duration / 3)
        self.reachy.goto_target(
            head=_create_head_pose(
                yaw=-25 * amplitude, pitch=10 * amplitude, degrees=True
            ),
            duration=duration / 3,
        )
        time.sleep(duration / 3)
        self.reachy.goto_target(head=_create_head_pose(), duration=duration / 3)

    def _simple_look_sad(self, duration: float = 2.0):
        self.reachy.goto_target(
            head=_create_head_pose(pitch=30, degrees=True), duration=duration / 2
        )
        time.sleep(duration / 2)
        self.reachy.goto_target(head=_create_head_pose(), duration=duration / 2)

    def _simple_excited_wiggle(self, duration: float = 2.0):
        cycles = int(duration * 3)

        for i in range(cycles):
            left_val = 0.7 if i % 2 == 0 else -0.7
            right_val = -0.7 if i % 2 == 0 else 0.7

            self.reachy.goto_target(antennas=[left_val, right_val], duration=0.15)
            time.sleep(0.05)

        self.reachy.goto_target(antennas=[0, 0], duration=0.3)

    def _simple_thoughtful_tilt(self, duration: float = 2.0):
        amplitude = 0.6

        self.reachy.goto_target(
            head=_create_head_pose(roll=15 * amplitude, degrees=True),
            duration=duration / 4,
        )
        time.sleep(duration / 4)
        self.reachy.goto_target(
            head=_create_head_pose(roll=-15 * amplitude, degrees=True),
            duration=duration / 4,
        )
        time.sleep(duration / 4)
        self.reachy.goto_target(head=_create_head_pose(), duration=duration / 2)


class ChatAppWithEdgeTTS:
    """Chat application with Edge-TTS"""

    def __init__(
        self,
        model: str = "qwen3.5:0.8b",
        ollama_url: str = "http://127.0.0.1:11434",
        debug: bool = False,
        gentle: bool = False,
        voice: str = "zh-CN-XiaoxiaoNeural",
    ):
        self.model = model
        self.ollama_url = ollama_url
        self.debug = debug
        self.gentle = gentle
        self.voice = voice
        self.controller = None

    def start_chat(self):
        """Start chat with Edge-TTS"""
        print("=" * 60)
        print("🤖 Reachy Mini Chat v5 with Edge-TTS")
        print("=" * 60)
        print("Features:")
        print("1. Edge-TTS (Microsoft Azure voices)")
        print("2. Your antenna/eye lip-sync approach")
        print("3. Emotion level calculation (like tts.py)")
        print("4. Recorded moves library")
        print("5. Enhanced emotion detection")
        print("=" * 60)

        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")
                self.controller = EmotionControllerV6(
                    reachy, debug=self.debug, gentle_mode=self.gentle, voice=self.voice
                )
                reachy.goto_target(head=_create_head_pose(), duration=1.0)
                time.sleep(1.0)

                print("\n💬 Start chatting (type 'quit' to exit)")
                print("🎭 Uses Edge-TTS with emotional voices")
                print("👄 Lip-sync with antennas and eyes")
                print("=" * 60)

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
                        response = self._get_ollama_response(user_input)

                        if response and self.controller:
                            emotion, intensity, emotion_level = (
                                self.controller.analyze_emotion(response)
                            )
                            if self.debug:
                                print(
                                    f"\n🎭 Emotion: {emotion}, Intensity: {intensity}, Level: {emotion_level:.2f}"
                                )
                            self.controller.speak_with_expression(
                                response, emotion, intensity, emotion_level
                            )

                    except EOFError:
                        eof_count += 1
                        if eof_count >= 3:
                            print("\n👋 EOF received, exiting chat.")
                            break
                        print("\n⚠️ Empty input (EOF). Type 'quit' to exit.")
                        continue
                    except KeyboardInterrupt:
                        print("\n\n👋 Interrupted")
                        break
                    except Exception as e:
                        print(f"\n⚠️ Error: {e}")
                        self._tts_only_mode()

        except Exception as e:
            print(f"\n❌ Cannot connect to Reachy Mini: {e}")
            self._tts_only_mode()

    def _get_ollama_response(self, prompt: str) -> Optional[str]:
        """Get response from Ollama"""
        try:
            import requests

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "system": ROBOT_PERSONA,
                    # Disable hidden chain-of-thought so the visible `response`
                    # isn't starved by the num_predict budget on thinking models.
                    "think": False,
                    # keep_alive: keep the model resident so the *next* reply
                    # doesn't pay a cold reload — snappier back-to-back at a booth.
                    "keep_alive": "30m",
                    # num_predict caps reply length. Short = faster to generate
                    # and to speak. Paired with the "2-3 sentences" persona above.
                    "options": {"temperature": 0.8, "num_predict": 120},
                },
                stream=True,
                timeout=30,
            )

            if not response.ok:
                print(f"\n⚠️ Ollama HTTP {response.status_code}: {response.text[:200]}")
                return None

            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        if chunk.get("error"):
                            print(f"\n⚠️ Ollama error: {chunk['error']}")
                            return None
                        content = chunk.get("response") or chunk.get("thinking") or ""
                        if content:
                            print(content, end="", flush=True)
                            full_response += content
                    except Exception:
                        continue

            print()
            return full_response

        except Exception as e:
            print(f"\n⚠️ Ollama error: {e}")
            return None

    def _tts_only_mode(self):
        """Run TTS without robot"""
        print("\n📻 Running in TTS-only mode (no robot)")

        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV6(reachy, debug=self.debug)

                test_texts = [
                    ("你好！我是Reachy Mini！", "neutral"),
                    ("我今天很开心！", "positive"),
                    ("我有点难过...", "negative"),
                    ("这是什么？", "question"),
                ]

                for text, emotion in test_texts:
                    print(f"\nTesting: '{text}'")
                    controller.tts_engine.speak_with_emotion(text, emotion)
                    time.sleep(1.0)

        except:
            print("\nTesting Edge-TTS standalone...")
            tts_engine = EdgeTTSEngine()
            tts_engine.speak_with_emotion("Hello! This is Edge-TTS working.", "neutral")

    def test_edge_tts(self):
        """Test Edge-TTS functionality"""
        print("🧪 Testing Edge-TTS...")

        test_sentences = [
            ("Hello! I am Reachy Mini!", "positive"),
            ("你好！我是Reachy Mini！", "neutral"),
            ("我今天非常开心！", "positive"),
            ("这是什么问题？", "question"),
        ]

        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV6(reachy, debug=self.debug)

                for text, emotion in test_sentences:
                    print(f"\nTesting: '{text}'")
                    emotion_type, intensity, level = controller.analyze_emotion(text)
                    print(f"Analyzed: {emotion_type}, {intensity}, level={level:.2f}")
                    controller.speak_with_expression(
                        text, emotion_type, intensity, level
                    )
                    time.sleep(2.0)

        except Exception as e:
            print(f"❌ Error: {e}")
            print("\nTesting Edge-TTS without robot...")
            tts_engine = EdgeTTSEngine()
            for text, emotion in test_sentences[:2]:
                print(f"\nTesting TTS: '{text}'")
                tts_engine.speak_with_emotion(text, emotion)
                time.sleep(2.0)

    def test_like_tts_py(self):
        """Test compatibility with your tts.py approach"""
        print("🧪 Testing tts.py compatibility mode...")

        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                print("模拟你的 tts.py 流程:")

                user_input = "你好，介绍一下你自己"
                print(f"\n用户: {user_input}")

                response = "你好！我是Reachy Mini，一个可爱的桌面机器人助手。我很高兴为你服务！"
                print(f"Reachy: {response}")

                emotion_level = min(len(response) / 200, 1.0)
                print(f"情感值: {emotion_level:.2f}")

                reachy.head.r_antenna.goal_position = emotion_level * 0.8
                reachy.head.l_antenna.goal_position = emotion_level * 0.8
                reachy.head.r_eye.goal_position = 1 - (emotion_level * 0.3)
                reachy.head.l_eye.goal_position = 1 - (emotion_level * 0.3)

                print("🗣️ Speaking with Edge-TTS...")
                tts_engine = EdgeTTSEngine()
                tts_engine.speak_with_emotion(response, "positive")

                reachy.head.r_antenna.goal_position = 0
                reachy.head.l_antenna.goal_position = 0
                reachy.head.r_eye.goal_position = 0.5
                reachy.head.l_eye.goal_position = 0.5

        except Exception as e:
            print(f"❌ Error: {e}")

    def test_combined_actions(self):
        """Test various combined action sequences"""
        print("🧪 Testing Reachy Mini Combined Actions")
        print("=" * 50)

        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                print("✅ Connected to Reachy Mini")

                # Initialize emotion controller
                controller = EmotionControllerV6(reachy, debug=self.debug)

                # Test each emotion's combined actions
                test_sequences = [
                    (
                        "Positive",
                        [
                            controller._combined_nod_blink,
                            controller._combined_shake_blink_yaw,
                            controller._combined_excited_sequence,
                        ],
                    ),
                    (
                        "Negative",
                        [
                            controller._combined_sad_blink,
                            controller._combined_slow_sequence,
                        ],
                    ),
                    (
                        "Question",
                        [
                            controller._combined_curious_blink,
                            controller._combined_question_sequence,
                        ],
                    ),
                    (
                        "Activity",
                        [
                            controller._combined_wiggle_blink,
                            controller._combined_activity_sequence,
                        ],
                    ),
                    (
                        "Neutral",
                        [
                            controller._combined_nod_blink,
                            controller._combined_neutral_sequence,
                        ],
                    ),
                ]

                for emotion_name, actions in test_sequences:
                    print(f"\n🎭 Testing {emotion_name} Actions")
                    print("-" * 30)

                    for i, action in enumerate(actions, 1):
                        action_name = (
                            action.__name__.replace("_combined_", "")
                            .replace("_", " ")
                            .title()
                        )
                        print(f"  {i}. Performing {action_name}...")
                        action()
                        time.sleep(2.0)  # Pause between actions

                    print(f"✅ {emotion_name} actions completed")
                    time.sleep(1.0)

                print("\n🎉 All combined action tests completed!")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("Note: Make sure Reachy Mini is connected and accessible")

    def test_individual_actions(self):
        """Test individual action components"""
        print("\n🔧 Testing Individual Action Components")
        print("=" * 50)

        try:
            from reachy_mini import ReachyMini

            with ReachyMini(media_backend="no_media") as reachy:
                controller = EmotionControllerV6(reachy, debug=self.debug)

                print("Testing basic movements:")

                # Test basic components
                print("1. Blink...")
                controller._simple_blink_once()
                time.sleep(1.5)

                print("2. Body yaw...")
                controller.reachy.set_target_body_yaw(0.3)  # 17 degrees
                time.sleep(1.0)
                controller.reachy.set_target_body_yaw(0.0)
                time.sleep(1.0)

                print("3. Antenna wiggle...")
                controller._simple_excited_wiggle_once()
                time.sleep(1.5)

                print("4. Head nod...")
                controller._simple_nod_once()
                time.sleep(1.5)

                print("✅ Individual component tests completed!")

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Reachy Mini Chat v5 with Edge-TTS")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat")
    parser.add_argument(
        "--test-tts", action="store_true", help="Test Edge-TTS functionality"
    )
    parser.add_argument(
        "--test-actions",
        action="store_true",
        help="Test combined and individual robot actions",
    )
    parser.add_argument("--model", default="qwen3.5:0.8b", help="Ollama model to use")
    parser.add_argument("--url", default="http://127.0.0.1:11434", help="Ollama URL")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument(
        "--gentle", action="store_true", help="Enable gentle_mode for subtle emotions"
    )
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="Default TTS voice")
    parser.add_argument(
        "--persona",
        default=None,
        help="Override Reachy's system-prompt personality (otherwise uses the TRY ME block)",
    )

    args = parser.parse_args()

    # CLI flags override the TRY ME defaults for coders who'd rather pass an arg.
    if args.persona:
        global ROBOT_PERSONA
        ROBOT_PERSONA = args.persona

    if not any([args.chat, args.test_tts, args.test_actions]):
        parser.print_help()
        return

    if not check_runtime_dependencies(require_reachy=True):
        return

    app = ChatAppWithEdgeTTS(
        model=args.model,
        ollama_url=args.url,
        debug=args.debug,
        gentle=args.gentle,
        voice=args.voice,
    )

    if args.test_tts:
        app.test_edge_tts()
    elif args.test_actions:
        app.test_combined_actions()

        if sys.stdin.isatty():
            print("\n" + "=" * 50)
            response = input("Also test individual components? (y/n): ").lower().strip()
            if response == "y":
                app.test_individual_actions()

    elif args.chat:
        app.start_chat()


if __name__ == "__main__":
    main()
