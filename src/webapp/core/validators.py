from __future__ import annotations

import re

from .io import die


_APP_NAME_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}")
_DOMAIN_LABEL_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?")


def validate_app_name(app_name: str) -> None:
    """Reject names that could escape managed configuration directories."""
    if not _APP_NAME_RE.fullmatch(app_name):
        die(
            "APP_NAME must be 1..128 characters and contain only letters, "
            "numbers, dots, underscores, or hyphens."
        )
    if app_name in {".", ".."}:
        die("APP_NAME cannot be '.' or '..'.")


def validate_domain(domain: str) -> None:
    domain = domain.strip().lower()
    if len(domain) > 253:
        die("DOMAIN is too long.")

    labels = domain.split(".")
    if len(labels) < 2 or any(not _DOMAIN_LABEL_RE.fullmatch(label) for label in labels):
        die("DOMAIN looks invalid.")


def validate_port(port: int) -> None:
    if not (1 <= port <= 65535):
        die("PORT must be in range 1..65535.")
