# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

"""The three lab tasks for the web app, built on the functions in reachy_chat.py.

The queue lets the page send messages while Reachy is still talking.
"""

from __future__ import annotations

import queue
import sys
import threading
import time
import urllib.error
from collections import deque
from pathlib import Path

from . import config

ASSETS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ASSETS))
from reachy_chat import ask, look_at_table, speak, start_reachy, voice  # noqa: E402


class Lab:
    def __init__(self, log=print):
        self.log = log
        self.daemon, self.mini, self.world = start_reachy()
        self.persona = {1: config.PERSONA_1, 2: config.PERSONA_2}
        self.voice = {1: config.VOICE_1, 2: config.PIPER_VOICE}
        self.style = config.VISION_STYLE
        self.history: list[dict] = []
        self._voices = {}

    def _voice(self, task: int):
        key = (task, self.voice[task])
        if key not in self._voices:  # Task 1: Edge voice; Tasks 2 and 3: Piper voice
            self._voices[key] = voice(self.mini, edge_voice=self.voice[1]) if task == 1 else \
                voice(self.mini, piper_model=self.voice[2])
        return self._voices[key]

    def _answer(self, task: int, question: str, text: str, seconds: float) -> dict:
        self.log(f"Reachy{' sees' if task == 3 else ''}: {text}  ({seconds:.1f} s on the iGPU)")
        out = {"task": task, "you": question, "reachy": text, "llm_s": round(seconds, 2)}
        if text:
            out["emotion"] = speak(self._voice(1 if task == 1 else 2), text)
            self.log(f"  emotion: {out['emotion']}")
        return out

    def chat(self, task: int, message: str) -> dict:
        """Tasks 1 and 2."""
        t0 = time.time()
        return self._answer(task, message, ask(message, system=self.persona[task]), time.time() - t0)

    def look(self, question: str) -> dict:
        """Task 3."""
        picture = look_at_table(self.mini, self.world)
        t0 = time.time()
        text = ask(f"{self.style.strip()} You are looking through your own camera. Answer this about what you "
                   f"currently see: {question}", image=picture, model=config.VISION_MODEL, temperature=0.5)
        return self._answer(3, question, text, time.time() - t0)

    def close(self):
        for fn in (self.world.close, lambda: self.mini.__exit__(None, None, None), self.daemon.__exit__):
            try:
                fn()
            except Exception:
                pass


class Runner:
    """Runs messages one at a time, in order, so the web page stays responsive."""

    def __init__(self):
        self.lines: deque[str] = deque(maxlen=300)
        self.busy = False
        self._q: queue.Queue = queue.Queue()
        self.lab = Lab(log=self.log)
        threading.Thread(target=self._work, daemon=True).start()

    def log(self, *parts):
        for line in " ".join(str(p) for p in parts).splitlines() or [""]:
            self.lines.append(line)

    def _work(self):
        while True:
            fn, args = self._q.get()
            self.busy = True
            try:
                self.lab.history.append(fn(*args))
            except urllib.error.URLError:
                self.log("error: Ollama is not answering. Start Ollama, then try again.")
            except Exception as e:  # keep the worker alive; show the error in the conversation
                self.log(f"error: {e}")
            finally:
                self.busy = not self._q.empty()
                self._q.task_done()

    def send(self, task: int, text: str):
        text = (text or "").strip()
        if not text:
            return
        self.log(f"\n[Task {task}] You: {text}")
        self._q.put((self.lab.look, (text,)) if task == 3 else (self.lab.chat, (task, text)))

    def wait(self, timeout: float | None = None):
        t0 = time.time()
        while self._q.unfinished_tasks and (timeout is None or time.time() - t0 < timeout):
            time.sleep(0.1)

    def close(self):
        self.wait(timeout=60)
        self.lab.close()
