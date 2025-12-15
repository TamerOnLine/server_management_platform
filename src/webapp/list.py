from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

ETC_WEBAPP = Path("/etc/webapp")
NGINX_AVAIL = Path("/etc/nginx/sites-available")
NGINX_ENABLED = Path("/etc/nginx/sites-enabled")


def _run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return p.returncode, (p.stdout or "").strip()


def systemd_state(service: str) -> tuple[str, str]:
    rc_a, out_a = _run(["systemctl", "is-active", service])
    rc_e, out_e = _run(["systemctl", "is-enabled", service])
    return (
        out_a if rc_a == 0 else "inactive",
        out_e if rc_e == 0 else "disabled",
    )


def parse_env(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


@dataclass
class WebApp:
    app: str
    domain: str
    port: Optional[int]
    systemd: str
    nginx: str
    env_file: str


def build_app(env_file: Path) -> WebApp:
    env = parse_env(env_file)
    app = env.get("APP_NAME", env_file.stem)
    domain = env.get("SERVER_NAME", app)
    port = int(env["PORT"]) if env.get("PORT", "").isdigit() else None

    active, enabled = systemd_state(f"webapp@{app}.service")
    nginx = f"{'avail' if (NGINX_AVAIL / app).exists() else '-'}|" \
            f"{'en' if (NGINX_ENABLED / app).exists() else '-'}"

    return WebApp(app=app, domain=domain, port=port, systemd=f"{active}/{enabled}", nginx=nginx, env_file=str(env_file))


def print_table(apps: list[WebApp]) -> None:
    print(f"{'APP':15} {'DOMAIN':30} {'PORT':6} {'SYSTEMD':20} {'NGINX'}")
    print("-" * 85)
    for a in apps:
        print(f"{a.app:15} {a.domain:30} {a.port or '':6} {a.systemd:20} {a.nginx}")


def list_apps(as_json: bool = False) -> None:
    apps = [build_app(p) for p in ETC_WEBAPP.glob("*.env")]
    apps.sort(key=lambda a: a.app)

    if as_json:
        print(json.dumps([asdict(a) for a in apps], indent=2))
    else:
        print_table(apps)
