# 🚀 pi-node-server-infra

**Infrastructure Toolkit for managing multiple FastAPI / Python web applications on a single Linux server**  
with **systemd**, **nginx**, and a unified **Python CLI (`webapp`)**.

This project provides a **clean, production-ready framework** for hosting, managing, deploying, and operating
multiple Python-based web applications on one server in a safe and scalable way.

---

## ✨ Key Features

- 🧠 **Single CLI tool**: `webapp`
- ⚙️ Automatic **systemd service** generation (`webapp@<app>.service`)
- 🌐 Automatic **nginx site configuration**
- 🔐 Supports **Cloudflare Origin SSL**
- 📦 Python-based infra tools (no fragile bash scripts)
- 🛟 Safe **backup & rollback** during deployment
- 🧩 Designed for **hosting many websites on one server**

---

## 📁 Project Structure

```
pi-node-server-infra/
├── deploy/                 # Deployment logic (Python)
│   └── deploy.py
├── nginx/                  # Nginx configs (versioned)
│   ├── sites-available/
│   ├── snippets/
│   └── nginx.conf
├── systemd/                # systemd service templates
│   └── webapp@.service
├── scripts/
│   └── legacy/             # Old bash tools (kept for reference)
├── src/
│   └── webapp/             # Python CLI package
│       ├── cli.py          # Entry point (webapp command)
│       ├── new.py
│       ├── update.py
│       ├── delete.py
│       ├── list.py
│       ├── env.py
│       └── core/
├── Docs/                   # Documentation
├── pyproject.toml          # Python package definition
├── README.md
└── LICENSE
```

---

## 🧠 Core Concept

Each web application:

- Lives under `/var/www/<app>`
- Runs via:
  ```
  systemd → webapp@<app>.service → uvicorn
  ```
- Is proxied by nginx
- Is fully managed using the `webapp` CLI

You **never manually write nginx or systemd files** again.

---

## ⚡ Installation (Recommended)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/www-website-online/pi-node-server-infra.git
cd pi-node-server-infra
```

### 2️⃣ Create & activate a virtual environment
```bash
uv venv .venv
source .venv/bin/activate
```

### 3️⃣ Install the CLI tool
```bash
uv pip install -e .
```

### 4️⃣ Verify installation
```bash
webapp --help
```

---

## 🌍 System-wide Usage (Recommended for Servers)

After installing the CLI inside the virtual environment, you can expose
the `webapp` command system-wide so it works without activating the venv.

```bash
sudo ln -sf /srv/pi-node-server-infra/.venv/bin/webapp /usr/local/bin/webapp
```

Now you can run:
```bash
webapp list
webapp new example.com
```
from anywhere on the server without activating `.venv`.

---

## 🛠️ CLI Usage

### List all managed webapps
```bash
webapp list
```

Example output:
```
APP                 DOMAIN                     PORT   SYSTEMD              NGINX
denkengewinnen.com  denkengewinnen.com         8601   active/enabled       avail|en
```

---

### Create a new webapp
```bash
webapp new example.com
```

This command will:
- Ask for a port
- Create `/etc/webapp/example.com.env`
- Generate nginx config
- Generate systemd service
- Enable the service

---

### Update an existing webapp
```bash
webapp update example.com
```

Options:
```bash
webapp update example.com --dry-run
webapp update example.com --reload-nginx
```

---

### Delete a webapp (safe)
```bash
webapp delete example.com
```

Features:
- Automatic backup
- Confirmation prompt
- systemd + nginx cleanup
- Rollback support

---

### Generate `.env` file for an app
```bash
webapp env --domain example.com --port 8600
```

Creates:
```
/var/www/example.com/.env
```

With secure defaults:
- SECRET_KEY
- CORS configuration
- SMTP placeholders

---

## 🚀 Deploying Infrastructure Changes

After pulling updates from GitHub:

```bash
sudo python3 deploy/deploy.py
```

What this does:
- Creates backups of:
  - `/etc/nginx`
  - `/etc/systemd`
  - `/usr/local/bin`
- Syncs configs from the repository
- Reloads systemd
- Tests nginx configuration
- Reloads nginx safely

Dry run:
```bash
sudo python3 deploy/deploy.py --dry-run
```

---

## 🔐 SSL (Cloudflare Origin)

This project is designed for **Cloudflare Full (Strict)** mode.

Certificates are expected in:
```
/etc/ssl/<domain>/origin.crt
/ect/ssl/<domain>/origin.key
```

See documentation under:
```
Docs/
```

---

## 🧱 Design Principles

- **Single entry point** (`webapp`)
- **Infrastructure as Code**
- **Safe by default** (dry-run, backups)
- **No hidden magic**
- **Server-first mindset**

---

## 🧑‍💻 Author

**Tamer Hamad Faour**  
Infrastructure & Backend Engineer  
GitHub: https://github.com/www-website-online

---

## 📜 License

MIT License – see `LICENSE` file.
