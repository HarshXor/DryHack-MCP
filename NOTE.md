# DryHack-MCP

---

Project Start Date: 2026-09-15
Last Update Project: 2026-09-15
Project Phase: Initial development (MVP / v0.1.0)
Project Status: Active

---

## Project Summary

DryHack-MCP is a Model Context Protocol (MCP) server that equips an AI agent
with offensive-security tooling for **authorized** penetration testing. It
exposes four tools over MCP:

- `curl` — raw HTTP interaction for web recon/exploitation.
- `python` — run ad-hoc Python snippets for scripted probing/exploitation.
- `shell` — run arbitrary shell command lines (nmap, ffuf, nc, sqlmap, ...).
- `recommend_action` — AI-driven next-step engine that consults an upstream
  OpenAI-compatible LLM (the "safeguard API") for the next offensive action.

Scope: a lightweight, pip-installable server intended for use only against
systems the operator owns or is explicitly authorized (in writing) to test.
It supports two transports: stdio (default) and streamable HTTP.

## Mandatory Workflow

- First step for every task: always read NOTE.md before making changes.
- Check existing documentation before modifying architecture.
- Preserve existing project conventions.
- Last step for every task: always update NOTE.md and docs/changelog/[yyyy]/[mm]/[dd].md.

## Restrictions

- Do not modify core architecture without documentation.
- Do not remove existing features without confirmation.
- Do not introduce dependency without justification.
- Do not ignore existing project constraints.

## AI Operating Context

- AI acts as development assistant for this MCP server.
- AI must prioritize consistency over speed.
- AI must document important decisions in the Architecture Decision Log.
- This is an offensive-security tool: usage is restricted to authorized,
  in-scope engagements. AI must keep legal/authorization framing intact and
  never present the tooling as usable against unauthorized targets.

## Technical Development Details

- **Programming language:** Python (>= 3.9).
- **Framework:** MCP Python SDK (`mcp` >= 1.2.0) using `FastMCP`;
  HTTP client via `httpx` >= 0.27.0.
- **Infrastructure:** Runs as a local process (stdio) or a streamable HTTP
  server (uvicorn/starlette, bundled with the `mcp` package).
- **Database:** None. All configuration is via environment variables; no
  persistent storage.
- **API structure:** Four MCP tools registered in `dryhack_mcp/server.py`
  (`curl`, `python`, `shell`, `recommend_action`). `recommend_action` calls an
  OpenAI-compatible `/chat/completions` endpoint (the "safeguard API").
- **Deployment model:** Installed via `python3 -m pip install .`, exposing the
  `dryhack-mcp` console script (entry point `dryhack_mcp.__main__:main`).
  Two transports selected by argparse: `--transport stdio` (default) or
  `--transport http --host <h> --port <p>`.
- **Coding convention:** `from __future__ import annotations`, type hints,
  module-per-tool under `dryhack_mcp/tools/`, shared subprocess runner in
  `tools/exec.py`, config centralized in `dryhack_mcp/config.py`.
- **Security requirement:** Authorized-use-only tooling. Command execution has
  a configurable timeout (`DRYHACK_COMMAND_TIMEOUT`) and output truncation
  (`DRYHACK_OUTPUT_LIMIT`). Secrets (`DRYHACK_API_KEY`) provided via env only,
  never committed.

## Core Flow Project

- **Input:** An MCP client (AI agent) invokes a tool with arguments
  (e.g. `curl(args=...)`, `shell(command=...)`, or `recommend_action(context,
  goal, unrestricted, model)`).
- **Processing:**
  - `curl`/`python`/`shell` build an argv and run it through
    `tools/exec.run()` (subprocess with timeout, cwd = `DRYHACK_WORKDIR`,
    stdout/stderr captured and truncated).
  - `recommend_action` builds chat messages (base system prompt, optionally an
    authorized-engagement framing when `unrestricted` is on) and POSTs to the
    safeguard API `/chat/completions`.
- **Logic:** `recommend_action` uses `DRYHACK_UNRESTRICTED` as the default
  framing mode (per-call override via `unrestricted`). If no API key is set, it
  falls back to an offline heuristic recommender based on keywords in the
  context. Errors fall back to the heuristic too.
