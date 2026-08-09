"""Global kill switch suitable for emergency halt operations."""

from __future__ import annotations

import threading


class KillSwitch:
    """A thread-safe global kill switch. Setting it flips the internal flag.

    The engine should poll `is_tripped()` frequently to react quickly.
    """

    def __init__(self) -> None:
        self._evt = threading.Event()

    def trip(self) -> None:
        self._evt.set()

    def reset(self) -> None:
        self._evt.clear()

    def is_tripped(self) -> bool:
        return self._evt.is_set()


class KillSwitchTripped(Exception):
    pass
