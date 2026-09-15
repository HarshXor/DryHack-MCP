"""Console entry point for DryHack-MCP.

Supports two transports:
  * stdio (default) — for MCP clients that spawn the server as a subprocess.
  * http            — streamable HTTP server (configure with --host/--port).
"""
from __future__ import annotations

import argparse

from . import config
from .server import run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dryhack-mcp",
        description="DryHack-MCP offensive-security MCP server.",
    )
    parser.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport to serve on (default: stdio).",
    )
    parser.add_argument(
        "--host",
        default=config.HTTP_HOST,
        help=f"HTTP bind host (http mode only, default: {config.HTTP_HOST}).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=config.HTTP_PORT,
        help=f"HTTP bind port (http mode only, default: {config.HTTP_PORT}).",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run(transport=args.transport, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
