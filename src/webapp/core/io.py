from __future__ import annotations

import os
import shlex
import subprocess
from typing import Optional


def log(msg: str) -> None:
    print(f"[webapp] {msg}")


def die(msg: str) -> None:
    raise SystemExit(f"[ERROR] {msg}")


def is_root() -> bool:
    return os.geteuid() == 0


def must_be_root() -> None:
    if not is_root():
        die("Please run as root (sudo).")


def run(
    cmd: list[str],
    *,
    cwd: Optional[str] = None,
    check: bool = True,
    dry_run: bool = False,
    quiet: bool = False,
) -> subprocess.CompletedProcess | None:
    cmd_str = " ".join(shlex.quote(c) for c in cmd)
    if dry_run:
        log(f"DRY-RUN: {cmd_str}")
        return None

    if not quiet:
        log(cmd_str)

    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def prompt_confirm(prompt: str) -> bool:
    ans = input(prompt).strip().lower()
    return ans in ("y", "yes")
