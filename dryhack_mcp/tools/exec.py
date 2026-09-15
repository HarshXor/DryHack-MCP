"""Shared command-execution helpers for curl / python / shell tools."""
from __future__ import annotations

import shlex
import subprocess
from typing import List, Optional

from .. import config


def _truncate(data: str, limit: int) -> str:
    if len(data.encode("utf-8", "replace")) <= limit:
        return data
    clipped = data.encode("utf-8", "replace")[:limit].decode("utf-8", "ignore")
    return clipped + f"\n... [truncated to {limit} bytes]"


def run(
    argv: List[str],
    *,
    stdin: Optional[str] = None,
    timeout: Optional[int] = None,
    cwd: Optional[str] = None,
) -> str:
    """Execute a command and return a formatted result string."""
    timeout = timeout or config.COMMAND_TIMEOUT
    cwd = cwd or config.WORKDIR
    printable = " ".join(shlex.quote(a) for a in argv)
    try:
        proc = subprocess.run(
            argv,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except FileNotFoundError:
        return f"$ {printable}\n[error] executable not found: {argv[0]!r}"
    except subprocess.TimeoutExpired:
        return f"$ {printable}\n[error] command timed out after {timeout}s"
    except Exception as exc:  # pragma: no cover - defensive
        return f"$ {printable}\n[error] {type(exc).__name__}: {exc}"

    out = _truncate(proc.stdout or "", config.OUTPUT_BYTE_LIMIT)
    err = _truncate(proc.stderr or "", config.OUTPUT_BYTE_LIMIT)
    parts = [f"$ {printable}", f"[exit] {proc.returncode}"]
    if out:
        parts.append(f"[stdout]\n{out}")
    if err:
        parts.append(f"[stderr]\n{err}")
    return "\n".join(parts)
