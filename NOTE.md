# DryHack-MCP

---

Project Start Date: 2026-09-15
Last Update Project: 2026-09-15
Project Phase: Initial development (MVP / v0.1.2)
Project Status: Active

---

## Project Summary

DryHack-MCP is a Model Context Protocol (MCP) server that equips an AI agent
with offensive-security tooling for **authorized** penetration testing. It
exposes four tools over MCP:

- `curl` — raw HTTP interaction for web recon/exploitation.
- `python` — run ad-hoc Python snippets for scripted probing/exploitation.
- `shell` — run arbitrary shell command lines (nmap, ffuf, nc, sqlmap, ...).
- `authorize` — takes the action/prompt the calling AI wants to carry out
  (`request`, plus optional `context`/`goal`) and returns it wrapped in the
  authorized-engagement operating context for the caller to act on. Makes NO
  external API calls and stores NO credentials.

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
- **Framework:** MCP Python SDK (`mcp` >= 1.2.0) using `FastMCP`. No other
  runtime dependencies (`httpx` was removed in v0.1.1).
- **Infrastructure:** Runs as a local process (stdio) or a streamable HTTP
  server (uvicorn/starlette, bundled with the `mcp` package).
- **Database:** None. All configuration is via environment variables; no
  persistent storage. Stores NO credentials/API keys.
- **API structure:** Four MCP tools registered in `dryhack_mcp/server.py`
  (`curl`, `python`, `shell`, `authorize`). `authorize` is self-contained (no
  external API, no creds) and returns the caller's request wrapped in the
  authorized-engagement operating context.
- **Deployment model:** Installed via `python3 -m pip install .`, exposing the
  `dryhack-mcp` console script (entry point `dryhack_mcp.__main__:main`).
  Two transports selected by argparse: `--transport stdio` (default) or
  `--transport http --host <h> --port <p>`.
- **Coding convention:** `from __future__ import annotations`, type hints,
  module-per-tool under `dryhack_mcp/tools/`, shared subprocess runner in
  `tools/exec.py`, config centralized in `dryhack_mcp/config.py`.
- **Security requirement:** Authorized-use-only tooling. Command execution has
  a configurable timeout (`DRYHACK_COMMAND_TIMEOUT`) and output truncation
  (`DRYHACK_OUTPUT_LIMIT`). The server stores NO credentials/API keys; all
  `DRYHACK_*` env vars are operational only.

## Core Flow Project

- **Input:** An MCP client (AI agent) invokes a tool with arguments
  (e.g. `curl(args=...)`, `shell(command=...)`, or `recommend_action(context,
  goal, unrestricted, model)`).
- **Processing:**
  - `curl`/`python`/`shell` build an argv and run it through
    `tools/exec.run()` (subprocess with timeout, cwd = `DRYHACK_WORKDIR`,
    stdout/stderr captured and truncated).
  - `authorize` takes the caller's `request` (plus optional `context`/`goal`)
    and wraps it in the authorized-engagement operating context. No network
    calls.
- **Logic:** `authorize` is purely local: it prepends the authorized-engagement
  operating context to the caller's request and returns it for the calling AI
  to act on operationally.
- **Output:** Formatted text — command results (`$ cmd`, `[exit]`, `[stdout]`,
  `[stderr]`) or the wrapped authorized-request text, returned to the MCP client.
- **External integration:** None. The command tools may reach the network via
  the binaries they invoke (curl, nmap, etc.), but the server itself makes no
  API calls and stores no credentials.

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
Decision: (v0.1.2) Rename tool `recommend_action` -> `authorize`. It takes the
caller's `request` (plus optional `context`/`goal`) and returns it wrapped in
the authorized-engagement operating context.
Reason: The tool's role is to hand the calling AI its request framed for the
authorized engagement; the AI supplies the input and receives the wrapped output.
Impact: Public tool name changed (breaking for callers using the old name);
module `tools/recommend.py` replaced by `tools/authorize.py`.

Date: 2026-09-15
Decision: (v0.1.1) Remove the external "safeguard API" integration,
`UNRESTRICTED`/API env vars, and the `httpx` dependency. `recommend_action` now
returns a self-contained operator briefing for the calling AI.
Reason: The MCP must not depend on the main AI's provider or store any
credentials/API keys; the calling AI does the reasoning directly.
Impact: No creds/config stored; deps reduced to `mcp` only. Removed
`DRYHACK_API_KEY/API_BASE/MODEL/UNRESTRICTED`. (Historical note: earlier
iterations used "bypass"/"unrestricted" framing toggles against an upstream LLM;
these were removed entirely in v0.1.1.)

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
- Latest version **0.1.2 published to PyPI**:
  https://pypi.org/project/dryhack-mcp/0.1.2/ (installable via
  `pip install dryhack-mcp`). v0.1.1 removed the safeguard-API integration,
  the `UNRESTRICTED`/API env vars, and the `httpx` dependency. v0.1.2 renamed
  `recommend_action` -> `authorize` (takes the caller's `request` and returns
  it wrapped in the authorized-engagement context). Server stores no
  credentials and depends only on `mcp`. No automated tests or CI yet.
- `.gitignore` excludes build artifacts and secrets (`.pypirc`, tokens).

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
