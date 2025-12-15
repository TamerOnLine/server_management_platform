# Environment Generator – `env.py`

This module generates **production `.env` files** for FastAPI web applications managed by the `webapp`
infrastructure toolkit.

It is used by the CLI command:

```bash
webapp env
```

and provides a **safe, repeatable, standardized** way to create environment configuration files.

---

## 📍 Location

```
src/webapp/env.py
```

---

## 🧠 Purpose

`env.py` centralizes the logic for creating **production-ready environment files** that are:

- Secure by default (permissions `600`)
- Consistent across all deployed web applications
- Optionally integrated with `systemd` via a symlink
- Able to restart the app service after writing

By default, the generated file is written to:

```
/var/www/<domain>/.env
```

---

## ✨ New Features

### 🔗 `--link-systemd`

If enabled, the tool creates (or replaces) a symlink:

```
/etc/webapp/<domain>.env  →  /var/www/<domain>/.env
```

This is useful when your `webapp@<domain>` systemd unit loads environment variables from
`/etc/webapp/<domain>.env` but you want to keep the canonical app `.env` inside the project directory.

### 🔁 `--restart`

If enabled, the tool restarts the systemd service after writing the env file:

```
systemctl restart webapp@<domain>
```

---

## ⚙️ Main Components

### 1️⃣ `EnvArgs` (Configuration Model)

A strongly-typed configuration object that defines all inputs required to generate an environment file.

Common inputs:

| Field | Description |
|------|------------|
| `domain` | Domain name of the application |
| `port` | Internal FastAPI port (must match Nginx upstream) |
| `project_root_base` | Base directory for projects (default: `/var/www`) |
| `app_module` | FastAPI entry point (default: `app.main:app`) |
| `site_name` | Human-readable site name |
| `meta_description` | Default SEO meta description |
| `company_email` | Contact email |
| `og_image` | OpenGraph image URL |
| `secret_key` | Application secret key |
| `force` | Overwrite existing `.env` file |
| `link_systemd` | Create symlink under `/etc/webapp/` |
| `restart` | Restart systemd service after writing |

---

### 2️⃣ Environment File Generator

The module dynamically generates a **documented `.env` file** including sections such as:

- Runtime & Application Core
- Site Configuration
- Security
- Allowed Hosts & CORS
- SMTP (optional)

If no secret key is provided, one may be generated automatically (depending on implementation).

---

### 3️⃣ File Writing & Permissions

When writing the `.env` file:

- The project directory is created if missing
- Existing files are protected unless `--force` is used
- File permissions are set to **600**
- Optional systemd integration via `--link-systemd`
- Optional systemd restart via `--restart`

---

## 🧪 CLI Usage

### Basic usage

```bash
sudo webapp env --domain example.com --port 8601
```

### Overwrite existing file

```bash
sudo webapp env --domain example.com --port 8601 --force
```

### Overwrite and restart service

```bash
sudo webapp env --domain example.com --port 8601 --force --restart
```

### Overwrite, link to systemd, and restart (recommended)

```bash
sudo webapp env --domain example.com --port 8601 --force --link-systemd --restart
```

---

## 🔐 Security Considerations

- `.env` files are readable only by the owner (`chmod 600`)
- Secrets are never hardcoded in the tool
- Restarting services is always **explicit** via `--restart`
- Linking `/etc/webapp/<domain>.env` is explicit via `--link-systemd`

---

## 🔁 systemd Integration Notes

Depending on your `webapp@.service`, you may use one of these patterns:

### Pattern A: systemd loads env from project `.env`

```ini
EnvironmentFile=/var/www/%i/.env
```

### Pattern B: systemd loads env from `/etc/webapp`

```ini
EnvironmentFile=/etc/webapp/%i.env
```

If you use Pattern B but want to store the canonical `.env` in the project directory,
use:

```bash
sudo webapp env --domain <domain> --port <port> --link-systemd
```

---

## ✅ Summary

`env.py` provides a **clean, secure, repeatable** way to manage production environment variables across
all FastAPI services in the infrastructure, with optional systemd linking and service restart.

---

## 👤 Author

**TamerOnLine**  
Infrastructure & DevOps  
FastAPI • systemd • Nginx
