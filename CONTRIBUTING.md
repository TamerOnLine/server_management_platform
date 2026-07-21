# Contributing

Thank you for improving Server Management Platform.

## Development setup

1. Fork or clone the repository.
2. Create a branch from `main`.
3. Create a virtual environment and install the project:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -e .
   ```

4. Run the test suite:

   ```bash
   python -m unittest discover -s tests -v
   ```

## Pull requests

- Keep each pull request focused on one change.
- Add or update tests for behavioral changes.
- Document new commands and flags.
- Do not include secrets, certificates, environment files, backups, or machine-specific paths.
- Exercise destructive or privileged workflows with `--dry-run` first.
- Describe any nginx, systemd, filesystem, or compatibility impact in the pull request.

## Safety expectations

Code that builds filesystem paths from user input must validate that input before reading, writing, or deleting files. External commands must use argument lists rather than shell strings. Tests must mock privileged commands and must not modify the host system.
