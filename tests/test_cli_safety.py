from __future__ import annotations

import argparse
import unittest
from unittest.mock import patch

from webapp import cli
from webapp.core.validators import validate_app_name, validate_domain, validate_port


class ValidatorTests(unittest.TestCase):
    def test_accepts_safe_app_names(self) -> None:
        for name in ("example.com", "api-v2", "customer_01"):
            with self.subTest(name=name):
                validate_app_name(name)

    def test_rejects_path_traversal_and_unsafe_names(self) -> None:
        for name in ("../site", "/var/www/site", ".", "..", "site name", "site/name"):
            with self.subTest(name=name):
                with self.assertRaises(SystemExit):
                    validate_app_name(name)

    def test_validates_domains(self) -> None:
        validate_domain("api.example.com")
        for domain in ("localhost", "-bad.example", "bad-.example", "bad..example"):
            with self.subTest(domain=domain):
                with self.assertRaises(SystemExit):
                    validate_domain(domain)

    def test_validates_port_boundaries(self) -> None:
        validate_port(1)
        validate_port(65535)
        for port in (0, 65536):
            with self.subTest(port=port):
                with self.assertRaises(SystemExit):
                    validate_port(port)


class PrivilegedCommandTests(unittest.TestCase):
    @patch("webapp.cli.must_be_root")
    @patch("webapp.cli.delete_webapp")
    def test_delete_rejects_path_traversal_before_deletion(
        self, delete_webapp, must_be_root
    ) -> None:
        args = argparse.Namespace(app_name="../victim", yes=True, dry_run=False)

        with self.assertRaises(SystemExit):
            cli.cmd_delete(args)

        must_be_root.assert_called_once_with()
        delete_webapp.assert_not_called()

    @patch("webapp.cli.must_be_root")
    @patch("webapp.cli.update_site")
    def test_update_rejects_path_traversal_before_update(
        self, update_site, must_be_root
    ) -> None:
        args = argparse.Namespace(
            app_name="../victim",
            dry_run=False,
            no_restart=False,
            reload_nginx=False,
        )

        with self.assertRaises(SystemExit):
            cli.cmd_update(args)

        must_be_root.assert_called_once_with()
        update_site.assert_not_called()


if __name__ == "__main__":
    unittest.main()
