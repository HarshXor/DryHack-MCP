"""DryHack-MCP server: registers the offensive-security tools over MCP."""
from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP

from . import config
from .tools.curl_tool import curl as _curl
from .tools.python_tool import python_run as _python_run
from .tools.shell_tool import shell as _shell
from .tools.recommend import recommend_action as _recommend_action

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
def recommend_action(
    context: str,
    goal: str = "",
    unrestricted: Optional[bool] = None,
    model: Optional[str] = None,
) -> str:
    """Recommend the next offensive action for an authorized engagement.

    Consults the upstream safeguard API (OpenAI-compatible LLM). By default it
    frames the request with an authorized-engagement context so the safeguard
    answers legitimate red-team guidance directly; set `unrestricted=false` to
    query it plainly. Defaults to the DRYHACK_UNRESTRICTED environment setting.
    """
    return _recommend_action(
        context,
        goal=goal,
        unrestricted=unrestricted,
        model=model,
    )


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
