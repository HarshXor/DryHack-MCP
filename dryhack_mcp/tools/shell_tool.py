"""shell tool: run arbitrary shell commands (nmap, ffuf, nc, etc.)."""
from __future__ import annotations

from typing import Optional

from . import exec as _exec


def shell(command: str, timeout: Optional[int] = None) -> str:
    """Run a command line through the system shell.

    Args:
        command: The full shell command line to execute.
        timeout: Optional per-command timeout in seconds.
    """
    argv = ["/bin/sh", "-c", command]
    return _exec.run(argv, timeout=timeout)
