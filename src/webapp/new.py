from __future__ import annotations

import os
from pathlib import Path

from .core.config import Cfg
from .core.io import log, run
from .core.static import detect_static_dir


def prepare_directories(cfg: Cfg, dry_run: bool) -> None:
    log(f"Creating project root: {cfg.project_root}")
    if not dry_run:
        cfg.project_root.mkdir(parents=True, exist_ok=True)

    run(["chown", "-R", f"{cfg.app_user}:{cfg.group}", str(cfg.project_root)], dry_run=dry_run)
    run(["chmod", "775", str(cfg.project_root)], dry_run=dry_run)

    log(f"Ensuring {cfg.etc_webapp} exists")
    if not dry_run:
        cfg.etc_webapp.mkdir(parents=True, exist_ok=True)

    log(f"Ensuring SSL dir exists: {cfg.ssl_dir}")
    if not dry_run:
        cfg.ssl_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(cfg.ssl_dir, 0o700)


def write_env_file(cfg: Cfg, static_dir: Path | None, dry_run: bool) -> None:
    log(f"Writing env file: {cfg.env_file}")
    static_str = str(static_dir) if static_dir else ""

    content = "\n".join([
        f"APP_NAME={cfg.app_name}",
        f"APP_USER={cfg.app_user}",
        "",
        f"PROJECT_ROOT={cfg.project_root}",
        f"PYTHONPATH={cfg.project_root}",
        "",
        f"APP_MODULE={cfg.app_module}",
        f"PORT={cfg.port}",
        "",
        f"SERVER_NAME={cfg.domain}",
        f"SERVER_NAME_WWW=www.{cfg.domain}",
        "",
        f"STATIC_DIR={static_str}",
        f"SSL_DIR={cfg.ssl_dir}",
        f"APP_LOG={cfg.project_root}/app.log",
        "",
    ])

    if dry_run:
        log("DRY-RUN: write env content:\n" + content)
        return

    cfg.env_file.write_text(content, encoding="utf-8")
    os.chmod(cfg.env_file, 0o600)
    run(["chown", f"{cfg.app_user}:{cfg.group}", str(cfg.env_file)], dry_run=dry_run)


def write_systemd_service(cfg: Cfg, dry_run: bool) -> None:
    log(f"Writing systemd service: {cfg.systemd_service}")

    service = f"""[Unit]
Description=FastAPI Web App - %i
After=network.target

[Service]
User={cfg.app_user}
Group={cfg.group}

EnvironmentFile={cfg.etc_webapp}/%i.env

WorkingDirectory=/var/www/%i/backend
Environment=PATH=/var/www/%i/{cfg.venv_name}/bin

ExecStart=/var/www/%i/{cfg.venv_name}/bin/uvicorn ${{APP_MODULE}} --host 127.0.0.1 --port ${{PORT}}

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

    if dry_run:
        log("DRY-RUN: write systemd content:\n" + service)
    else:
        cfg.systemd_service.write_text(service, encoding="utf-8")

    run(["systemctl", "daemon-reload"], dry_run=dry_run)
    run(["systemctl", "enable", f"webapp@{cfg.app_name}.service"], dry_run=dry_run)


def write_nginx_config(cfg: Cfg, static_dir: Path | None, dry_run: bool) -> None:
    log(f"Writing Nginx config: {cfg.nginx_available}")

    if static_dir:
        static_block = f"""
    location /static/ {{
        alias {static_dir}/;
        try_files $uri =404;
        access_log off;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }}
"""
    else:
        static_block = """
    # Static files not detected (STATIC_DIR is empty)
    # location /static/ { ... }
"""

    nginx_conf = f"""server {{
    listen 80;
    server_name {cfg.domain} www.{cfg.domain};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {cfg.domain} www.{cfg.domain};

    ssl_certificate     {cfg.ssl_dir}/origin.crt;
    ssl_certificate_key {cfg.ssl_dir}/origin.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
{static_block}
    location / {{
        proxy_pass http://127.0.0.1:{cfg.port};
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}
"""

    if dry_run:
        log("DRY-RUN: write nginx content:\n" + nginx_conf)
        return

    cfg.nginx_available.write_text(nginx_conf, encoding="utf-8")

    if cfg.nginx_enabled_link.exists() or cfg.nginx_enabled_link.is_symlink():
        cfg.nginx_enabled_link.unlink()
    cfg.nginx_enabled_link.symlink_to(cfg.nginx_available)

    run(["nginx", "-t"], dry_run=dry_run)
    run(["systemctl", "reload", "nginx"], dry_run=dry_run)


def create_webapp(cfg: Cfg, dry_run: bool) -> Path | None:
    prepare_directories(cfg, dry_run=dry_run)

    log("Detecting static directory...")
    static_dir = detect_static_dir(cfg)
    log(f"Static directory: {static_dir if static_dir else '<none detected>'}")

    write_env_file(cfg, static_dir, dry_run=dry_run)
    write_systemd_service(cfg, dry_run=dry_run)
    write_nginx_config(cfg, static_dir, dry_run=dry_run)

    return static_dir
