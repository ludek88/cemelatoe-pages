from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_site_seo.py"
SPEC = importlib.util.spec_from_file_location("validate_site_seo", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_index(site: Path, route: str, robots: str) -> None:
    target = site / "index.html" if route == "/" else site / route.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f"""<!doctype html>
<html lang="en">
<head><meta name="robots" content="{robots}"></head>
<body><h1>Test page</h1></body>
</html>
""",
        encoding="utf-8",
    )


class DiscoverIndexablePagesTest(unittest.TestCase):
    def test_discovers_future_indexable_routes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original_site = MODULE.SITE
            try:
                MODULE.SITE = Path(directory) / "site"
                write_index(MODULE.SITE, "/", "index,follow")
                write_index(MODULE.SITE, "/camel-toe/new-guide/", "index,follow")

                pages = MODULE.discover_indexable_pages()

                self.assertEqual(set(pages), {"/", "/camel-toe/new-guide/"})
            finally:
                MODULE.SITE = original_site

    def test_excludes_noindex_pages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            original_site = MODULE.SITE
            try:
                MODULE.SITE = Path(directory) / "site"
                write_index(MODULE.SITE, "/", "index,follow")
                write_index(MODULE.SITE, "/private/", "noindex,nofollow")

                pages = MODULE.discover_indexable_pages()

                self.assertEqual(set(pages), {"/"})
            finally:
                MODULE.SITE = original_site


class StructuredDataDateTimeTest(unittest.TestCase):
    def test_accepts_iso8601_datetime_with_offset(self) -> None:
        self.assertTrue(
            MODULE.is_iso8601_datetime_with_timezone("2026-07-23T09:20:56+02:00")
        )
        self.assertTrue(MODULE.is_iso8601_datetime_with_timezone("2026-07-23T07:20:56Z"))

    def test_rejects_date_only_or_timezone_free_values(self) -> None:
        self.assertFalse(MODULE.is_iso8601_datetime_with_timezone("2026-07-23"))
        self.assertFalse(
            MODULE.is_iso8601_datetime_with_timezone("2026-07-23T09:20:56")
        )


if __name__ == "__main__":
    unittest.main()
