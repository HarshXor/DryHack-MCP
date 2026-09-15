# DryHack-MCP

---

Project Start Date: 2026-09-15
Last Update Project: 2026-09-15
Project Phase: Initial development (v2.1.2)
Project Status: Active

---

## Latest working-tree update (2026-09-15) — released as v2.1.2

**Self-correction (leave this here for the next session):** an earlier pass in
this same session mistakenly claimed the per-call `scope` change had already
shipped as v2.1.1. That was wrong — checked directly against the git history
and the package actually uploaded: **v2.1.1 (still on PyPI) is the
`DRYHACK_SCOPE`-env-var design**, signature `authorize(target, request,
context="", goal="")`, with no `scope` parameter at all. The per-call
`scope: list[str]` parameter had only been made in the local working tree
(uncommitted) and had never been released before this session. Both changes
below are real and are now correctly bundled into the v2.1.2 release that was
actually built and uploaded this session.

v2.1.2 bundles two changes, both verified against the actual diff from the
last committed/released state (v2.1.1):

1. **Breaking:** `authorize(target, request, scope: list[str], context="",
   goal="")` replaces the `DRYHACK_SCOPE` environment variable with a
   required per-call `scope` argument. `config.SCOPE`/`DRYHACK_SCOPE` were
   removed entirely; `tools/scope.py::check()` now takes `scope` as a
   parameter instead of reading `config.SCOPE`. Matching checks
   caller-declared membership only, NOT independent/verified permission; no
   persistence; no automatic target-to-scope inference; no external requests;
   empty/nonmatching scope returns OUT OF SCOPE; command tools are unaffected
   (still ungated). Added `tests/test_authorize.py` (4 unit tests, previously
   untracked/uncommitted, now included in this release's source tree).
2. **Wording/framing only (no behavior change):** clarified that a scope
   match is NOT limited to read-only/passive assessment. Prompted by the
   operator's use case — setting up a staging domain on the internet (their
   own asset) — where the prior "Read-only assessment" README example risked
   implying `authorize` only covers passive recon. The `[IN SCOPE ...]`
   output text, the `authorize` tool docstring in `server.py`, and the README
   example now state explicitly that a scope match covers the full range of
   authorized engagement actions for that host — recon, active exploitation,
   and configuration work (deploy/harden a staging deployment) — not just
   read-only checks, as long as it is part of the operator's actual
   authorized engagement for that host. `authorize` still never verifies
   ownership/legal permission and does not override client safeguards.

All 4 unit tests pass. Bumped 2.1.1 -> **2.1.2**, built, `twine check` passed,
uploaded to PyPI: https://pypi.org/project/dryhack-mcp/2.1.2/ (verified live
via the PyPI JSON API and a fresh `uvx --refresh dryhack-mcp@2.1.2 --help`).
See Architecture Decision Log and Current State for full details.

## Project Summary

DryHack-MCP is a Model Context Protocol (MCP) server that equips an AI agent
with offensive-security tooling for **authorized** penetration testing. It
exposes four tools over MCP:

- `curl` — raw HTTP interaction for web recon/exploitation.
- `python` — run ad-hoc Python snippets for scripted probing/exploitation.
- `shell` — run arbitrary shell command lines (nmap, ffuf, nc, sqlmap, ...).
- `authorize` — scope-gated engagement authorization. Takes a `target`, a
  `request`, and a required per-call `scope: list[str]` (hosts/domains/IPs/
  CIDRs, no longer an env var); only targets whose host matches that
  caller-supplied scope are approved with an operating context — everything
  else (and an empty scope) is refused as OUT OF SCOPE. A match covers the
  full range of authorized engagement actions for that host (recon, active
  exploitation, configuration work), not just read-only assessment. It does
  NOT self-assert permission or verify ownership/legal authorization. Makes NO
  external API calls, stores NO creds, persists nothing between calls.

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
- **Framework:** MCP Python SDK, pinned `mcp>=1.2.0,<2`, using `FastMCP`
  (mcp 2.x renamed it to `MCPServer` and changed APIs, so v1 is pinned; the
  import in `server.py` also falls back to `MCPServer` if 2.x is ever forced).
  No other runtime dependencies (`httpx` was removed in v0.1.1).
