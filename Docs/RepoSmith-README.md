# RepoSmith Installation & Usage Guide

Lightweight Project Bootstrapper for Python (venv + uv)

---

## 1. Install RepoSmith System-Wide

### Create a dedicated tools directory
```bash
sudo mkdir -p /opt/py-tools
sudo chown tamer:tamer /opt/py-tools
cd /opt/py-tools
```

### Create a virtual environment using `uv`
```bash
uv venv
source .venv/bin/activate
```

### Install RepoSmith inside the venv
```bash
uv pip install reposmith-tol
```

### Verify installation
```bash
/opt/py-tools/.venv/bin/reposmith --help
```

### Expose RepoSmith as a system command
```bash
sudo ln -sf /opt/py-tools/.venv/bin/reposmith /usr/local/bin/reposmith
```

---

## 2. Check Server Environment
```bash
reposmith doctor
```

---

## 3. Create a New Python Project
```bash
cd /var/www
reposmith init my-new-project
```

Example structure:
```
my-new-project/
├── .venv/
├── src/
│   └── main.py
├── pyproject.toml
└── README.md
```

Activate venv:
```bash
source my-new-project/.venv/bin/activate
```

---

## 4. Update RepoSmith
```bash
source /opt/py-tools/.venv/bin/activate
uv pip install --upgrade reposmith-tol
```

---

## 5. Remove RepoSmith
```bash
sudo rm -f /usr/local/bin/reposmith
sudo rm -rf /opt/py-tools
```
