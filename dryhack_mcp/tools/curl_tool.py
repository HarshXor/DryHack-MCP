"""curl tool: raw HTTP interaction for web recon/exploitation."""
from __future__ import annotations

import shlex
from typing import Optional

from . import exec as _exec


def curl(args: str, timeout: Optional[int] = None) -> str:
    """Run curl with the given argument string.

    Args:
        args: Arguments passed to curl, e.g. "-skiL https://target/". Do not
            include the leading `curl`.
        timeout: Optional per-command timeout in seconds.
    """
    argv = ["curl"] + shlex.split(args)
    return _exec.run(argv, timeout=timeout)