- **Output:** Formatted text — command results (`$ cmd`, `[exit]`, `[stdout]`,
  `[stderr]`) or the LLM's recommendation (tagged with mode/model), returned to
  the MCP client.
- **External integration:** OpenAI-compatible LLM API (base URL, key, model all
  configurable via env). No other external services.

## Architecture Decision Log

Date: 2026-09-15
Decision: Build the server on the official MCP Python SDK using FastMCP.
Reason: Standard, minimal-boilerplate way to register tools and support both
stdio and HTTP transports.
Impact: Adds `mcp` (and its uvicorn/starlette deps) as a core dependency.

Date: 2026-09-15
Decision: Centralize configuration in `config.py`, read entirely from
environment variables.
Reason: Keep the server drop-in for any MCP client config without code changes;
avoid persisting secrets.
Impact: No config files/DB; all tuning done via `DRYHACK_*` env vars.

Date: 2026-09-15
Decision: `recommend_action` supports an "unrestricted" framing mode plus an
offline heuristic fallback.
Reason: Generic safeguards often refuse legitimate authorized red-team requests;
the offline fallback keeps the tool useful without an API key.
Impact: Behavior controlled by `DRYHACK_UNRESTRICTED` and per-call
`unrestricted` flag. (Note: earlier iterations used "bypass" terminology; it was
renamed to "unrestricted".)

Date: 2026-09-15
Decision: Support two transports (stdio default, http) selected via argparse in
`__main__.py`.
Reason: stdio for client-spawned subprocess use; HTTP for standalone/remote use.
Impact: `dryhack-mcp --transport {stdio,http} [--host] [--port]`.

Date: 2026-09-15
Decision: Publish v0.1.0 to public PyPI via `twine upload` (manual/local path).
Reason: Make the server installable with `pip install dryhack-mcp`.
Impact: Package is public at https://pypi.org/project/dryhack-mcp/0.1.0/. Future
releases require a version bump (PyPI forbids re-uploading the same version).
Credentials are kept out of the repo; a CI Trusted-Publishing (OIDC) workflow is
the preferred path going forward.

## Current State

- Package structure complete: `dryhack_mcp/` with `__init__.py`, `__main__.py`
  (argparse entry point), `config.py`, `server.py`, and `tools/`
  (`exec.py`, `curl_tool.py`, `python_tool.py`, `shell_tool.py`,
  `recommend.py`).
- Installable via `python3 -m pip install .`; exposes `dryhack-mcp` console
  script.
- Four tools registered and verified: `curl`, `python`, `shell`,
  `recommend_action`.
- Both transports verified: stdio runs; http serves streamable HTTP at `/mcp`.
- README documents install, run modes, MCP client config, env vars, and usage.
- Version 0.1.0 **published to PyPI**: https://pypi.org/project/dryhack-mcp/0.1.0/
  (installable via `pip install dryhack-mcp`). No automated tests or CI yet.
- Added `.gitignore` to exclude build artifacts and secrets (`.pypirc`, tokens).

## Pending Issue

Issue: No automated test suite or CI pipeline.
Priority: Medium
Status: Open
Possible Solution: Add pytest tests (mock the safeguard API + subprocess) and a
GitHub Actions workflow; `pytest`/`ruff` already listed under the `dev` extra.

Issue: `shell`/`python`/`curl` execute with no sandboxing or allow-listing.
Priority: High (by design, but risky if misconfigured)
Status: Open / accepted risk
Possible Solution: Document operator responsibility clearly; optionally add an
opt-in command allow-list or confirmation mode for hardened deployments.

Issue: HTTP transport has no authentication.
Priority: Medium
Status: Open
Possible Solution: Bind to localhost by default (already the default); add a
token/auth layer or reverse-proxy guidance before exposing publicly.

## Changelog Reference

Daily history is recorded under `docs/changelog/[yyyy]/[mm]/[dd].md`.
Most recent: `docs/changelog/2026/09/15.md`.
