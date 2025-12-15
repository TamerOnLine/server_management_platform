# README — Installing Cloudflare Origin Certificate for Any Website (Ubuntu + Nginx)

This guide explains how to install a Cloudflare Origin Certificate for any domain on a server running Nginx.  
The certificate secures the connection **between Cloudflare and your server**.

---

## ✅ 1. Create the SSL directory for your domain

Replace `<domain>` with your real domain name:

```bash
sudo mkdir -p /etc/ssl/<domain>
```

Example:

```bash
sudo mkdir -p /etc/ssl/denkengewinnen.com
```

---

## ✅ 2. Add the certificate and private key

### Origin Certificate (CRT)

```bash
sudo nano /etc/ssl/<domain>/origin.crt
```

Paste the Cloudflare Origin Certificate, then save.

### Private Key (KEY)

```bash
sudo nano /etc/ssl/<domain>/origin.key
```

Paste your private key, then save.

---

## ✅ 3. Set correct permissions

```bash
sudo chmod 600 /etc/ssl/<domain>/origin.key
sudo chmod 644 /etc/ssl/<domain>/origin.crt
```

---

## ✅ 4. Update your website's Nginx configuration

Open the domain configuration file:

```bash
sudo nano /etc/nginx/sites-available/<domain>
```

Ensure these lines exist inside the HTTPS server block:

```nginx
server {
    listen 443 ssl http2;
    server_name <domain> www.<domain>;

    ssl_certificate     /etc/ssl/<domain>/origin.crt;
    ssl_certificate_key /etc/ssl/<domain>/origin.key;

    # ... rest of your configuration
}
```

---

## ✅ 5. Test and reload Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## ✅ 6. Configure Cloudflare

In Cloudflare dashboard:

1. Go to **SSL/TLS**
2. Select **Full (strict)** mode

---

## ✅ 7. Test the website

```bash
curl -v https://<domain>/
```

Or open the website in a browser and verify that HTTPS lock appears without warnings.

---

### 🎉 Done — Your Origin Certificate is fully installed and active.
You can reuse these steps for any new domain on your server.