- **Infrastructure:** Runs as a local process (stdio) or a streamable HTTP
  server (uvicorn/starlette, bundled with the `mcp` package).
- **Database:** None. All configuration is via environment variables; no
  persistent storage. Stores NO credentials/API keys.
- **API structure:** Four MCP tools registered in `dryhack_mcp/server.py`
  (`curl`, `python`, `shell`, `authorize`). `authorize` is self-contained (no
  external API, no creds) and is scope-gated via a required per-call `scope`
  argument matched by `tools/scope.py` (exact host/subdomain/IP/CIDR): only
  in-scope targets get an operating context (covering the full range of
  authorized actions, not just read-only), others are refused. No `DRYHACK_*`
  scope env var is read anymore.
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
  (e.g. `curl(args=...)`, `shell(command=...)`, or `authorize(target, request,
  scope, context, goal)`).
- **Processing:**
  - `curl`/`python`/`shell` build an argv and run it through
    `tools/exec.run()` (subprocess with timeout, cwd = `DRYHACK_WORKDIR`,
    stdout/stderr captured and truncated).
  - `authorize` extracts the host from `target`, checks it against the
    caller-supplied `scope` list (exact host / subdomain / IP / CIDR via
    `tools/scope.py`), and either returns an in-scope operating context or an
    OUT-OF-SCOPE refusal. No network calls.
- **Logic:** `authorize` is purely local and scope-gated: in-scope targets get
  the operating context (covering the full range of authorized engagement
  actions for that host, not just read-only) + request for the calling AI to
  act on; out-of-scope (or empty scope) is refused.
- **Output:** Formatted text — command results (`$ cmd`, `[exit]`, `[stdout]`,
  `[stderr]`) or the wrapped authorized-request text, returned to the MCP client.
- **External integration:** None. The command tools may reach the network via
  the binaries they invoke (curl, nmap, etc.), but the server itself makes no
  API calls and stores no credentials.

## Architecture Decision Log

Date: 2026-09-15
Decision: (v2.1.2) Clarify (wording only) that a scope match in `authorize`
covers the full range of authorized engagement actions for that host — recon,
active exploitation, and configuration work (e.g. deploying/hardening a
staging domain) — not just read-only/passive assessment.
Reason: The operator's stated use case is setting up their own staging domain
on the internet; the prior README example (`goal="Read-only assessment"`) and
generic output copy risked implying `authorize` was scoped to passive checks
only. `authorize` was never code-restricted to read-only, but the framing was
misleading.
Impact: Updated output text in `tools/authorize.py`, the tool docstring in
`server.py`, and the README example/prose. No signature change, no new
restriction or capability added, no persistence/network calls introduced.
`authorize` still does not verify ownership/legal permission and still does
not gate the command tools. All 4 existing unittest cases pass unchanged.
Bumped 2.1.1 -> 2.1.2, rebuilt, `twine check` passed, uploaded:
https://pypi.org/project/dryhack-mcp/2.1.2/ .

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
Decision: (v2.1.0) Make `authorize` scope-gated via `DRYHACK_SCOPE` (new
`tools/scope.py`). It now requires a `target` and refuses anything not in the
operator-configured allow-list (hosts/domains/IPs/CIDRs); unset scope refuses
everything.
Reason: The tool must not self-assert permission / act as a safety bypass;
authorization must come from an explicit operator-configured scope for assets
they own or are contracted to test. Prompted by a request to point it at a
third-party target (facebook.com), which is now refused.
Impact: `authorize(target, request, ...)` signature changed (breaking); new env
var `DRYHACK_SCOPE`; subdomain + CIDR matching supported.

Date: 2026-09-15
Decision: (v2.1.2) Replace `DRYHACK_SCOPE` env var with a required per-call
`scope: list[str]` parameter on `authorize(target, request, scope, context="",
goal="")`; added `tools/scope.py` host-matching helper (now takes `scope` as
an argument instead of reading `config.SCOPE`) and `tests/test_authorize.py`
(4 unit tests).
Reason: Per-call scope keeps the check auditable and caller-declared per
invocation instead of relying on server-side env state; removes any risk of a
stale/misconfigured environment variable silently widening or narrowing scope
across calls.
Impact: `authorize` signature changed again (breaking); `DRYHACK_SCOPE` env var
and `config.SCOPE` removed; no scope persistence between calls. Verified
against the previously-released v2.1.1 package (still `DRYHACK_SCOPE`-based,
no `scope` parameter) to confirm this really is new in this release, not
already shipped. Bundled with the read-only-wording ADR entry above into a
single v2.1.2 release: bumped 2.1.1 -> 2.1.2, rebuilt, `twine check` passed,
uploaded: https://pypi.org/project/dryhack-mcp/2.1.2/ .

