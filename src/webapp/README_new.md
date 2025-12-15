# WebApp Creator – new.py

This module is responsible for creating and provisioning a new FastAPI web application
on the server, including nginx, systemd, and environment configuration.

---

## 📍 Location

src/webapp/new.py

---

## 🧠 Purpose

`new.py` implements the **creation workflow** used by the `webapp new` command.
It standardizes how new applications are deployed on the server to ensure consistency,
security, and reproducibility.

---

## ⚙️ Responsibilities

The module performs the following tasks:

- Create the project directory under `/var/www/<app_name>`
- Generate `/etc/webapp/<app_name>.env`
- Create and enable `systemd` service: `webapp@<app_name>.service`
- Generate nginx configuration with HTTP → HTTPS redirect
- Detect and configure static file serving automatically
- Reload systemd and nginx safely

---

## 🧩 Workflow Overview

1. Prepare required directories and permissions
2. Detect static directory if present
3. Write environment file
4. Create systemd unit
5. Create nginx site configuration
6. Validate nginx configuration and reload

All steps support **dry-run mode**.

---

## 🧪 Dry Run

Example:

```bash
webapp new example.com --dry-run
```

No system changes will be applied.

---

## 🔐 Security Notes

- Applications run as non-root users
- Secrets are stored only in env files
- SSL directories use restricted permissions
- systemd manages process lifecycle safely

---

## 👤 Author

TamerOnLine  
Core Infrastructure & DevOps
