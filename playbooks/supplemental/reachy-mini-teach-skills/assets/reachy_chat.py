# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

"""Reachy Mini's brain, voice and eyes in one short script.

  python reachy_chat.py                  # a joke, then what Reachy sees on the table
  python reachy_chat.py "Who are you?"

Saves what Reachy says to reachy_says_*.wav and what it sees to reachy_sees.jpg.
"""

import base64
import json
import sys
import time
import urllib.request
from pathlib import Path

import cv2

from reachy_lab import config
from reachy_lab.sim import SimDaemon, SimWorld, connect

ASSETS = Path(__file__).resolve().parent
sys.path.insert(0, str(ASSETS / "lab"))  # emo_v1, emo_v2 from the Reachy Mini lab


def start_reachy(port=8765):
    """Start the simulator, connect to Reachy, and open the scene that renders its camera."""
    daemon = SimDaemon(port).__enter__()
    mini = connect(port).__enter__()
    return daemon, mini, SimWorld(mini)


def ask(prompt, system=None, image=None, model=config.CHAT_MODEL, temperature=0.8):
    """Send a message, and optionally a picture, to the model Ollama runs on the iGPU."""
    payload = {"model": model, "prompt": prompt, "think": False, "stream": False, "keep_alive": "30m",
               "options": {"temperature": temperature, "num_predict": 120, "num_ctx": 4096}}
    if system:
        payload["system"] = system
    if image is not None:  # an RGB picture: send it as JPEG, encoded in base64
        jpg = cv2.imencode(".jpg", image[:, :, ::-1])[1]
        payload["images"] = [base64.b64encode(jpg.tobytes()).decode()]
    request = urllib.request.Request(config.OLLAMA_URL + "/api/generate", data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as r:
        return json.load(r)["response"].strip()


def voice(mini, piper_model=None, edge_voice=config.VOICE_1):
    """Thomas' controllers: a local Piper voice if a model file is given, otherwise a cloud Edge voice."""
    if piper_model:
        from emo_v2 import EmotionControllerV71
        return EmotionControllerV71(mini, str(ASSETS / piper_model), piper_config=None, speaker_id=0, gentle_mode=True)
    from emo_v1 import EmotionControllerV6
    return EmotionControllerV6(mini, gentle_mode=True, voice=edge_voice)


def speak(controller, text):
    """Read the mood of the text, then say it while Reachy moves its head and antennas to match."""
    from emo_v1 import strip_emojis
    emotion, intensity, level = controller.analyze_emotion(text)
    controller.speak_with_expression(strip_emojis(text), emotion, intensity, level)
    return emotion


def look_at_table(mini, world):
    """Tilt Reachy's head down to the table and return what its head camera sees."""
    from reachy_mini.utils import create_head_pose
    mini.goto_target(head=create_head_pose(pitch=22, degrees=True), duration=0.8)
    return world.eye_frame(settle=1.0)


def main():
    from reachy_lab.audio import redirect

    question = " ".join(sys.argv[1:]) or "Tell me a joke!"
    redirect(lambda path, seconds: print(f"  (Reachy said {seconds:.1f} s of speech: {path})"), out_dir=".")
    daemon, mini, world = start_reachy()
    try:
        t0 = time.time()
        reply = ask(question, system=config.PERSONA_2)
        print(f"You: {question}\nReachy: {reply}  ({time.time() - t0:.1f} s on the iGPU)")
        reachy_voice = voice(mini, piper_model=config.PIPER_VOICE)
        print(f"  emotion: {speak(reachy_voice, reply)}")

        picture = look_at_table(mini, world)
        cv2.imwrite("reachy_sees.jpg", picture[:, :, ::-1])
        t0 = time.time()
        seen = ask(f"{config.VISION_STYLE} You are looking through your own camera. What do you see?",
                   image=picture, model=config.VISION_MODEL, temperature=0.5)
        print(f"Reachy sees: {seen}  ({time.time() - t0:.1f} s on the iGPU)")
        speak(reachy_voice, seen)
    finally:
        world.close()
        mini.__exit__(None, None, None)
        daemon.__exit__()


if __name__ == "__main__":
    main()
