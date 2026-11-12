# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
#
# Portions of this file consist of AI-generated content. AI-assisted
# content has been reviewed and validated by the authors.

"""Reachy Mini in the MuJoCo simulator.

SimDaemon runs Pollen Robotics' simulator daemon, which moves the joints like the real robot's
daemon. SimWorld follows those joints in the same scene, with a table, and renders the reader's
view and Reachy's head camera.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

if sys.platform.startswith("linux"):
    os.environ.setdefault("MUJOCO_GL", "egl")  # render offscreen on the GPU; Windows uses its default (WGL)


def daemon_status(port: int) -> dict | None:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/daemon/status", timeout=2) as r:
            return json.load(r)
    except Exception:
        return None


class SimDaemon:
    """Starts the simulator in its own process and always stops it: `with SimDaemon(8765): ...`"""

    def __init__(self, port: int = 8765, log_path: str | None = None):
        self.log_path = log_path or str(Path(os.environ.get("REACHY_LAB_LOGS", ".")) / "sim_daemon.log")
        self.port, self.proc = port, None

    def __enter__(self):
        if daemon_status(self.port):
            raise RuntimeError(f"something already answers on port {self.port}: close it and try again")
        cmd = [sys.executable, "-m", "reachy_mini.daemon.app.main", "--sim", "--headless", "--scene", "minimal",
               "--no-media", "--fastapi-host", "127.0.0.1", "--fastapi-port", str(self.port),
               "--no-preload-datasets", "--no-goto-sleep-on-stop", "--log-level", "WARNING"]
        kw = {"start_new_session": True} if os.name == "posix" else {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        self._log = open(self.log_path, "w")
        self.proc = subprocess.Popen(cmd, stdout=self._log, stderr=subprocess.STDOUT, **kw)
        t0 = time.time()
        while time.time() - t0 < 90 and self.proc.poll() is None:
            if (daemon_status(self.port) or {}).get("state") == "running":
                return self
            time.sleep(0.5)
        self.__exit__()
        raise RuntimeError(f"the simulator did not start; see {self.log_path}")

    def __exit__(self, *exc):
        if self.proc and self.proc.poll() is None:
            if os.name == "posix":
                os.killpg(self.proc.pid, signal.SIGTERM)
            else:
                self.proc.send_signal(signal.CTRL_BREAK_EVENT)
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        if getattr(self, "_log", None):
            self._log.close()
        return False


def connect(port: int):
    """The Reachy Mini SDK client, talking to the simulator daemon."""
    from reachy_mini import ReachyMini

    return ReachyMini(host="127.0.0.1", port=port, connection_mode="localhost_only", media_backend="no_media")


class SimWorld:
    def __init__(self, mini, eye_size=(640, 360), view_size=(640, 480), fps: float = 15.0):
        import mujoco
        import reachy_mini

        scene = Path(reachy_mini.__file__).parent / "descriptions" / "reachy_mini" / "mjcf" / "scenes" / "minimal.xml"
        self.mujoco, self.mini, self.fps = mujoco, mini, fps
        self.m = mujoco.MjModel.from_xml_path(str(scene))
        self.d = mujoco.MjData(self.m)
        self.eye_size, self.view_size = eye_size, view_size
        self.eye_cam = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_CAMERA, "eye_camera")
        # The reader's view: from across the table, so Reachy's face and the objects are both in the picture
        self.view_cam = mujoco.MjvCamera()
        self.view_cam.type = mujoco.mjtCamera.mjCAMERA_FREE
        self.view_cam.lookat[:] = (0.3, 0.0, 0.05)
        self.view_cam.azimuth, self.view_cam.elevation, self.view_cam.distance = 200.0, -25.0, 1.3
        self.eye = self.view = None  # latest RGB pictures
        self._stop, self._ready = threading.Event(), threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        if not self._ready.wait(60):
            raise RuntimeError("the simulator could not render a picture (is the graphics driver installed?)")

    def _run(self):
        """Everything that renders runs on this thread, which owns the GPU context."""
        import numpy as np

        mj = self.mujoco
        eye_r = mj.Renderer(self.m, height=self.eye_size[1], width=self.eye_size[0])
        view_r = mj.Renderer(self.m, height=self.view_size[1], width=self.view_size[0])
        for _ in range(300):  # let the objects settle on the table
            mj.mj_step(self.m, self.d)
        while not self._stop.is_set():
            t0 = time.time()
            try:
                head, antennas = self.mini.get_current_joint_positions()
            except Exception:
                break  # the simulator has stopped
            self.d.ctrl[:7] = head
            self.d.ctrl[-2:] = -np.asarray(antennas)
            for _ in range(max(1, int(1 / self.fps / self.m.opt.timestep))):
                mj.mj_step(self.m, self.d)
            eye_r.update_scene(self.d, camera=self.eye_cam)
            view_r.update_scene(self.d, camera=self.view_cam)
            self.eye, self.view = eye_r.render().copy(), view_r.render().copy()
            self._ready.set()
            time.sleep(max(0.0, 1 / self.fps - (time.time() - t0)))
        eye_r.close()
        view_r.close()

    def eye_frame(self, settle: float = 1.0):
        """What Reachy sees (RGB), after waiting for the head to finish moving."""
        time.sleep(settle)
        return self.eye

    def close(self):
        self._stop.set()
        self.thread.join(timeout=5)
