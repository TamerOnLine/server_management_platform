from __future__ import annotations

import re
from .io import die


def validate_domain(domain: str) -> None:
    domain = domain.strip().lower()
    if not re.fullmatch(r"[a-z0-9.-]+", domain):
        die("DOMAIN contains invalid characters.")
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        die("DOMAIN looks invalid.")


def validate_port(port: int) -> None:
    if not (1 <= port <= 65535):
        die("PORT must be in range 1..65535.")
