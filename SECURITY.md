# Security Policy

## Supported version

Security fixes are currently applied to the latest revision of the `main` branch.

## Reporting a vulnerability

Please do not open a public issue for an unpatched vulnerability. Use GitHub's private vulnerability reporting feature for this repository. If it is unavailable, contact the maintainer privately through the profile links on [TamerOnLine](https://github.com/TamerOnLine).

Include:

- the affected command or file;
- reproduction steps;
- the potential impact;
- any suggested mitigation.

Do not include real credentials, private keys, certificates, tokens, or production server data.

## Operational guidance

This tool changes nginx, systemd, SSL, application, and backup paths with elevated privileges. Before running it:

- inspect the source and generated configuration;
- use `--dry-run` where supported;
- keep a separate, verified server backup;
- test on a non-production host;
- restrict who can run the `webapp` command;
- review application names, domains, ports, and filesystem targets.

Never commit files from `/etc/webapp`, private keys from `/etc/ssl`, or archives from `/var/backups/sites`.
