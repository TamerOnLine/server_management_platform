# 🚀 Tamer

This README contains all terminal commands required to manage this website
using the **webapp CLI**.

---

## 📌 Website Information

- Domain: `tamer`
- Internal Port: `6666`

---

## 🆕 Create Website

```bash
sudo webapp new tamer
```

Dry run:
```bash
sudo webapp new tamer --dry-run
```

---

## 🔐 Generate / Update Environment (.env)

```bash
sudo webapp env --domain tamer --port 6666
```

Force overwrite:
```bash
sudo webapp env --domain tamer --port 6666 --force
```

Recommended:
```bash
sudo webapp env --domain tamer --port 6666 --force --link-systemd --restart
```

---

## 🔄 Update / Deploy Website

```bash
sudo webapp update tamer
```

Dry run:
```bash
sudo webapp update tamer --dry-run
```

Reload nginx:
```bash
sudo webapp update tamer --reload-nginx
```

---

## 📋 List All Websites

```bash
webapp list
```

JSON output:
```bash
webapp list --json
```

---

## 🧠 systemd Commands

Status:
```bash
systemctl status webapp@tamer --no-pager
```

Restart:
```bash
sudo systemctl restart webapp@tamer
```

Logs:
```bash
journalctl -u webapp@tamer -f
```

Reload units:
```bash
sudo systemctl daemon-reload
```

---

## 🌐 Nginx Commands

Test configuration:
```bash
sudo nginx -t
```

Reload nginx:
```bash
sudo systemctl reload nginx
```

Restart nginx:
```bash
sudo systemctl restart nginx
```

---

## 🧪 Local Health Check

```bash
curl http://127.0.0.1:6666
```

---

## 🗑️ Delete Website

```bash
sudo webapp delete tamer
```

---

Maintained by **Tamer**
