from __future__ import annotations

from pathlib import Path

import os
from .core.io import log, die, run

BASE_DIR = Path("/var/www")
SYSTEMD_TEMPLATE = "webapp@{}.service"


def update_git(project_root: Path, dry_run: bool) -> None:
    if not (project_root / ".git").exists():
        die(f"{project_root} is not a git repository")
    log("Updating git repository...")
    owner = os.stat(project_root).st_uid
    run(["sudo", "-u", f"#{owner}", "git", "pull"], cwd=str(project_root), dry_run=dry_run)



def restart_service(app_name: str, dry_run: bool) -> None:
    service = SYSTEMD_TEMPLATE.format(app_name)
    log(f"Restarting systemd service: {service}")
    run(["systemctl", "restart", service], dry_run=dry_run)
    run(["systemctl", "status", service, "--no-pager"], dry_run=dry_run)


def reload_nginx(dry_run: bool) -> None:
    log("Reloading nginx...")
    run(["nginx", "-t"], check=False, dry_run=dry_run)
    run(["systemctl", "reload", "nginx"], check=False, dry_run=dry_run)


def update_site(app_name: str, dry_run: bool, no_restart: bool, do_reload_nginx: bool) -> None:
    project_root = BASE_DIR / app_name
    if not project_root.exists():
        die(f"Project directory not found: {project_root}")

    log(f"Project: {project_root}")
    update_git(project_root, dry_run=dry_run)

    if not no_restart:
        restart_service(app_name, dry_run=dry_run)

    if do_reload_nginx:
        reload_nginx(dry_run=dry_run)

    log("Update completed successfully.")
