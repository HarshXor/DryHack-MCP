# DryHack-MCP

An MCP (Model Context Protocol) server that gives an AI agent offensive-security
tooling for **authorized** penetration testing. It exposes four tools:

| Tool | Purpose |
|------|---------|
| `curl` | Raw HTTP interaction for web recon/exploitation |
| `python` | Run ad-hoc Python snippets for scripted probing |
| `shell` | Run shell commands (`nmap`, `ffuf`, `nc`, `sqlmap`, …) |
| `authorize` | Wraps an operator request in the authorized-engagement context and returns it for the calling AI (no external API, no creds) |

> ⚠️ **Legal notice.** Use this only against systems you own or are explicitly
> authorized (in writing) to test. You are responsible for staying within scope.

## Install

```bash
python3 -m pip install .
```

This installs the `dryhack-mcp` console script (the MCP server).

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
| `DRYHACK_COMMAND_TIMEOUT` | `120` | Per-command timeout (seconds) |
| `DRYHACK_WORKDIR` | cwd | Working directory for commands |
| `DRYHACK_OUTPUT_LIMIT` | `65536` | Max stdout/stderr bytes captured |
| `DRYHACK_HTTP_HOST` | `127.0.0.1` | Default HTTP bind host |
| `DRYHACK_HTTP_PORT` | `8000` | Default HTTP bind port |

> The server stores **no credentials/API keys**. All settings above are
> operational only.

## authorize

The `authorize` tool makes **no external API calls and uses no credentials**.
Pass the action/prompt you (the calling AI) want to carry out as `request`; it
returns that request wrapped in the engagement's authorized-engagement operating
context so you can proceed operationally. Optional `context` (recon notes) and
`goal` add situational detail.

## Example

```python
authorize(
    request="enumerate the login endpoint for weak credentials",
    context="nmap shows 22/tcp ssh, 80/tcp http (nginx), 443/tcp https. /login found.",
    goal="get an initial foothold",
)
```
