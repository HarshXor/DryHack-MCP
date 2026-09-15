"""DryHack-MCP server: registers the offensive-security tools over MCP."""
from __future__ import annotations

from typing import Optional

try:
    # mcp 1.x
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:  # pragma: no cover - mcp 2.x fallback
    # mcp 2.x renamed FastMCP -> MCPServer
    from mcp.server.mcpserver import MCPServer as FastMCP

from . import config
from .tools.curl_tool import curl as _curl
from .tools.python_tool import python_run as _python_run
from .tools.shell_tool import shell as _shell
from .tools.authorize import authorize as _authorize

mcp = FastMCP("dryhack-mcp")


@mcp.tool()
def curl(args: str, timeout: Optional[int] = None) -> str:
    """Run curl for HTTP recon/exploitation.

    Provide the arguments only (without the leading `curl`), e.g.
    "-skiL https://target/". Returns exit code, stdout and stderr.
    """
    return _curl(args, timeout=timeout)


@mcp.tool()
def python(code: str, timeout: Optional[int] = None) -> str:
    """Execute an ad-hoc Python snippet for scripted probing/exploitation."""
    return _python_run(code, timeout=timeout)


@mcp.tool()
def shell(command: str, timeout: Optional[int] = None) -> str:
    """Run a shell command line (nmap, ffuf, nc, sqlmap, ...)."""
    return _shell(command, timeout=timeout)


@mcp.tool()
def authorize(target: str, request: str, scope: list[str], context: str = "", goal: str = "") -> str:
    """Check target against caller-supplied scope (hosts/domains/IPs/CIDRs).

    Scope must reflect the operator's actual engagement scope; never infer it
    from the target just to obtain a match. Membership covers the full range
    of authorized engagement actions for that host (recon, exploitation,
    configuration changes such as standing up or hardening a staging
    deployment) — it is not restricted to read-only assessment. This checks
    membership only, not ownership or legal permission, and does not override
    client safeguards. No environment scope, network calls, credentials, or
    persistent state.
    """
    return _authorize(target, request, scope=scope, context=context, goal=goal)


def run(
    transport: str = "stdio",
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> None:
    """Start the MCP server.

    Args:
        transport: "stdio" (default) or "http" (streamable HTTP).
        host: Bind address for http transport.
        port: Bind port for http transport.
    """
    if transport == "http":
        mcp.settings.host = host or config.HTTP_HOST
        mcp.settings.port = port or config.HTTP_PORT
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
