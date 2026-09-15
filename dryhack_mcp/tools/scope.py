"""Scope enforcement: only operator-authorized targets are permitted.

Authorization is defined by the operator via the DRYHACK_SCOPE environment
variable (see config.SCOPE) — a list of hosts, domains, IPs, or CIDRs the
operator has explicit written permission to test. Anything not matched is
treated as OUT OF SCOPE. This is what makes `authorize` a real guardrail
instead of a self-asserted claim.
"""
from __future__ import annotations

import ipaddress
from typing import Optional, Tuple
from urllib.parse import urlparse

from .. import config


def extract_host(target: str) -> Optional[str]:
    """Best-effort extraction of a hostname/IP from a URL or host[:port]."""
    t = (target or "").strip()
    if not t:
        return None
    parsed = urlparse(t if "://" in t else "//" + t)
    netloc = parsed.netloc or parsed.path
    host = netloc.split("@")[-1]  # strip userinfo
    if host.startswith("["):  # bracketed IPv6
        host = host[1:].split("]")[0]
    else:
        host = host.split(":")[0]  # strip port
    return host.lower() or None


def _matches(host: str, entry: str) -> bool:
    entry = entry.lower().strip()
    if not entry:
        return False
    # IP / CIDR entries
    try:
        net = ipaddress.ip_network(entry, strict=False)
        try:
            return ipaddress.ip_address(host) in net
        except ValueError:
            return False
    except ValueError:
        pass
    # domain / host entries (exact or subdomain)
    return host == entry or host.endswith("." + entry)


def check(target: str) -> Tuple[bool, Optional[str], str]:
    """Return (in_scope, host, reason)."""
    host = extract_host(target)
    if not host:
        return (False, None, "could not parse a host from the target")
    if not config.SCOPE:
        return (
            False,
            host,
            "no scope configured — set DRYHACK_SCOPE to the hosts/domains/CIDRs "
            "you are explicitly authorized to test",
        )
    for entry in config.SCOPE:
        if _matches(host, entry):
            return (True, host, entry)
    return (False, host, "host is not in the operator-configured scope")