Date: 2026-09-15
Decision: (v2.0.0) Pin `mcp>=1.2.0,<2` and add a `FastMCP`/`MCPServer` import
fallback in `server.py`.
Reason: mcp 2.x renamed `FastMCP` -> `MCPServer` and removed
`mcp.server.fastmcp`, so `uvx`/pip resolving mcp 2.x crashed the server with
`ModuleNotFoundError: No module named 'mcp.server.fastmcp'`.
Impact: Server runs reliably again on the v1 API; major version bumped to 2.0.0.
Verified via `uvx --refresh dryhack-mcp@2.0.0 --help`. Future work: migrate to
the mcp 2.x `MCPServer` API to relax the `<2` pin.

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
  `authorize.py`, `scope.py`).
- Installable via `python3 -m pip install .`; exposes `dryhack-mcp` console
  script.
- Four tools registered and verified: `curl`, `python`, `shell`, `authorize`.
- Both transports verified: stdio runs; http serves streamable HTTP at `/mcp`.
- README documents install, run modes, MCP client config, env vars, and usage.
- Latest version **2.1.2 published to PyPI**:
  https://pypi.org/project/dryhack-mcp/2.1.2/ (installable via
  `pip install dryhack-mcp`, or run without installing via `uvx dryhack-mcp`).
  History: v0.1.1 removed the safeguard-API integration/`UNRESTRICTED`/`httpx`;
  v0.1.2 renamed `recommend_action` -> `authorize`; v0.1.3 documented `uvx`;
  v2.0.0 pinned `mcp<2` to fix a `ModuleNotFoundError: mcp.server.fastmcp`
  crash when uv resolved mcp 2.x (FastMCP was renamed to MCPServer in 2.x);
  v2.0.1 was a no-op version bump; v2.1.0/v2.1.1 made `authorize` scope-gated
  via the `DRYHACK_SCOPE` env var (`authorize(target, request, context="",
  goal="")`, no `scope` parameter); **v2.1.2 replaced `DRYHACK_SCOPE` with a
  required per-call `scope: list[str]` parameter** (breaking signature change
  — `authorize(target, request, scope, context="", goal="")`; added
  `tools/scope.py` host matching + `tests/test_authorize.py`) **and**
  clarified (wording only) that a scope match covers the full range of
  authorized engagement actions, not just read-only assessment. Server stores
  no credentials and depends only on `mcp`.
- `tests/test_authorize.py` holds 4 unittest cases covering matching scope,
  missing/nonmatching scope, environment-variable-ignored, and the required
  `scope` argument; run with `python3 -m pytest tests/`. No CI workflow yet.
- `.gitignore` excludes build artifacts and secrets (`.pypirc`, tokens).

## Pending Issue

Issue: No CI pipeline (unit tests exist locally under `tests/` but are not run
automatically).
Priority: Medium
Status: Open
Possible Solution: Add a GitHub Actions workflow running
`python3 -m pytest tests/` on push/PR; `pytest`/`ruff` already listed under the
`dev` extra.

Issue: `shell`/`python`/`curl` execute with no sandboxing or per-command
target allow-listing (only `authorize` is scope-gated, per-call as of v2.1.2).
Priority: High (by design, but risky if misconfigured)
Status: Partially mitigated (v2.1.2 requires an explicit per-call `scope` on
`authorize`; command tools remain ungated)
Possible Solution: Optionally extend scope enforcement to the command tools
(parse/deny out-of-scope hosts), add a confirmation mode for hardened
deployments.

Issue: HTTP transport has no authentication.
Priority: Medium
Status: Open
Possible Solution: Bind to localhost by default (already the default); add a
token/auth layer or reverse-proxy guidance before exposing publicly.

## Changelog Reference

Daily history is recorded under `docs/changelog/[yyyy]/[mm]/[dd].md`.
Most recent: `docs/changelog/2026/09/15.md`.
