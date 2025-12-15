from __future__ import annotations

import shutil
import tarfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .core.io import log, run, prompt_confirm


@dataclass
class Targets:
    app_name: str
    project_root: Path
    env_file: Path
    service_unit: Path
    nginx_available: Path
    nginx_enabled: Path
    ssl_dir: Path
    backup_base: Path
    workdir: Path
    archive: Path


def build_targets(app_name: str) -> Targets:
    project_root = Path("/var/www") / app_name
    env_file = Path("/etc/webapp") / f"{app_name}.env"
    service_unit = Path("/etc/systemd/system") / f"webapp@{app_name}.service"
    nginx_available = Path("/etc/nginx/sites-available") / app_name
    nginx_enabled = Path("/etc/nginx/sites-enabled") / app_name
    ssl_dir = Path("/etc/ssl") / app_name

    backup_base = Path("/var/backups/sites")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    workdir = backup_base / f"{app_name}-{ts}"
    archive = backup_base / f"{app_name}-{ts}.tar.gz"

    return Targets(
        app_name=app_name,
        project_root=project_root,
        env_file=env_file,
        service_unit=service_unit,
        nginx_available=nginx_available,
        nginx_enabled=nginx_enabled,
        ssl_dir=ssl_dir,
        backup_base=backup_base,
        workdir=workdir,
        archive=archive,
    )


def copy_if_exists(src: Path, dest: Path, dry_run: bool) -> None:
    if not src.exists() and not src.is_symlink():
        log(f"  - Skipping (not found): {src}")
        return

    log(f"  + Backing up {src}")
    if dry_run:
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir() and not src.is_symlink():
        shutil.copytree(src, dest, dirs_exist_ok=True, symlinks=True)
    else:
        if dest.exists():
            dest.unlink()
        shutil.copy2(src, dest, follow_symlinks=False)


def safe_rm(path: Path, dry_run: bool) -> None:
    if not path.exists() and not path.is_symlink():
        log(f"  - Already gone: {path}")
        return

    log(f"  - Removing {path}")
    if dry_run:
        return

    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    else:
        shutil.rmtree(path, ignore_errors=True)


def create_backup(t: Targets, dry_run: bool) -> None:
    log("↪ Creating backup directories...")
    if not dry_run:
        t.workdir.mkdir(parents=True, exist_ok=True)
        t.backup_base.mkdir(parents=True, exist_ok=True)

    log("↪ Collecting files for backup...")
    copy_if_exists(t.project_root, t.workdir / "var/www" / t.app_name, dry_run=dry_run)
    copy_if_exists(t.env_file, t.workdir / "etc/webapp" / f"{t.app_name}.env", dry_run=dry_run)
    copy_if_exists(t.service_unit, t.workdir / "etc/systemd/system" / f"webapp@{t.app_name}.service", dry_run=dry_run)
    copy_if_exists(t.nginx_available, t.workdir / "etc/nginx/sites-available" / t.app_name, dry_run=dry_run)
    copy_if_exists(t.nginx_enabled, t.workdir / "etc/nginx/sites-enabled" / t.app_name, dry_run=dry_run)
    copy_if_exists(t.ssl_dir, t.workdir / "etc/ssl" / t.app_name, dry_run=dry_run)

    log("↪ Creating tar.gz archive...")
    if dry_run:
        log(f"[DRY-RUN] Would create archive: {t.archive}")
        return

    with tarfile.open(t.archive, "w:gz") as tar:
        tar.add(t.workdir, arcname=".")

    log(f"✅ Backup created at: {t.archive}")


def stop_disable_service(app_name: str, dry_run: bool) -> None:
    svc = f"webapp@{app_name}"
    log(f"↪ Stopping service {svc}...")
    run(["systemctl", "stop", svc], check=False, dry_run=dry_run)
    log("↪ Disabling service...")
    run(["systemctl", "disable", svc], check=False, dry_run=dry_run)


def reload_systemd_and_nginx(dry_run: bool) -> None:
    log("↪ Reloading systemd & nginx...")
    run(["systemctl", "daemon-reload"], check=False, dry_run=dry_run)

    cp = run(["nginx", "-t"], check=False, dry_run=dry_run)
    if dry_run:
        run(["systemctl", "reload", "nginx"], check=False, dry_run=True)
        return

    if cp and cp.returncode == 0:
        run(["systemctl", "reload", "nginx"], check=False, dry_run=dry_run)
    else:
        log("⚠️ nginx -t failed. Not reloading nginx.")


def delete_webapp(app_name: str, yes: bool, dry_run: bool) -> None:
    t = build_targets(app_name)

    log("==================================================")
    log("  SAFE DELETE WEBAPP")
    log("==================================================")
    log(f"App Name      : {t.app_name}")
    log(f"Project Root  : {t.project_root}")
    log(f"Env File      : {t.env_file}")
    log(f"Service Unit  : {t.service_unit}")
    log(f"Nginx avail   : {t.nginx_available}")
    log(f"Nginx enabled : {t.nginx_enabled}")
    log(f"SSL dir       : {t.ssl_dir}")
    log("")
    log(f"Backup target : {t.archive}")
    log("==================================================")

    if not yes:
        if not prompt_confirm("Are you sure you want to BACKUP then DELETE this webapp? [y/N] "):
            log("Aborted.")
            return

    create_backup(t, dry_run=dry_run)

    log("")
    log("==================================================")
    log("  DELETING WEBAPP FILES")
    log("==================================================")

    stop_disable_service(t.app_name, dry_run=dry_run)

    safe_rm(t.project_root, dry_run=dry_run)
    safe_rm(t.env_file, dry_run=dry_run)
    safe_rm(t.service_unit, dry_run=dry_run)
    safe_rm(t.nginx_available, dry_run=dry_run)
    safe_rm(t.nginx_enabled, dry_run=dry_run)
    safe_rm(t.ssl_dir, dry_run=dry_run)

    reload_systemd_and_nginx(dry_run=dry_run)

    log("")
    log("✅ DONE.")
    log(f"Backup is stored at: {t.archive}")
    log(f"Inspect: tar -tzf {t.archive}")
