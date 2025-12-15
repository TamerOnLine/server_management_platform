# 📘 README — Deploying a FastAPI App on Ubuntu Using Uvicorn, uv, systemd, and Nginx

This guide describes how to deploy a FastAPI application on a production server using:

- uv as a fast package and environment manager
- venv for isolated Python environments
- reposmith for optional project bootstrapping
- systemd for running the app as a service
- Nginx as a reverse proxy
- Cloudflare Origin SSL certificates

This document reflects the setup used for the project denkengewinnen.com.

---

## 1. Clone the Project

```bash
git clone git@github.com:www-website-online/denkengewinnen.git /var/www/denkengewinnen.com
cd /var/www/denkengewinnen.com
```

---

## 2. Create a Virtual Environment

```bash
uv venv
source .venv/bin/activate
```

---

## 3. Install Dependencies (using uv)

```bash
uv sync
```

---

## 4. Environment Variables (.env)

Create or edit:

/var/www/denkengewinnen.com/.env

Example:

```env
ENV=production
DEBUG=false

SITE_NAME="Denken Gewinnen"
DOMAIN="denkengewinnen.com"
DEFAULT_TITLE_SUFFIX=" – Denken Gewinnen"
DEFAULT_OG_IMAGE="https://denkengewinnen.com/static/img/og-default.jpg"
DEFAULT_META_DESCRIPTION="Denken Gewinnen – a modern platform for clearer thinking."

COMPANY_NAME="Denken Gewinnen"
COMPANY_EMAIL="info@denkengewinnen.com"
COMPANY_ADDRESS="Berlin, Germany"

SECRET_KEY="change-this-secret-key"

ALLOWED_HOSTS_CSV="denkengewinnen.com,www.denkengewinnen.com"
CORS_ORIGINS_CSV="https://denkengewinnen.com"
```

---

## 5. Systemd Service

Service file:

/etc/systemd/system/webapp@denkengewinnen.com.service

```ini
[Unit]
Description=FastAPI Web App - %i
After=network.target

[Service]
User=tamer
Group=www-data

WorkingDirectory=/var/www/%i/backend
EnvironmentFile=/etc/webapp/%i.env
Environment="PATH=/var/www/%i/.venv/bin"

ExecStart=/var/www/%i/.venv/bin/uvicorn ${APP_MODULE} --host 127.0.0.1 --port ${PORT}

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
sudo systemctl enable webapp@denkengewinnen.com
sudo systemctl restart webapp@denkengewinnen.com
```

---

## 6. Nginx Reverse Proxy

/etc/nginx/sites-available/denkengewinnen.com:

```nginx
server {
    listen 80;
    server_name denkengewinnen.com www.denkengewinnen.com;
    return 301 https://denkengewinnen.com$request_uri;
}

server {
    listen 443 ssl;
    server_name denkengewinnen.com www.denkengewinnen.com;

    ssl_certificate     /etc/ssl/denkengewinnen.com/origin.crt;
    ssl_certificate_key /etc/ssl/denkengewinnen.com/origin.key;

    location / {
        proxy_pass http://127.0.0.1:8099;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/denkengewinnen.com/backend/app/static/;
    }
}
```

---

## 7. Cloudflare Origin SSL

```bash
sudo chmod 600 /etc/ssl/denkengewinnen.com/origin.key
sudo chmod 644 /etc/ssl/denkengewinnen.com/origin.crt
```

---

## 8. Testing

```bash
curl -v http://127.0.0.1:8099/
curl -v -H "Host: denkengewinnen.com" http://127.0.0.1/
```

---

## 9. Deployment Workflow

```bash
cd /var/www/denkengewinnen.com
git pull
uv sync
sudo systemctl restart webapp@denkengewinnen.com
```

Deployment finished successfully.
