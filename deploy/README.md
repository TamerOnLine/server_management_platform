# pi-node-server-infra – Safe Deploy Script

This repository contains the **infrastructure deployment system** for the Pi Node server.
The main entry point for applying infrastructure changes on the server is:

```
deploy/deploy.py
```

It is a **safe deployment script** written in Python that performs:

- Git update (non-root, SSH-safe)
- Automatic backups
- Sync of nginx, systemd, and helper scripts
- Permission fixes
- nginx validation
- Automatic rollback on failure

---

## 🚀 Quick Deploy (Recommended)

```bash
cd /srv/pi-node-server-infra
git pull
sudo /srv/pi-node-server-infra/deploy/deploy.py
```

---

## 🧠 What `deploy.py` Does

### 1️⃣ Git Pull (Non-root)
Runs `git pull origin main` as the original user to ensure SSH keys work correctly.

### 2️⃣ Automatic Backups
Creates timestamped backups in:

```
/var/backups/pi-node-server-infra/YYYYMMDD-HHMMSS/
```

Backed up directories:
- `/etc/nginx/sites-available`
- `/etc/nginx/snippets`
- `/etc/systemd/system`
- `/usr/local/bin`

### 3️⃣ Sync Infrastructure
Uses `rsync` to apply repo configs safely to the system.

### 4️⃣ Permissions
Ensures all helper scripts are executable.

### 5️⃣ systemd & nginx
- Reloads systemd
- Validates nginx config
- Reloads nginx on success
- Rolls back automatically on failure

---

## 🧪 Dry Run

```bash
sudo /srv/pi-node-server-infra/deploy/deploy.py --dry-run
```

---

## ⚙️ Options

- `--dry-run`
- `--no-backup`
- `--no-chmod`
- `--repo-dir`
- `--branch`
- `--remote`

---

## 🔐 Root Requirement

The script must be run with `sudo` because it modifies system-level directories.

---

## ✅ Recommended Workflow

```bash
cd /srv/pi-node-server-infra
git pull
sudo ./deploy/deploy.py
```

---

Maintained by **TamerOnLine**
