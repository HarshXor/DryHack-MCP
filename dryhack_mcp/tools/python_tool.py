"""python tool: run ad-hoc Python for scripted probing/exploitation."""
from __future__ import annotations

import sys
from typing import Optional

from . import exec as _exec


def python_run(code: str, timeout: Optional[int] = None) -> str:
    """Execute a Python snippet with the current interpreter.

    Args:
        code: Python source to run (executed via `python -c`).
        timeout: Optional per-command timeout in seconds.
    """
    argv = [sys.executable, "-c", code]
    return _exec.run(argv, timeout=timeout)
