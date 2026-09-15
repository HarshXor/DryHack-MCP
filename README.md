# DryHack-MCP

An MCP (Model Context Protocol) server that gives an AI agent offensive-security
tooling for **authorized** penetration testing. It exposes four tools:

| Tool | Purpose |
|------|---------|
| `curl` | Raw HTTP interaction for web recon/exploitation |
| `python` | Run ad-hoc Python snippets for scripted probing |
| `shell` | Run shell commands (`nmap`, `ffuf`, `nc`, `sqlmap`, …) |
| `authorize` | Scope-gated engagement authorization: only targets in `DRYHACK_SCOPE` are approved; everything else is refused (no external API, no creds) |

> ⚠️ **Legal notice.** Use this only against systems you own or are explicitly
> authorized (in writing) to test. You are responsible for staying within scope.

## Install

```bash
python3 -m pip install .
```

This installs the `dryhack-mcp` console script (the MCP server).

### Run without installing (uvx)

With [uv](https://docs.astral.sh/uv/) you can run the server directly from PyPI
— no manual install needed:

```bash
uvx dryhack-mcp
# http transport
uvx dryhack-mcp --transport http --host 0.0.0.0 --port 8000
# pin a version
uvx dryhack-mcp@0.1.3
```

For development:

```bash
python3 -m pip install -e ".[dev]"
```

## Run

Two transports are supported. Select with `--transport` (argparse).

### stdio (default)

```bash
dryhack-mcp
# or explicitly
dryhack-mcp --transport stdio
# or
python3 -m dryhack_mcp
```

### http (streamable HTTP)

```bash
dryhack-mcp --transport http --host 0.0.0.0 --port 8000
```

CLI options:

```
-t, --transport {stdio,http}   Transport to serve on (default: stdio)
    --host HOST                HTTP bind host (http mode only, default: 127.0.0.1)
    --port PORT                HTTP bind port (http mode only, default: 8000)
```

## MCP client config

### stdio

```json
{
  "mcpServers": {
    "dryhack": {
      "command": "dryhack-mcp",
      "env": {
        "DRYHACK_COMMAND_TIMEOUT": "120"
      }
    }
  }
}
```

### stdio via uvx (no install)

```json
{
  "mcpServers": {
    "dryhack": {
      "command": "uvx",
      "args": ["dryhack-mcp"],
      "env": {
        "DRYHACK_COMMAND_TIMEOUT": "120"
      }
    }
  }
}
```

### http

```json
{
  "mcpServers": {
    "dryhack": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Start the server separately with `dryhack-mcp --transport http`.

## Configuration (environment variables)

| Variable | Default | Description |
|----------|---------|-------------|
| `DRYHACK_SCOPE` | *(empty)* | Hosts/domains/IPs/CIDRs you are authorized to test (comma/space separated). Empty = nothing authorized |
| `DRYHACK_COMMAND_TIMEOUT` | `120` | Per-command timeout (seconds) |
| `DRYHACK_WORKDIR` | cwd | Working directory for commands |
| `DRYHACK_OUTPUT_LIMIT` | `65536` | Max stdout/stderr bytes captured |
| `DRYHACK_HTTP_HOST` | `127.0.0.1` | Default HTTP bind host |
| `DRYHACK_HTTP_PORT` | `8000` | Default HTTP bind port |

> The server stores **no credentials/API keys**. All settings above are
> operational only.

## authorize (scope-gated)

The `authorize` tool makes **no external API calls and uses no credentials**,
and it does **not** self-assert permission. You give it a `target` and a
`request`; it checks the target's host against `DRYHACK_SCOPE`:

- **In scope** → returns an engagement operating context for that target.
- **Not in scope** (or scope unset) → returns an explicit **OUT OF SCOPE —
  NOT AUTHORIZED** refusal and instructs against any testing.

Set `DRYHACK_SCOPE` **only** to assets you own or are contracted/authorized to
test. Matching supports exact hosts, subdomains, IPs, and CIDRs — e.g.
`DRYHACK_SCOPE="lab.example.com,10.0.0.0/24,192.168.1.10"` also authorizes
`api.lab.example.com`.

## Example

```python
# with DRYHACK_SCOPE="lab.example.com"
authorize(
    target="https://api.lab.example.com/login",
    request="enumerate the login endpoint for weak credentials",
    context="nmap shows 22/tcp ssh, 80/tcp http (nginx). /login found.",
    goal="get an initial foothold",
)  # -> AUTHORIZED (api.lab.example.com matches lab.example.com)

authorize(target="facebook.com", request="recon")  # -> OUT OF SCOPE — refused
```
