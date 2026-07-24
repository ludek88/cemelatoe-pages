#!/usr/bin/env python3
"""Validate the static website's minimum technical SEO contract."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ORIGIN = "https://camelatoe.com"
REQUIRED_ROUTES = {
    "/",
    "/camel-toe/",
    "/camel-toe/meaning/",
    "/camel-toe/leggings/",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.h1_count = 0
        self.descriptions: list[str] = []
        self.robots: list[str] = []
        self.canonicals: list[str] = []
        self.og_urls: list[str] = []
        self.og_images: list[str] = []
        self.links: list[str] = []
        self.image_attrs: list[dict[str, str | None]] = []
        self.json_ld: list[str] = []
        self.lang: str | None = None
        self._in_title = False
        self._in_json_ld = False
        self._json_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            name = (values.get("name") or "").lower()
            prop = (values.get("property") or "").lower()
            content = values.get("content") or ""
            if name == "description":
                self.descriptions.append(content.strip())
            elif name == "robots":
                self.robots.append(content.strip().lower())
            elif prop == "og:url":
                self.og_urls.append(content.strip())
            elif prop == "og:image":
                self.og_images.append(content.strip())
        elif tag == "link" and (values.get("rel") or "").lower() == "canonical":
            self.canonicals.append((values.get("href") or "").strip())
        elif tag == "a":
            href = values.get("href")
            if href:
                self.links.append(href)
        elif tag == "img":
            self.image_attrs.append(values)
        elif tag == "script" and (values.get("type") or "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._json_parts).strip())
            self._in_json_ld = False
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if self._in_json_ld:
            self._json_parts.append(data)

    @property
    def title(self) -> str:
        return " ".join("".join(self.title_parts).split())


def local_target_exists(href: str) -> bool:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc or href.startswith(("#", "mailto:", "tel:")):
        return True
    path = parsed.path
    if not path.startswith("/"):
        return True
    candidate = SITE / path.lstrip("/")
    return (
        candidate.is_file()
        or (candidate / "index.html").is_file()
        or candidate.with_suffix(".html").is_file()
    )


def canonical_image_exists(image_url: str) -> bool:
    parsed = urlparse(image_url)
    if f"{parsed.scheme}://{parsed.netloc}" != ORIGIN:
        return False
    if not parsed.path.startswith("/assets/"):
        return False
    return (SITE / parsed.path.lstrip("/")).is_file()


def robots_tokens(parser: PageParser) -> set[str]:
    if len(parser.robots) != 1:
        return set()
    return {
        token
        for token in parser.robots[0].replace(",", " ").split()
        if token
    }


def route_for_index(file_path: Path) -> str:
    relative = file_path.relative_to(SITE)
    if relative == Path("index.html"):
        return "/"
    return f"/{relative.parent.as_posix().strip('/')}/"


def discover_indexable_pages() -> dict[str, Path]:
    pages: dict[str, Path] = {}
    for file_path in sorted(SITE.rglob("index.html")):
        parser = PageParser()
        parser.feed(file_path.read_text(encoding="utf-8"))
        tokens = robots_tokens(parser)
        if "index" in tokens and "noindex" not in tokens:
            pages[route_for_index(file_path)] = file_path
    return pages


def structured_data_nodes(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from structured_data_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from structured_data_nodes(child)


def is_iso8601_datetime_with_timezone(value: object) -> bool:
    if not isinstance(value, str) or "T" not in value:
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate(indexable: dict[str, Path] | None = None) -> list[str]:
    errors: list[str] = []
    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    canonicals: dict[str, str] = {}
    indexable = indexable or discover_indexable_pages()

    missing_required = REQUIRED_ROUTES - set(indexable)
    if missing_required:
        errors.append(f"missing required indexable routes: {sorted(missing_required)}")

    for route, file_path in sorted(indexable.items()):
        label = file_path.relative_to(ROOT)
        if not file_path.is_file():
            errors.append(f"{label}: missing indexable page")
            continue

        parser = PageParser()
        parser.feed(file_path.read_text(encoding="utf-8"))
        expected_url = f"{ORIGIN}{route}"

        if parser.lang != "en":
            errors.append(f"{label}: expected html lang=en")
        if not parser.title or len(parser.title) > 65:
            errors.append(f"{label}: title is missing or longer than 65 characters")
        elif parser.title in titles:
            errors.append(f"{label}: duplicate title also used by {titles[parser.title]}")
        else:
            titles[parser.title] = str(label)
        if len(parser.descriptions) != 1 or not 80 <= len(parser.descriptions[0]) <= 180:
            errors.append(f"{label}: needs one description of 80-180 characters")
        elif parser.descriptions[0] in descriptions:
            errors.append(f"{label}: duplicate description also used by {descriptions[parser.descriptions[0]]}")
        else:
            descriptions[parser.descriptions[0]] = str(label)
        if parser.h1_count != 1:
            errors.append(f"{label}: expected exactly one h1, found {parser.h1_count}")
        if parser.canonicals != [expected_url]:
            errors.append(f"{label}: canonical must be exactly {expected_url}")
        elif expected_url in canonicals:
            errors.append(f"{label}: duplicate canonical also used by {canonicals[expected_url]}")
        else:
            canonicals[expected_url] = str(label)
        if parser.og_urls != [expected_url]:
            errors.append(f"{label}: og:url must be exactly {expected_url}")
        if len(parser.og_images) != 1 or not canonical_image_exists(parser.og_images[0]):
            errors.append(f"{label}: needs one existing first-party social preview image")
        tokens = robots_tokens(parser)
        if "index" not in tokens or "noindex" in tokens:
            errors.append(f"{label}: page must explicitly allow indexing")
        if not parser.json_ld:
            errors.append(f"{label}: missing JSON-LD")
        for block in parser.json_ld:
            try:
                structured_data = json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: invalid JSON-LD ({exc})")
                continue
            for node in structured_data_nodes(structured_data):
                node_types = node.get("@type")
                if isinstance(node_types, str):
                    node_types = [node_types]
                if not isinstance(node_types, list) or "ProfilePage" not in node_types:
                    continue
                for property_name in ("dateCreated", "dateModified"):
                    if property_name in node and not is_iso8601_datetime_with_timezone(
                        node[property_name]
                    ):
                        errors.append(
                            f"{label}: ProfilePage {property_name} must be an "
                            "ISO 8601 DateTime with timezone"
                        )
        for href in parser.links:
            if not local_target_exists(href):
                errors.append(f"{label}: broken internal link {href}")
        for number, attrs in enumerate(parser.image_attrs, start=1):
            if not (attrs.get("alt") or "").strip():
                errors.append(f"{label}: image {number} needs useful alt text")
            if not attrs.get("width") or not attrs.get("height"):
                errors.append(f"{label}: image {number} needs width and height")

    robots_path = SITE / "robots.txt"
    if not robots_path.is_file():
        errors.append("site/robots.txt: missing")
    else:
        robots = robots_path.read_text(encoding="utf-8")
        if "<html" in robots.lower():
            errors.append("site/robots.txt: contains HTML")
        if f"Sitemap: {ORIGIN}/sitemap.xml" not in robots:
            errors.append("site/robots.txt: missing canonical sitemap directive")
        if "Disallow: /" in robots:
            errors.append("site/robots.txt: blocks the whole site")

    sitemap_path = SITE / "sitemap.xml"
    if not sitemap_path.is_file():
        errors.append("site/sitemap.xml: missing")
    else:
        try:
            root = ET.parse(sitemap_path).getroot()
            namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = {node.text for node in root.findall("sm:url/sm:loc", namespace)}
            expected = {f"{ORIGIN}{route}" for route in indexable}
            if urls != expected:
                errors.append(f"site/sitemap.xml: expected exactly {sorted(expected)}, found {sorted(urls)}")
        except ET.ParseError as exc:
            errors.append(f"site/sitemap.xml: invalid XML ({exc})")

    not_found_path = SITE / "404.html"
    if not not_found_path.is_file():
        errors.append("site/404.html: missing")
    else:
        parser = PageParser()
        parser.feed(not_found_path.read_text(encoding="utf-8"))
        if len(parser.robots) != 1 or "noindex" not in parser.robots[0]:
            errors.append("site/404.html: must use noindex")

    headers_path = SITE / "_headers"
    if not headers_path.is_file():
        errors.append("site/_headers: missing")
    else:
        headers = headers_path.read_text(encoding="utf-8")
        if "https://camela-toe.pages.dev/*" not in headers or "X-Robots-Tag: noindex, nofollow" not in headers:
            errors.append("site/_headers: must noindex the pages.dev hostname")

    social_card = SITE / "assets" / "camela-social-card.png"
    if not social_card.is_file():
        errors.append("site/assets/camela-social-card.png: missing")

    return errors


if __name__ == "__main__":
    pages = discover_indexable_pages()
    failures = validate(pages)
    if failures:
        print("SEO validation failed:")
        for failure in failures:
            print(f"  - {failure}")
        sys.exit(1)
    print(f"SEO validation passed for {len(pages)} indexable pages.")
