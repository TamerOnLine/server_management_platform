#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
from datetime import datetime
from pathlib import Path


def log(msg: str) -> None:
    print(msg)


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    dry_run: bool = False,
) -> subprocess.CompletedProcess | None:
    cmd_str = " ".join(shlex.quote(c) for c in cmd)
    if dry_run:
        log(f"[DRY-RUN] {cmd_str}")
        return None
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check, text=True)


def run_as_user(
    cmd: list[str],
    *,
    user: str,
    cwd: Path | None = None,
    check: bool = True,
    dry_run: bool = False,
) -> subprocess.CompletedProcess | None:
    """
    Run a command as a specific user (useful when this script runs as root).
    """
    return run(["sudo", "-u", user, *cmd], cwd=cwd, check=check, dry_run=dry_run)


def must_be_root() -> None:
    if os.geteuid() != 0:
        raise SystemExit("Please run as root (sudo).")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def ensure_dir(p: Path, dry_run: bool) -> None:
    if dry_run:
        log(f"[DRY-RUN] mkdir -p {p}")
        return
    p.mkdir(parents=True, exist_ok=True)


def rsync_dir(src: Path, dst: Path, dry_run: bool) -> None:
    # rsync trailing slash semantics: src/ -> dst/
    run(
        ["rsync", "-av", f"{src.as_posix().rstrip('/')}/", f"{dst.as_posix().rstrip('/')}/"],
        dry_run=dry_run,
    )


def backup_dir(path: Path, backup_root: Path, label: str, dry_run: bool) -> Path:
    """
    Backup existing directory to backup_root/<label>/ (rsync copy).
    Returns backup destination path.
    """
    dest = backup_root / label
    ensure_dir(dest, dry_run=dry_run)
    if path.exists():
        log(f"🛟 Backup: {path} -> {dest}")
        rsync_dir(path, dest, dry_run=dry_run)
    else:
        log(f"ℹ️ Nothing to backup (missing): {path}")
    return dest


def restore_dir(backup_src: Path, target_dst: Path, dry_run: bool) -> None:
    """
    Restore from backup_src/ into target_dst/
    """
    log(f"↩️ Restore: {backup_src} -> {target_dst}")
    ensure_dir(target_dst, dry_run=dry_run)
    rsync_dir(backup_src, target_dst, dry_run=dry_run)


def chmod_bin_dir(bin_dir: Path, dry_run: bool) -> None:
    if dry_run:
        log(f"[DRY-RUN] chmod +x {bin_dir}/*")
        return
    for p in bin_dir.iterdir():
        if p.is_file() and not p.is_symlink():
            mode = p.stat().st_mode
            p.chmod(mode | 0o111)


def nginx_test(dry_run: bool) -> bool:
    cp = run(["nginx", "-t"], check=False, dry_run=dry_run)
    if dry_run:
        return True
    return bool(cp and cp.returncode == 0)


def main() -> None:
    p = argparse.ArgumentParser(description="Safe deploy for pi-node-server-infra (backup + rollback).")
    p.add_argument("--repo-dir", default="/srv/pi-node-server-infra", help="Path to infra repo on server")
    p.add_argument("--branch", default="main", help="Git branch to pull")
    p.add_argument("--remote", default="origin", help="Git remote name")
    p.add_argument("--no-chmod", action="store_true", help="Skip chmod +x for /usr/local/bin")
    p.add_argument("--no-backup", action="store_true", help="Skip backups (not recommended)")
    p.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    args = p.parse_args()

    must_be_root()

    repo_dir = Path(args.repo_dir).resolve()
    if not repo_dir.exists():
        raise SystemExit(f"[ERROR] Repo dir not found: {repo_dir}")

    # Sync sources (from repo)
    src_sites = repo_dir / "nginx" / "sites-available"
    src_snips = repo_dir / "nginx" / "snippets"
    src_systemd = repo_dir / "systemd"
    src_scripts = repo_dir / "scripts"

    # Sync targets
    dst_sites = Path("/etc/nginx/sites-available")
    dst_snips = Path("/etc/nginx/snippets")
    dst_systemd = Path("/etc/systemd/system")
    dst_bin = Path("/usr/local/bin")

    # Backup root
    backup_root = Path("/var/backups/pi-node-server-infra") / timestamp()

    # ----------------------------
    # Git pull (ALWAYS non-root)
    # ----------------------------
    log("📦 Pull latest infra from Git...")

    pull_user = os.environ.get("SUDO_USER") or "tamer"
    # Always run git pull as a non-root user to use that user's SSH keys
    run_as_user(
        ["git", "pull", args.remote, args.branch],
        user=pull_user,
        cwd=repo_dir,
        dry_run=args.dry_run,
    )

    # Backups
    if not args.no_backup:
        log(f"🛟 Creating backups at: {backup_root}")
        ensure_dir(backup_root, dry_run=args.dry_run)

        backup_dir(dst_sites, backup_root, "etc/nginx/sites-available", args.dry_run)
        backup_dir(dst_snips, backup_root, "etc/nginx/snippets", args.dry_run)
        backup_dir(dst_systemd, backup_root, "etc/systemd/system", args.dry_run)
        backup_dir(dst_bin, backup_root, "usr/local/bin", args.dry_run)

    # Sync
    log("🧩 Sync nginx sites and snippets...")
    rsync_dir(src_sites, dst_sites, dry_run=args.dry_run)
    rsync_dir(src_snips, dst_snips, dry_run=args.dry_run)

    log("🧩 Sync systemd units...")
    rsync_dir(src_systemd, dst_systemd, dry_run=args.dry_run)

    log("🧩 Sync helper scripts...")
    rsync_dir(src_scripts, dst_bin, dry_run=args.dry_run)

    if not args.no_chmod:
        log("🔐 chmod +x on /usr/local/bin/* ...")
        chmod_bin_dir(dst_bin, dry_run=args.dry_run)
    else:
        log("ℹ️ Skipping chmod (--no-chmod).")

    log("🔁 Reload systemd...")
    run(["systemctl", "daemon-reload"], dry_run=args.dry_run)

    log("🔎 Testing nginx config (nginx -t)...")
    ok = nginx_test(dry_run=args.dry_run)

    if not ok:
        log("❌ nginx -t FAILED.")
        if args.no_backup:
            raise SystemExit("Rollback is disabled (--no-backup). Fix nginx config manually.")

        log("↩️ Rolling back from backups...")
        restore_dir(backup_root / "etc/nginx/sites-available", dst_sites, dry_run=args.dry_run)
        restore_dir(backup_root / "etc/nginx/snippets", dst_snips, dry_run=args.dry_run)
        restore_dir(backup_root / "etc/systemd/system", dst_systemd, dry_run=args.dry_run)
        restore_dir(backup_root / "usr/local/bin", dst_bin, dry_run=args.dry_run)

        run(["systemctl", "daemon-reload"], dry_run=args.dry_run)

        if not nginx_test(dry_run=args.dry_run):
            raise SystemExit("Rollback done, but nginx -t still fails. Please inspect nginx config.")
        log("✅ Rollback successful (nginx -t OK).")
        raise SystemExit("Deployment aborted due to nginx test failure (but rollback succeeded).")

    log("✅ nginx -t OK. Reloading nginx...")
    run(["systemctl", "reload", "nginx"], dry_run=args.dry_run)

    log("✅ Deploy finished successfully.")
    if not args.no_backup:
        log(f"🛟 Backups stored at: {backup_root}")


if __name__ == "__main__":
    main()
