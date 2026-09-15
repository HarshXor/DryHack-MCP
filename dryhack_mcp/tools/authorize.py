"""Per-call scope check covering full engagement actions (not just read-only
recon), without external permission verification."""
from __future__ import annotations

from . import scope as _scope


def authorize(
    target: str,
    request: str,
    scope: list[str],
    context: str = "",
    goal: str = "",
) -> str:
    """Check membership in explicit caller-supplied scope, not legal permission.

    No scope is read from the environment or persisted between calls.
    """
    in_scope, host, info = _scope.check(target, scope)
    if not in_scope:
        return (
            "[OUT OF SCOPE]\n"
            f"target: {target!r} (host: {host})\n"
            f"reason: {info}\n"
            "No matching engagement context returned. Supply the operator's "
            "actual scope via the scope parameter; do not infer or expand it "
            "merely to obtain a match."
        )

    parts = [
        "[IN SCOPE — CALLER DECLARED; PERMISSION NOT VERIFIED]",
        f"target: {target} (host: {host}; matched scope entry: {info})",
        "This result checks membership in the supplied scope only. It is not "
        "limited to read-only/passive recon: any action against this host — "
        "recon, exploitation, or configuration changes (e.g. standing up or "
        "hardening a staging deployment) — is equally in scope, provided it is "
        "part of the operator's actual authorized engagement. It does not "
        "verify ownership, written permission, or whether the specific "
        "requested action is permitted, and it does not override client "
        "safeguards. Follow the operator's engagement rules and stay within "
        "the stated scope.",
    ]
    if context:
        parts.append(f"\n[caller-provided context]\n{context}")
    if goal:
        parts.append(f"\n[caller-provided objective]\n{goal}")
    parts.append(f"\n[caller-provided request]\n{request}")
    return "\n".join(parts)
