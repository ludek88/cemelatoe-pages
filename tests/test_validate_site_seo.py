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


class SitemapAndContentContractTest(unittest.TestCase):
    def test_accepts_exact_sitemap_dates_only(self) -> None:
        self.assertTrue(MODULE.is_yyyy_mm_dd("2026-11-19"))
        self.assertFalse(MODULE.is_yyyy_mm_dd("2026-11-19T00:00:00Z"))
        self.assertFalse(MODULE.is_yyyy_mm_dd("2026-13-40"))
        self.assertFalse(MODULE.is_yyyy_mm_dd("19 Nov 2026"))

    def test_faq_answers_must_be_visible_outside_json_ld(self) -> None:
        html = """
        <script type="application/ld+json">
        {"@type":"FAQPage","mainEntity":[
          {"@type":"Question","name":"What does camel toe mean?","acceptedAnswer":{"@type":"Answer","text":"A visible clothing outline."}}
        ]}
        </script>
        <h3>What does camel toe mean?</h3>
        <p>A visible clothing outline.</p>
        """
        self.assertEqual(MODULE.faq_text_gaps(html), [])

        hidden = html.replace("<p>A visible clothing outline.</p>", "<p>Something else.</p>")
        self.assertIn("A visible clothing outline.", MODULE.faq_text_gaps(hidden))

    def test_social_dimensions_follow_each_image_file(self) -> None:
        assets = Path(__file__).resolve().parents[1] / "site" / "assets"
        social_card = assets / "camela-social-card.png"
        leggings = assets / "leggings-construction-flatlay.jpg"
        hero_webp = assets / "camela-hero.webp"
        self.assertEqual(MODULE.image_pixel_size(social_card), (1200, 630))
        self.assertEqual(MODULE.image_pixel_size(leggings), (1200, 670))
        self.assertEqual(
            MODULE.image_pixel_size(hero_webp),
            MODULE.image_pixel_size(assets / "camela-hero.jpg"),
        )
        self.assertEqual(
            MODULE.social_dimension_errors(
                "site/camel-toe/leggings/index.html",
                "og:image",
                "https://camelatoe.com/assets/leggings-construction-flatlay.jpg",
                "1200",
                "670",
            ),
            [],
        )
        mismatch = MODULE.social_dimension_errors(
            "site/camel-toe/leggings/index.html",
            "og:image",
            "https://camelatoe.com/assets/leggings-construction-flatlay.jpg",
            "1200",
            "630",
        )
        self.assertEqual(len(mismatch), 1)
        self.assertIn("1200x670", mismatch[0])

    def test_homepage_photos_keep_a_smaller_webp_sibling(self) -> None:
        assets = Path(__file__).resolve().parents[1] / "site" / "assets"
        names = (
            "camela-hero",
            "camela-yoga",
            "camela-home",
            "camela-bedroom-knit",
            "camela-balcony",
            "camela-bedroom",
        )
        webp_total = 0
        for name in names:
            jpeg = assets / f"{name}.jpg"
            webp = assets / f"{name}.webp"
            self.assertTrue(jpeg.is_file(), name)
            self.assertTrue(webp.is_file(), name)
            self.assertLess(webp.stat().st_size, jpeg.stat().st_size, name)
            self.assertEqual(MODULE.image_pixel_size(webp), MODULE.image_pixel_size(jpeg), name)
            self.assertTrue(webp.read_bytes().startswith(b"RIFF"), name)
            webp_total += webp.stat().st_size
        self.assertLess(webp_total, 450_000)
        social_card = assets / "camela-social-card.png"
        self.assertLess(social_card.stat().st_size, 200_000)
        self.assertEqual(MODULE.image_pixel_size(social_card), (1200, 630))

    def test_editorial_images_stay_compact(self) -> None:
        assets = Path(__file__).resolve().parents[1] / "site" / "assets"
        limits = {
            "leggings-construction.webp": 80_000,
            "camela-author.webp": 80_000,
        }
        for name, limit in limits.items():
            path = assets / name
            self.assertTrue(path.is_file(), name)
            self.assertLess(path.stat().st_size, limit, name)
            self.assertTrue(path.read_bytes().startswith(b"RIFF"), name)


def indexable_html() -> dict[str, str]:
    return {
        route: path.read_text(encoding="utf-8")
        for route, path in MODULE.discover_indexable_pages().items()
    }


class BrandEntityContractTest(unittest.TestCase):
    def test_live_pages_share_one_camela_entity(self) -> None:
        self.assertEqual(MODULE.entity_contract_errors_for_pages(indexable_html()), [])

    def test_live_site_passes_the_seo_contract(self) -> None:
        self.assertEqual(MODULE.validate(), [])

    def test_facebook_markup_stays_on_the_owner_profile(self) -> None:
        self.assertEqual(MODULE.facebook_markup_errors(), [])

    def test_rejects_reordered_homepage_same_as(self) -> None:
        pages = indexable_html()
        pages["/"] = pages["/"].replace(
            '"https://www.instagram.com/cemelatoe/",\n'
            '                "https://www.facebook.com/558918060640371"',
            '"https://www.facebook.com/558918060640371",\n'
            '                "https://www.instagram.com/cemelatoe/"',
            1,
        )
        errors = MODULE.entity_contract_errors_for_pages(pages)
        self.assertTrue(any(error.startswith("/") and "sameAs" in error for error in errors))

    def test_rejects_a_camela_reference_without_the_shared_same_as(self) -> None:
        pages = indexable_html()
        pages["/camel-toe/"] = """
        <script type="application/ld+json">
        {"@type":"Article","isPartOf":{"@id":"https://camelatoe.com/#website"},
         "publisher":{"@id":"https://camelatoe.com/#camela"}}
        </script>
        """
        errors = MODULE.entity_contract_errors_for_pages(pages)
        self.assertTrue(any("exactly one embedded Person #camela" in error for error in errors))
        self.assertTrue(any("Article publisher must be the shared Person" in error for error in errors))

    def test_rejects_a_homepage_without_a_website_node(self) -> None:
        pages = indexable_html()
        pages["/"] = pages["/"].replace('"@type": "WebSite"', '"@type": "WebPage"', 1)
        errors = MODULE.entity_contract_errors_for_pages(pages)
        self.assertTrue(any("exactly one WebSite" in error for error in errors))

    def test_rejects_a_website_without_the_publisher_reference(self) -> None:
        pages = indexable_html()
        pages["/"] = pages["/"].replace(
            '"publisher": {\n              "@id": "https://camelatoe.com/#camela"\n            },\n',
            "",
            1,
        )
        errors = MODULE.entity_contract_errors_for_pages(pages)
        self.assertTrue(any("WebSite publisher must reference" in error for error in errors))

    def test_rejects_a_missing_about_anchor(self) -> None:
        pages = indexable_html()
        pages["/"] = pages["/"].replace('id="about"', 'id="story"', 1)
        errors = MODULE.entity_contract_errors_for_pages(pages)
        self.assertTrue(any('id="about"' in error for error in errors))

    def test_rejects_a_different_facebook_url(self) -> None:
        html = f'<a href="{MODULE.FACEBOOK_PROFILE_URL}">Facebook</a> https://facebook.com/camelastoe'
        errors = MODULE.facebook_markup_errors({"site/index.html": html})
        self.assertTrue(any("camelastoe" in error for error in errors))
        self.assertTrue(all(MODULE.FACEBOOK_PROFILE_URL in error or "camelastoe" in error for error in errors))


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
