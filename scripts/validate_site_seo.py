#!/usr/bin/env python3
"""Validate the static website's minimum technical SEO contract."""

from __future__ import annotations

import json
import re
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
        self.og_image_widths: list[str] = []
        self.og_image_heights: list[str] = []
        self.twitter_images: list[str] = []
        self.twitter_image_widths: list[str] = []
        self.twitter_image_heights: list[str] = []
        self.links: list[str] = []
        self.image_attrs: list[dict[str, str | None]] = []
        self.source_srcsets: list[str] = []
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
            elif prop == "og:image:width":
                self.og_image_widths.append(content.strip())
            elif prop == "og:image:height":
                self.og_image_heights.append(content.strip())
            social_name = prop or name
            if social_name == "twitter:image":
                self.twitter_images.append(content.strip())
            elif social_name == "twitter:image:width":
                self.twitter_image_widths.append(content.strip())
            elif social_name == "twitter:image:height":
                self.twitter_image_heights.append(content.strip())
        elif tag == "link" and (values.get("rel") or "").lower() == "canonical":
            self.canonicals.append((values.get("href") or "").strip())
        elif tag == "a":
            href = values.get("href")
            if href:
                self.links.append(href)
        elif tag == "img":
            self.image_attrs.append(values)
        elif tag == "source":
            srcset = (values.get("srcset") or "").strip()
            if srcset:
                self.source_srcsets.append(srcset)
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


