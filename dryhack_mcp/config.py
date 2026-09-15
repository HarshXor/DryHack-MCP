"""Runtime configuration for DryHack-MCP.

Only operational, non-secret settings live here. The server intentionally
stores NO credentials/API keys of any kind.
"""
from __future__ import annotations

import os


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


# ---- Command execution -------------------------------------------------------
# Default per-command timeout (seconds) for curl / python / shell tools.
COMMAND_TIMEOUT = int(_get("DRYHACK_COMMAND_TIMEOUT", "120") or "120")

# Working directory for spawned commands. Defaults to the current dir.
WORKDIR = _get("DRYHACK_WORKDIR", os.getcwd())

# Max bytes captured from stdout/stderr before truncation.
OUTPUT_BYTE_LIMIT = int(_get("DRYHACK_OUTPUT_LIMIT", "65536") or "65536")


# ---- Transport ---------------------------------------------------------------
# Default HTTP bind address when running in http mode.
HTTP_HOST = _get("DRYHACK_HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(_get("DRYHACK_HTTP_PORT", "8000") or "8000")
