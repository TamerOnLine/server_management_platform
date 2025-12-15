# update.py – WebApp Update & Deploy Helper

## Overview

`update.py` is part of the **webapp** infrastructure toolkit.  
It provides a clean and reliable **update & deploy mechanism** for hosted websites.

With a single command, it allows you to:
- Pull the latest code from Git
- Restart the FastAPI / Uvicorn systemd service
- Optionally reload Nginx

> Goal: **One-command production deploy** with minimal risk and maximum clarity.

---

## Usage

```bash
sudo webapp update <app_name>
```

Example:
```bash
sudo webapp update denkengewinnen.com
```

---

## What Happens Internally

When the command is executed, `update.py` performs the following steps:

1. 📁 Resolves the project directory:
   ```
   /var/www/<app_name>
   ```

2. 🔍 Verifies the project is a Git repository

3. ⬇️ Pulls the latest changes:
   ```bash
   git pull
   ```

4. 🔁 Restarts the systemd service:
   ```bash
   systemctl restart webapp@<app_name>
   ```

5. 📊 Displays the service status

---

## Optional Flags

### Disable Restart
```bash
sudo webapp update <app_name> --no-restart
```

### Reload Nginx
```bash
sudo webapp update <app_name> --reload-nginx
```

### Dry Run (Simulation Mode)
```bash
sudo webapp update <app_name> --dry-run
```

---

## Functions Overview

### `update_git(project_root, dry_run)`
- Ensures the project is a Git repository
- Executes `git pull`

### `restart_service(app_name, dry_run)`
- Restarts `webapp@<app_name>.service`
- Shows the service status

### `reload_nginx(dry_run)`
- Validates Nginx configuration
- Reloads Nginx without downtime

### `update_site(app_name, dry_run, no_restart, do_reload_nginx)`
Main orchestrator that executes all update steps in order.

---

## Expected Project Layout

```text
/var/www/
 └── denkengewinnen.com/
     ├── .git/
     ├── .env
     ├── app/
     └── ...
```

Systemd service:
```text
webapp@denkengewinnen.com.service
```

---

## Why This Matters

- 🚀 One-command deployment
- 🧠 No manual SSH steps
- 🔐 Safe by design
- 📦 Perfect for multi-site servers
- 🧩 Easy to extend (migrations, health checks, rollback)

---

## Summary

**`update.py` is the deploy button of your server.**

`git pull` → restart service → site updated.

---

Author: Tamer  
Part of the **webapp** infrastructure toolkit
