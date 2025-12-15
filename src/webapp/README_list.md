# list.py – WebApp Inventory & Status Viewer

## Overview

`list.py` is part of the **webapp** infrastructure toolkit.  
It provides a clear **inventory and status overview** of all managed web applications on the server.

With a single command, it shows:
- Registered applications
- Domain names
- Ports in use
- systemd service status
- Nginx integration status

> Goal: **Get a full operational overview of all web apps in one command.**

---

## Usage

### Show table view
```bash
webapp list
```

### JSON output (for automation / scripts)
```bash
webapp list --json
```

---

## How It Works

1. Reads all environment files from:
   ```
   /etc/webapp/*.env
   ```

2. Each `.env` file represents one managed web application.

3. Extracts core configuration values:
   - Application name
   - Domain
   - Port

4. Checks systemd:
   - Is the service active?
   - Is it enabled on boot?

5. Checks Nginx:
   - Site exists in `sites-available`
   - Site enabled in `sites-enabled`

6. Prints a formatted table or JSON output.

---

## Output Columns

| Column   | Description |
|--------|-------------|
| APP    | Application / service name |
| DOMAIN | Configured domain name |
| PORT   | FastAPI listening port |
| SYSTEMD | Service state (`active/enabled`) |
| NGINX  | Nginx status (`avail|en`) |

---

## Example Output

```text
APP              DOMAIN                         PORT   SYSTEMD              NGINX
-------------------------------------------------------------------------------------
denkengewinnen   denkengewinnen.com             8601   active/enabled       avail|en
```

---

## Internal Components

### `_run(cmd)`
Executes system commands and returns exit code and output.

### `systemd_state(service)`
Retrieves:
- Active state
- Enabled state

### `parse_env(path)`
Parses `.env` files into key/value pairs.

### `WebApp`
Dataclass representing a single web application.

### `build_app(env_file)`
Builds a full application status object from an `.env` file.

### `print_table(apps)`
Displays a clean, readable CLI table.

### `list_apps(as_json)`
Main entry function for listing all web apps.

---

## Expected Server Layout

```text
/etc/webapp/
 ├── site1.env
 ├── site2.env

/etc/nginx/
 ├── sites-available/
 ├── sites-enabled/
```

Systemd services:
```text
webapp@<app_name>.service
```

---

## Why This Matters

- 📊 Instant server overview
- 🧠 No guessing, real system state
- 🔍 Fast troubleshooting
- 🧩 Foundation for dashboards, monitoring, and automation

---

## Summary

**`list.py` is the monitoring lens of your server.**  
One command → full visibility.

---

Author: Tamer  
Part of the **webapp Infrastructure Toolkit**
