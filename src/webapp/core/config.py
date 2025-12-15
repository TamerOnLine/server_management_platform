from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Cfg:
    app_name: str
    domain: str
    port: int
    app_module: str

    app_user: str = "tamer"
    group: str = "www-data"

    project_root_base: Path = Path("/var/www")
    etc_webapp: Path = Path("/etc/webapp")
    nginx_avail: Path = Path("/etc/nginx/sites-available")
    nginx_enabled: Path = Path("/etc/nginx/sites-enabled")
    systemd_dir: Path = Path("/etc/systemd/system")
    ssl_base: Path = Path("/etc/ssl")
    venv_name: str = ".venv"

    @property
    def project_root(self) -> Path:
        return self.project_root_base / self.app_name

    @property
    def backend_dir(self) -> Path:
        return self.project_root / "backend"

    @property
    def app_dir(self) -> Path:
        return self.backend_dir / "app"

    @property
    def ssl_dir(self) -> Path:
        return self.ssl_base / self.domain

    @property
    def env_file(self) -> Path:
        return self.etc_webapp / f"{self.app_name}.env"

    @property
    def nginx_available(self) -> Path:
        return self.nginx_avail / self.app_name

    @property
    def nginx_enabled_link(self) -> Path:
        return self.nginx_enabled / self.app_name

    @property
    def systemd_service(self) -> Path:
        return self.systemd_dir / f"webapp@{self.app_name}.service"

    @property
    def venv_bin(self) -> Path:
        return self.project_root / self.venv_name / "bin"