def is_yyyy_mm_dd(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return parsed.strftime("%Y-%m-%d") == value


def is_positive_int_attribute(value: str | None) -> bool:
    return bool(value) and value.isdigit() and int(value) > 0


def image_pixel_size(path: Path) -> tuple[int, int] | None:
    """Return width and height from a PNG, JPEG, or WebP file header."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24 and data[12:16] == b"IHDR":
        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")
    if data.startswith(b"\xff\xd8"):
        return _jpeg_pixel_size(data)
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return _webp_pixel_size(data)
    return None


def _jpeg_pixel_size(data: bytes) -> tuple[int, int] | None:
    sof_markers = {
        0xC0, 0xC1, 0xC2, 0xC3,
        0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB,
        0xCD, 0xCE, 0xCF,
    }
    index = 2
    while index + 1 < len(data):
        if data[index] != 0xFF:
            return None
        index += 1
        while index < len(data) and data[index] == 0xFF:
            index += 1
        if index >= len(data):
            return None
        marker = data[index]
        index += 1
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7:
            continue
        if index + 2 > len(data):
            return None
        segment_length = int.from_bytes(data[index:index + 2], "big")
        if segment_length < 2 or index + segment_length > len(data):
            return None
        if marker in sof_markers:
            if segment_length < 7:
                return None
            height = int.from_bytes(data[index + 3:index + 5], "big")
            width = int.from_bytes(data[index + 5:index + 7], "big")
            if width > 0 and height > 0:
                return width, height
            return None
        index += segment_length
    return None


def _webp_pixel_size(data: bytes) -> tuple[int, int] | None:
    if len(data) < 30:
        return None
    chunk = data[12:16]
    if chunk == b"VP8X":
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
    elif chunk == b"VP8 ":
        width = int.from_bytes(data[26:28], "little") & 0x3FFF
        height = int.from_bytes(data[28:30], "little") & 0x3FFF
    elif chunk == b"VP8L" and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        width = (bits & 0x3FFF) + 1
        height = ((bits >> 14) & 0x3FFF) + 1
    else:
        return None
    if width > 0 and height > 0:
        return width, height
    return None


def srcset_urls(srcset: str) -> list[str]:
    urls: list[str] = []
    for candidate in srcset.split(","):
        parts = candidate.strip().split()
        if parts:
            urls.append(parts[0])
    return urls


def social_dimension_errors(
    label: str,
    kind: str,
    image_url: str,
    width: str | None,
    height: str | None,
) -> list[str]:
    """Compare declared social-image dimensions with the file itself."""
    if not is_positive_int_attribute(width) or not is_positive_int_attribute(height):
        return [f"{label}: {kind} needs positive integer width and height"]
    if not canonical_image_exists(image_url):
        return [f"{label}: {kind} file is missing ({image_url})"]
    path = SITE / urlparse(image_url).path.lstrip("/")
    actual = image_pixel_size(path)
    if actual is None:
        return [f"{label}: could not read pixel size of {path.relative_to(ROOT)}"]
    declared = (int(width or "0"), int(height or "0"))
    if declared != actual:
        return [
            f"{label}: {kind} declares {declared[0]}x{declared[1]} "
            f"but {path.relative_to(ROOT)} is {actual[0]}x{actual[1]}"
        ]
    return []


def local_image_exists(src: str) -> bool:
    parsed = urlparse(src)
    if parsed.scheme or parsed.netloc or src.startswith("data:"):
        return True
    relative = Path(parsed.path)
    if parsed.path.startswith("/"):
        candidate = (SITE / parsed.path.lstrip("/")).resolve()
    else:
        candidate = (SITE / relative).resolve()
    try:
        candidate.relative_to(SITE.resolve())
    except ValueError:
        return False
    return candidate.is_file()


def node_types(node: dict) -> list[str]:
    value = node.get("@type")
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def html_without_json_ld(html: str) -> str:
    return re.sub(
        r"<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>.*?</script>",
        "",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )


def faq_text_gaps(html: str) -> list[str]:
    """Return FAQ questions or answers that are not visible outside JSON-LD."""
    visible = html_without_json_ld(html)
    gaps: list[str] = []
    for match in re.finditer(
        r"<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        try:
            structured_data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        for node in structured_data_nodes(structured_data):
            if "Question" not in node_types(node):
                continue
            name = node.get("name")
            if isinstance(name, str) and name not in visible:
                gaps.append(name)
            answer = node.get("acceptedAnswer")
            if isinstance(answer, dict):
                text = answer.get("text")
                if isinstance(text, str) and text not in visible:
                    gaps.append(text)
    return gaps


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

        html = file_path.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(html)
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
        elif len(parser.og_image_widths) != 1 or len(parser.og_image_heights) != 1:
            errors.append(f"{label}: og:image needs one width and one height")
        else:
            errors.extend(
                social_dimension_errors(
                    str(label),
                    "og:image",
                    parser.og_images[0],
                    parser.og_image_widths[0],
                    parser.og_image_heights[0],
                )
            )
        if parser.twitter_image_widths or parser.twitter_image_heights:
            if (
                len(parser.twitter_images) != 1
                or len(parser.twitter_image_widths) != 1
                or len(parser.twitter_image_heights) != 1
            ):
                errors.append(f"{label}: twitter:image needs one image, width, and height")
            else:
                errors.extend(
                    social_dimension_errors(
                        str(label),
                        "twitter:image",
                        parser.twitter_images[0],
                        parser.twitter_image_widths[0],
                        parser.twitter_image_heights[0],
                    )
                )
        tokens = robots_tokens(parser)
        if "index" not in tokens or "noindex" in tokens:
            errors.append(f"{label}: page must explicitly allow indexing")
        if not parser.json_ld:
            errors.append(f"{label}: missing JSON-LD")
        found_breadcrumb = False
        for block in parser.json_ld:
            try:
                structured_data = json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: invalid JSON-LD ({exc})")
                continue
            for node in structured_data_nodes(structured_data):
                if "BreadcrumbList" in node_types(node):
                    found_breadcrumb = True
                if "ProfilePage" not in node_types(node):
                    continue
                for property_name in ("dateCreated", "dateModified"):
                    if property_name in node and not is_iso8601_datetime_with_timezone(
                        node[property_name]
                    ):
                        errors.append(
                            f"{label}: ProfilePage {property_name} must be an "
                            "ISO 8601 DateTime with timezone"
                        )
        if route != "/" and not found_breadcrumb:
            errors.append(f"{label}: indexable page needs a BreadcrumbList")
        for gap in faq_text_gaps(html):
            errors.append(f"{label}: FAQ text is not visible on the page: {gap}")
        for href in parser.links:
            if not local_target_exists(href):
                errors.append(f"{label}: broken internal link {href}")
        for number, attrs in enumerate(parser.image_attrs, start=1):
            if not (attrs.get("alt") or "").strip():
                errors.append(f"{label}: image {number} needs useful alt text")
            if not is_positive_int_attribute(attrs.get("width")) or not is_positive_int_attribute(
                attrs.get("height")
            ):
                errors.append(f"{label}: image {number} needs positive integer width and height")
            src = attrs.get("src") or ""
            if not src or not local_image_exists(src):
                errors.append(f"{label}: image {number} is missing a local file ({src})")
        for srcset in parser.source_srcsets:
            for url in srcset_urls(srcset):
                if not local_image_exists(url):
                    errors.append(f"{label}: image source is missing a local file ({url})")

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
            urls: set[str] = set()
            for url_node in root.findall("sm:url", namespace):
                loc = url_node.find("sm:loc", namespace)
                lastmod = url_node.find("sm:lastmod", namespace)
                loc_text = (loc.text or "").strip() if loc is not None else ""
                lastmod_text = (lastmod.text or "").strip() if lastmod is not None else ""
                urls.add(loc_text)
                if not is_yyyy_mm_dd(lastmod_text):
                    errors.append(
                        f"site/sitemap.xml: {loc_text or 'a URL'} needs a YYYY-MM-DD lastmod"
                    )
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
