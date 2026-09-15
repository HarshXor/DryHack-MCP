"""Match targets against caller-supplied scope; does not verify permission."""
from __future__ import annotations

import ipaddress
from typing import Optional, Tuple
from urllib.parse import urlparse



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


def check(target: str, scope: list[str]) -> Tuple[bool, Optional[str], str]:
    """Return (in_scope, host, reason)."""
    host = extract_host(target)
    if not host:
        return (False, None, "could not parse a host from the target")
    if not scope:
        return (
            False,
            host,
            "no scope supplied — pass scope containing hosts/domains/CIDRs "
            "you are explicitly authorized to test",
        )
    for entry in scope:
        if _matches(host, entry):
            return (True, host, entry)
    return (False, host, "host is not in the caller-supplied scope")
