#!/bin/bash

# Restore a single site from backup
# Usage:
#   sudo restore-site mystrotamer
#   sudo restore-site mystrotamer /var/backups/sites/mystrotamer/mystrotamer_2025-12-04_01-02-37.tar.gz

if [[ $EUID -ne 0 ]]; then
  echo "❌ Please run this script as root: sudo $0 <site_name> [backup_file]"
  exit 1
fi

SITE_NAME="$1"
BACKUP_FILE="$2"

if [[ -z "$SITE_NAME" ]]; then
  echo "❌ Usage: sudo restore-site <site_name> [backup_file]"
  exit 1
fi

BACKUP_DIR="/var/backups/sites/$SITE_NAME"

if [[ -z "$BACKUP_FILE" ]]; then
  # Automatically select the newest backup
  BACKUP_FILE=$(ls -t "$BACKUP_DIR"/${SITE_NAME}_*.tar.gz 2>/dev/null | head -n1)
fi

if [[ -z "$BACKUP_FILE" || ! -f "$BACKUP_FILE" ]]; then
  echo "❌ Backup file not found for site '$SITE_NAME'."
  echo "   Searched in: $BACKUP_DIR"
  exit 1
fi

echo "======================================"
echo "♻ Restoring site: $SITE_NAME"
echo "📦 Backup file: $BACKUP_FILE"
echo "======================================"
echo "This will overwrite files under:"
echo "  - /var/www/$SITE_NAME"
echo "  - /etc/webapp/$SITE_NAME.env (if included in backup)"
echo "  - /etc/nginx/sites-available (if config is included)"
echo

read -p "Are you sure you want to continue? [y/N]: " CONFIRM
case "$CONFIRM" in
  y|Y|yes|YES) ;;
  *) echo "❌ Restore cancelled."; exit 1;;
esac

# Extract the backup into the system root /
tar -xzf "$BACKUP_FILE" -C /

# Fix permissions for the project folder (optional but useful)
if [[ -d "/var/www/$SITE_NAME" ]]; then
  chown -R tamer:www-data "/var/www/$SITE_NAME"
fi

echo "✅ Restore completed for site: $SITE_NAME"
echo "ℹ️ If an nginx config was restored, you may want to reload nginx:"
echo "   sudo nginx -t && sudo systemctl reload nginx"
