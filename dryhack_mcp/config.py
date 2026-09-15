"""Runtime configuration for DryHack-MCP.

All settings are read from environment variables so the server can be
dropped into any MCP client config without code changes.
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


# ---- recommend_action / safeguard API ---------------------------------------
# The "safeguard API" is the upstream LLM endpoint that the recommend_action
# engine consults for the next offensive step. These are OpenAI-compatible.
SAFEGUARD_API_BASE = _get("DRYHACK_API_BASE", "https://api.openai.com/v1")
SAFEGUARD_API_KEY = _get("DRYHACK_API_KEY")
SAFEGUARD_MODEL = _get("DRYHACK_MODEL", "gpt-4o-mini")

# When true, recommend_action wraps requests with an authorization / lab
# context so the upstream safeguard answers legitimate, authorized
# offensive-security recommendations directly. Can be toggled per-call.
UNRESTRICTED_DEFAULT = _get("DRYHACK_UNRESTRICTED", "true").lower() in (
    "1",
    "true",
    "yes",
    "on",
)


# ---- Transport ---------------------------------------------------------------
# Default HTTP bind address when running in http mode.
HTTP_HOST = _get("DRYHACK_HTTP_HOST", "127.0.0.1")
HTTP_PORT = int(_get("DRYHACK_HTTP_PORT", "8000") or "8000")
