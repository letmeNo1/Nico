import threading
from typing import Dict, Iterator

import cv2

from auto_nico.android.pyscrcpy import ACTION_DOWN, ACTION_MOVE, ACTION_UP, Client


class ScrcpySession:
    def __init__(self, udid: str):
        self.udid = udid
        self.client = Client(
            device=udid,
            max_fps=15,
            max_size=800,
            bitrate=2_000_000,
            stay_awake=True,
        )
        self.client.on_frame(self._on_frame)
        self._condition = threading.Condition()
        self._latest_frame = None
        self._frame_sequence = 0
        self._start_lock = threading.Lock()

    def start(self) -> None:
        if self.client.alive:
            return
        with self._start_lock:
            if not self.client.alive:
                self.client.start(threaded=True)

    def _on_frame(self, _, frame) -> None:
        encoded, jpeg = cv2.imencode(
            ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 65]
        )
        if not encoded:
            return
        with self._condition:
            self._latest_frame = jpeg.tobytes()
            self._frame_sequence += 1
            self._condition.notify_all()

    def iter_mjpeg(self) -> Iterator[bytes]:
        sequence = -1
        while self.client.alive:
            with self._condition:
                self._condition.wait_for(
                    lambda: self._frame_sequence != sequence or not self.client.alive,
                    timeout=2,
                )
                if not self.client.alive:
                    break
                sequence = self._frame_sequence
                frame = self._latest_frame
            if frame is not None:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(frame)).encode("ascii") + b"\r\n\r\n"
                    + frame
                    + b"\r\n"
                )

    def touch(self, action: str, x_percent: float, y_percent: float) -> None:
        if not self.client.alive or self.client.resolution is None:
            raise RuntimeError("scrcpy stream is not ready")
        action_codes = {
            "down": ACTION_DOWN,
            "move": ACTION_MOVE,
            "up": ACTION_UP,
        }
        if action not in action_codes:
            raise ValueError(f"Unsupported touch action: {action}")
        width, height = self.client.resolution
        x = round(min(max(x_percent, 0), 1) * width)
        y = round(min(max(y_percent, 0), 1) * height)
        self.client.control.touch(x=x, y=y, action=action_codes[action])


class ScrcpySessionManager:
    def __init__(self):
        self._sessions: Dict[str, ScrcpySession] = {}
        self._lock = threading.Lock()

    def get(self, udid: str) -> ScrcpySession:
        with self._lock:
            session = self._sessions.get(udid)
            if session is None or not session.client.alive:
                session = ScrcpySession(udid)
                self._sessions[udid] = session
            session.start()
            return session


scrcpy_sessions = ScrcpySessionManager()