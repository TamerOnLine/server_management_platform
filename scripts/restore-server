#!/bin/bash

# Restore FULL server config + sites from backup
# Usage:
#   sudo restore-server
#   sudo restore-server /var/backups/server/server_2025-12-04_01-20-33.tar.gz

if [[ $EUID -ne 0 ]]; then
  echo "❌ Please run this script as root: sudo $0 [backup_file]"
  exit 1
fi

BACKUP_FILE="$1"
BACKUP_DIR="/var/backups/server"

if [[ -z "$BACKUP_FILE" ]]; then
  BACKUP_FILE=$(ls -t "$BACKUP_DIR"/server_*.tar.gz 2>/dev/null | head -n1)
fi

if [[ -z "$BACKUP_FILE" || ! -f "$BACKUP_FILE" ]]; then
  echo "❌ Server backup file not found."
  echo "   Searched in: $BACKUP_DIR"
  exit 1
fi

echo "======================================"
echo "♻ Restoring FULL SERVER from backup"
echo "📦 Backup file: $BACKUP_FILE"
echo "======================================"
echo "This will overwrite the following paths (if included in the backup archive):"
echo "  - /etc"
echo "  - /etc/nginx"
echo "  - /etc/webapp"
echo "  - /etc/systemd/system"
echo "  - /var/www"
echo "  - /home/tamer"
echo "  - /var/spool/cron/crontabs"
echo
echo "⚠️ WARNING: This will roll back the ENTIRE server."
echo "   Only use this if you intend a full system restore."
echo

read -p "Are you absolutely sure you want to continue? [type YES to continue]: " CONFIRM
if [[ "$CONFIRM" != "YES" ]]; then
  echo "❌ Restore cancelled."
  exit 1
fi

# Extract the backup into the system root /
tar -xzf "$BACKUP_FILE" -C /

# Reload systemd and restart nginx (safe operations)
if command -v systemctl >/dev/null 2>&1; then
  systemctl daemon-reload 2>/dev/null || true
  systemctl restart nginx 2>/dev/null || true
fi

# Fix permissions for website directories (optional but useful)
if [[ -d "/var/www" ]]; then
  chown -R tamer:www-data /var/www
fi

echo "✅ FULL SERVER restore completed successfully."
echo "ℹ️ It is recommended to reboot the server:"
echo "   sudo reboot"
