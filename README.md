# Server Management Platform

A Linux infrastructure toolkit for managing multiple Python web applications behind **nginx** and **systemd** through a single `webapp` command.

> [!IMPORTANT]
> This project performs privileged server operations. Review generated configuration, use `--dry-run` where available, and test it on a non-production server before adoption.

## Features

- Create nginx and systemd configuration for a Python web application.
- Keep application settings in `/etc/webapp/<app>.env` with mode `0600`.
- List managed applications and their service status.
- Pull application updates and optionally restart services or reload nginx.
- Back up application files and configuration before deletion.
- Generate production-oriented environment files.
- Support Cloudflare Origin certificates.
- Validate domains, ports, and application names before privileged operations.

## Requirements

- Linux with systemd and nginx
- Python 3.10 or newer
- Root access for commands that modify server configuration
- A Python application served by an ASGI server such as Uvicorn
- Cloudflare Origin certificates if the generated HTTPS configuration is used

## Installation

```bash
git clone https://github.com/TamerOnLine/server_management_platform.git
cd server_management_platform

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .

webapp --help
```

To expose the command system-wide while keeping it installed in the virtual environment:

```bash
sudo ln -s /srv/server_management_platform/.venv/bin/webapp /usr/local/bin/webapp
```

Adjust `/srv/server_management_platform` to the actual clone location.

## Usage

### List applications

```bash
webapp list
webapp list --json
```

### Create application configuration

Interactive mode:

```bash
sudo webapp new example.com --dry-run
sudo webapp new example.com
```

Advanced mode:

```bash
sudo webapp new \
  --app-name example-api \
  --domain api.example.com \
  --port 8600 \
  --app-module backend.app.main:app \
  --dry-run
```

Remove `--dry-run` only after reviewing the output and placing certificates at:

```text
/etc/ssl/<domain>/origin.crt
/etc/ssl/<domain>/origin.key
```

### Update an application

```bash
sudo webapp update example-api --dry-run
sudo webapp update example-api
sudo webapp update example-api --reload-nginx
```

### Generate an environment file

```bash
sudo webapp env --domain example.com --port 8600
```

### Back up and delete an application

Always preview the targets first:

```bash
sudo webapp delete example-api --dry-run
sudo webapp delete example-api
```

The delete command creates a `.tar.gz` archive under `/var/backups/sites` before removing managed files. Verify that the backup exists and is readable.

## Infrastructure deployment

The repository also includes an infrastructure deployment script:

```bash
sudo python3 deploy/deploy.py --dry-run
sudo python3 deploy/deploy.py
```

It backs up managed nginx, systemd, and command files before synchronization, then validates nginx before reload.

## Project structure

```text
.
├── deploy/                  # Infrastructure deployment logic
├── nginx/                   # Versioned nginx configuration
├── systemd/                 # systemd templates
├── src/webapp/              # Python CLI package
│   ├── cli.py
│   ├── new.py
│   ├── update.py
│   ├── delete.py
│   ├── list.py
│   ├── env.py
│   └── core/
├── tests/                   # Unit tests
├── Docs/                    # Operational documentation
└── pyproject.toml
```

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

CI runs the test suite on Python 3.10 and 3.12.

## Security

Do not commit environment files, certificates, private keys, or server backups. To report a vulnerability, follow [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development and pull-request workflow.

## License

Released under the [MIT License](LICENSE).
