# Server Management Platform

A lightweight infrastructure toolkit for deploying and operating multiple Python and FastAPI applications on a single Linux server.

The platform combines a unified Python CLI named `webapp` with systemd and Nginx to make application provisioning, deployment, updates, backups, and rollback workflows consistent and repeatable.

## Why this project exists

Operating several web applications on one server often leads to duplicated service files, handwritten proxy configuration, inconsistent environment variables, and risky manual deployment steps.

This project provides one operational interface and a predictable layout for managing those applications while keeping the underlying Linux components explicit and inspectable.

## Key capabilities

- Unified `webapp` command-line interface
- Automated application provisioning
- Generated systemd service configuration
- Generated Nginx reverse-proxy configuration
- Centralized environment configuration
- Cloudflare Origin SSL support
- Safe update, backup, deletion, and rollback workflows
- Operational status and application listing
- Support for multiple Python and FastAPI applications on one server

## Architecture

Each managed application:

- lives under `/var/www/<app>`
- runs through a systemd service
- is served by Uvicorn
- is proxied through Nginx
- is managed through the `webapp` CLI

~~~text
Client
  |
Nginx
  |
systemd service
  |
Uvicorn / FastAPI application
~~~

## Technology stack

- Python
- FastAPI and Uvicorn
- Linux
- systemd
- Nginx
- Cloudflare Origin SSL
- GitHub Actions
- Bash for selected operational tasks

## Project structure

~~~text
server_management_platform/
├── deploy/                 # Deployment logic
├── nginx/                  # Versioned Nginx configuration
├── systemd/                # Service templates
├── scripts/                # Supporting and legacy scripts
├── src/webapp/             # Python CLI package
├── Docs/                   # Additional documentation
├── pyproject.toml
├── README.md
└── LICENSE
~~~

## Installation

### 1. Clone the repository

~~~bash
git clone https://github.com/TamerOnLine/server_management_platform.git
cd server_management_platform
~~~

### 2. Create a virtual environment

~~~bash
uv venv .venv
source .venv/bin/activate
~~~

### 3. Install the CLI

~~~bash
uv pip install -e .
webapp --help
~~~

For system-wide use on a server, expose the installed command:

~~~bash
sudo ln -sf "$(pwd)/.venv/bin/webapp" /usr/local/bin/webapp
~~~

## CLI examples

### List managed applications

~~~bash
webapp list
~~~

### Provision an application

~~~bash
webapp new example.com
~~~

The provisioning workflow creates the environment configuration, prepares the Nginx configuration, and configures the systemd service.

### Update an application

~~~bash
webapp update example.com
webapp update example.com --dry-run
webapp update example.com --reload-nginx
~~~

### Generate environment configuration

~~~bash
webapp env --domain example.com --port 8600
~~~

### Remove an application safely

~~~bash
webapp delete example.com
~~~

The deletion workflow includes confirmation, backup, configuration cleanup, and rollback-oriented safeguards.

## Operational principles

- Prefer repeatable commands over manual server edits.
- Keep configuration versioned and reviewable.
- Validate changes before reloading services.
- Back up application state before destructive operations.
- Keep secrets outside source control.
- Treat rollback as part of deployment design.

## Project status

This project is under active development and is used as a reference implementation for managing production-oriented Python web applications on Linux.

Review commands and configuration before using the toolkit on a production server. Test changes in an isolated environment first.

## License

Released under the MIT License. See [LICENSE](LICENSE).
