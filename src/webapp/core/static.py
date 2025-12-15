from __future__ import annotations

from pathlib import Path
from .config import Cfg


def detect_static_dir(cfg: Cfg) -> Path | None:
    # Priority:
    # 1) backend/app/static
    # 2) backend/static
    # 3) project_root/static
    p1 = cfg.app_dir / "static"
    p2 = cfg.backend_dir / "static"
    p3 = cfg.project_root / "static"

    if p1.is_dir():
        return p1
    if p2.is_dir():
        return p2
    if p3.is_dir():
        return p3
    return None
