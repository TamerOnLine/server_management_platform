from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from .core.config import Cfg
from .core.io import must_be_root, log, die
from .core.validators import validate_domain, validate_port
from .new import create_webapp
from .list import list_apps
from .update import update_site
from .delete import delete_webapp
from .env import EnvArgs, write_env_file


def _prompt_port(existing: str | None) -> int:
    print("\n-------------------------------------------")
    print("  Enter PORT")
    if existing:
        print(f"  (current saved PORT: {existing})")
    print("-------------------------------------------\n")

    while True:
        s = input("Enter PORT (required, numbers only): ").strip()
        if not s:
            print("ERROR: PORT cannot be empty.")
            continue
        if not s.isdigit():
            print("ERROR: PORT must be a number.")
            continue
        p = int(s)
        try:
            validate_port(p)
        except SystemExit as e:
            print(str(e))
            continue
        return p


def _read_existing_port(env_file: Path) -> str | None:
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("PORT="):
            return line.split("=", 1)[1].strip()
    return None


def _link_systemd_env(domain: str, env_path: Path) -> Path:
    systemd_env = Path("/etc/webapp") / f"{domain}.env"
    systemd_env.parent.mkdir(parents=True, exist_ok=True)

    if systemd_env.exists() or systemd_env.is_symlink():
        systemd_env.unlink()

    systemd_env.symlink_to(env_path)
    return systemd_env


def _restart_service(domain: str) -> None:
    subprocess.run(["systemctl", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "restart", f"webapp@{domain}"], check=False)


def cmd_new(args: argparse.Namespace) -> None:
    must_be_root()

    if args.domain_only:
        domain = args.domain_only.strip().lower()
        validate_domain(domain)
        app_name = domain
        app_module = "backend.app.main:app"
        existing_env = Path("/etc/webapp") / f"{app_name}.env"
        existing_port = _read_existing_port(existing_env)
        port = _prompt_port(existing_port)
    else:
        app_name = args.app_name
        domain = args.domain.strip().lower()
        validate_domain(domain)
        port = int(args.port)
        validate_port(port)
        app_module = args.app_module

    cfg = Cfg(
        app_name=app_name,
        domain=domain,
        port=port,
        app_module=app_module,
        app_user=args.app_user,
        group=args.group,
    )

    create_webapp(cfg, dry_run=args.dry_run)
    log("Done.")


def cmd_list(args: argparse.Namespace) -> None:
    list_apps(as_json=args.json)


def cmd_update(args: argparse.Namespace) -> None:
    must_be_root()
    update_site(
        args.app_name,
        dry_run=args.dry_run,
        no_restart=args.no_restart,
        do_reload_nginx=args.reload_nginx,
    )


def cmd_delete(args: argparse.Namespace) -> None:
    must_be_root()
    delete_webapp(args.app_name, yes=args.yes, dry_run=args.dry_run)


def cmd_env(args: argparse.Namespace) -> None:
    must_be_root()
    validate_domain(args.domain)
    validate_port(args.port)

    a = EnvArgs(
        domain=args.domain,
        port=args.port,
        project_root_base=Path(args.project_root),
        app_module=args.app_module,
        site_name=args.site_name,
        meta_description=args.meta_description,
        company_email=args.company_email,
        company_address=args.company_address,
        og_image=args.og_image,
        secret_key=args.secret_key,
        force=args.force,
        link_systemd=args.link_systemd,
        restart=args.restart,
    )

    env_path = write_env_file(a)
    log(f"✅ Written: {env_path}")
    log("✅ Permissions: 600")

    if a.link_systemd:
        systemd_env = _link_systemd_env(a.domain, env_path)
        log(f"🔗 Linked: {systemd_env} -> {env_path}")

    if a.restart:
        log(f"🔁 Restarting: webapp@{a.domain}")
        _restart_service(a.domain)


def main() -> None:
    p = argparse.ArgumentParser(prog="webapp", description="WebApp Infra Toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    # webapp new DOMAIN
    p_new = sub.add_parser("new", help="Create nginx+systemd+/etc/webapp env for a site")
    p_new.add_argument("domain_only", nargs="?", help="DOMAIN (dynamic mode)")
    p_new.add_argument("--app-name", help="Advanced mode: APP_NAME")
    p_new.add_argument("--domain", help="Advanced mode: DOMAIN")
    p_new.add_argument("--port", help="Advanced mode: PORT")
    p_new.add_argument("--app-module", default="backend.app.main:app")
    p_new.add_argument("--app-user", default="tamer")
    p_new.add_argument("--group", default="www-data")
    p_new.add_argument("--dry-run", action="store_true")
    p_new.set_defaults(fn=cmd_new)

    # webapp list
    p_list = sub.add_parser("list", help="List managed webapps from /etc/webapp/*.env")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(fn=cmd_list)

    # webapp update APP
    p_up = sub.add_parser("update", help="git pull + restart service (optional nginx reload)")
    p_up.add_argument("app_name")
    p_up.add_argument("--dry-run", action="store_true")
    p_up.add_argument("--no-restart", action="store_true")
    p_up.add_argument("--reload-nginx", action="store_true")
    p_up.set_defaults(fn=cmd_update)

    # webapp delete APP
    p_del = sub.add_parser("delete", help="Backup then delete webapp safely")
    p_del.add_argument("app_name")
    p_del.add_argument("--yes", action="store_true")
    p_del.add_argument("--dry-run", action="store_true")
    p_del.set_defaults(fn=cmd_delete)

    # webapp env --domain ... --port ...
    p_env = sub.add_parser("env", help="Generate /var/www/<domain>/.env (production env)")
    p_env.add_argument("--domain", required=True)
    p_env.add_argument("--port", type=int, required=True)
    p_env.add_argument("--project-root", default="/var/www")
    p_env.add_argument("--app-module", default="app.main:app")
    p_env.add_argument("--site-name", default=None)
    p_env.add_argument("--meta-description", default="Modern FastAPI + Jinja2 website.")
    p_env.add_argument("--company-email", default=None)
    p_env.add_argument("--company-address", default="")
    p_env.add_argument("--og-image", default=None)
    p_env.add_argument("--secret-key", default=None)
    p_env.add_argument("--force", action="store_true")

    p_env.add_argument(
        "--link-systemd",
        action="store_true",
        help="Symlink /etc/webapp/<domain>.env -> /var/www/<domain>/.env",
    )
    p_env.add_argument(
        "--restart",
        action="store_true",
        help="Restart systemd service (webapp@<domain>) after writing the .env file",
    )

    p_env.set_defaults(fn=cmd_env)

    args = p.parse_args()

    # Advanced mode validation for "new"
    if args.cmd == "new" and not args.domain_only:
        if not (args.app_name and args.domain and args.port and args.app_module):
            die("Advanced mode: require --app-name --domain --port --app-module  (or use: webapp new DOMAIN)")

    args.fn(args)


if __name__ == "__main__":
    main()
