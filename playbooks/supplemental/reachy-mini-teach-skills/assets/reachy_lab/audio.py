# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

"""Save Reachy's voice to WAV files instead of playing it on a speaker.

The lab's voices call sounddevice.play() then sounddevice.wait(). redirect() replaces both:
play() writes the clip and passes it to a callback, wait() sleeps for the clip's length so the
gestures stay in time with the words.
"""

from __future__ import annotations

import sys
import tempfile
import threading
import time
import types
from pathlib import Path

_state = {"until": 0.0, "n": 0}
_lock = threading.Lock()


def redirect(on_clip, out_dir: str | None = None):
    """on_clip(path, seconds) is called for every sentence Reachy says."""
    out = Path(out_dir or tempfile.mkdtemp(prefix="reachy_voice_"))
    out.mkdir(parents=True, exist_ok=True)

    def play(data, samplerate=None, **_):
        import numpy as np
        import soundfile as sf

        data = np.asarray(data, dtype="float32")
        if data.size == 0 or not samplerate:
            return
        with _lock:
            _state["n"] += 1
            path = out / f"reachy_says_{_state['n']:03d}.wav"
        sf.write(path, data, int(samplerate), subtype="PCM_16")
        seconds = len(data) / float(samplerate)
        _state["until"] = time.time() + seconds
        on_clip(str(path), seconds)

    def wait(*_, **__):
        time.sleep(max(0.0, _state["until"] - time.time()))

    try:
        import sounddevice as sd
    except Exception:  # no PortAudio (e.g. CI)
        sd = types.ModuleType("sounddevice")
        sys.modules["sounddevice"] = sd
    sd.play, sd.wait = play, wait
    return out
