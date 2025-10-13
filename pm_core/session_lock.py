import tkinter as tk
from typing import Callable

class SessionLock:
    def __init__(self, root: tk.Tk, timeout_minutes: int, on_lock: Callable[[], None]):
        self.root = root
        self.ms = int(timeout_minutes * 60_000)
        self.on_lock = on_lock
        self._timer = None
        # Bind a few common activity events to reset the timer
        for ev in ("<Motion>", "<Key>", "<Button>"):
            root.bind_all(ev, self._reset)
        self._arm()

    def _arm(self):
        self._cancel()
        self._timer = self.root.after(self.ms, self._lock)

    def _cancel(self):
        if self._timer is not None:
            try:
                self.root.after_cancel(self._timer)
            except Exception:
                pass
            self._timer = None

    def _reset(self, *_):
        self._arm()

    def _lock(self):
        try:
            self.on_lock()
        finally:
            self._arm()
