# DryHack-MCP

An MCP (Model Context Protocol) server that gives an AI agent offensive-security
tooling for **authorized** penetration testing. It exposes four tools:

| Tool | Purpose |
|------|---------|
| `curl` | Raw HTTP interaction for web recon/exploitation |
| `python` | Run ad-hoc Python snippets for scripted probing |
| `shell` | Run shell commands (`nmap`, `ffuf`, `nc`, `sqlmap`, …) |
| `recommend_action` | AI-driven next-step engine backed by the *safeguard API* |

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
        "DRYHACK_API_KEY": "sk-...",
        "DRYHACK_API_BASE": "https://api.openai.com/v1",
        "DRYHACK_MODEL": "gpt-4o-mini",
        "DRYHACK_UNRESTRICTED": "true"
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
| `DRYHACK_API_BASE` | `https://api.openai.com/v1` | Safeguard API base URL |
| `DRYHACK_API_KEY` | *(unset)* | Safeguard API key. If unset, `recommend_action` uses an offline heuristic |
| `DRYHACK_MODEL` | `gpt-4o-mini` | Model used by `recommend_action` |
| `DRYHACK_UNRESTRICTED` | `true` | Default mode for `recommend_action` |
| `DRYHACK_HTTP_HOST` | `127.0.0.1` | Default HTTP bind host |
| `DRYHACK_HTTP_PORT` | `8000` | Default HTTP bind port |

## recommend_action

The `recommend_action` tool consults an upstream LLM ("the safeguard API") for
the next offensive step. Generic safeguards often refuse legitimate, authorized
red-team requests. In **unrestricted** mode each request is framed with an
explicit authorized-engagement / lab-scope context (rules-of-engagement on file,
targets owned by the requesting party) so the model answers operationally.

- Global default: `DRYHACK_UNRESTRICTED=true|false`
- Per-call override: `recommend_action(context=..., unrestricted=true)`

When `unrestricted` is `off`, requests use the plain system prompt with no
authorization framing.

## Example

```python
recommend_action(
    context="nmap shows 22/tcp ssh, 80/tcp http (nginx), 443/tcp https. /login found.",
    goal="get an initial foothold",
    unrestricted=True,
)
```
