# Camela Toe Website

This repository is the standalone static website project for `camelatoe.com`.

Production hosting is Cloudflare Pages project `camela-toe`. The `.pl` domain
is a redirect-only alias to the `.com` site, not a second copy of the website.

The related private content and publishing automation project is
[`ludek88/cemelatoe`](https://github.com/ludek88/cemelatoe). Keep both
repositories as sibling local checkouts:

```text
/Users/maciej/Documents/cemelatoe-pages   website
/Users/maciej/Documents/cemelatoe         content automation
```

Each repository contains an `AGENTS.md` file that routes cross-project work to
the correct checkout. A request spanning both projects must use separate
branches, commits, tests, and pull requests.

## Files

- `site/index.html` - public Camela Toe landing page.
- `site/camel-toe/index.html` - body-positive topic hub.
- `site/camel-toe/meaning/index.html` - definition and respectful-language guide.
- `site/camel-toe/leggings/index.html` - leggings construction and fit guide.
- `site/privacy.html` - privacy page kept for Meta/app review and direct links.
- `site/data-deletion.html` - data deletion page kept for Meta/app review.
- `site/404.html` - real not-found page with `noindex`.
- `site/robots.txt` - crawler access and canonical sitemap location.
- `site/sitemap.xml` - only the four public, indexable canonical pages.
- `site/_headers` - security/cache headers and `noindex` for `pages.dev`.
- `site/CNAME` - custom domain declaration for `camelatoe.com`.
- `site/assets/` - optimized public image assets.
- `docs/` - deployment and SEO operating notes.
- `scripts/validate_site_seo.py` - local and CI validation.

Current homepage-specific assets:

- `site/assets/favicon.svg` - browser favicon matching the CT header mark.
- `site/assets/favicon-180.png` - touch icon generated from the same CT mark.
- `site/assets/camela-social-card.png` - 1200×630 Open Graph/social preview.
- `site/assets/camela-bedroom-knit.jpg` - bedroom glamour portrait used in the
  follow/exclusive section. Keep descriptive filenames instead of generic or
  stale names such as `camela-beach.jpg`.

## Local Preview

```bash
python3 -m http.server 9876 --bind 127.0.0.1 --directory site
```

Open:

```text
http://127.0.0.1:9876/
```

Run the same technical SEO contract used by CI:

```bash
python3 scripts/validate_site_seo.py
```

The validator checks unique titles and descriptions, self-referencing
canonicals, robots directives, Open Graph URLs, valid JSON-LD, internal links,
image dimensions, the sitemap, the real 404 page, and `pages.dev` index
protection. Update the validator and sitemap whenever a new indexable page is
added.

## Deployment

Manual deploy:

```bash
npx --yes wrangler pages deploy site --project-name camela-toe --branch main
```

GitHub Actions workflow:

```text
.github/workflows/deploy-site.yml
```

The workflow validates required files on `main` pushes that touch `site/**`.
Automatic Cloudflare deployment runs only after these GitHub Actions repository
secrets are configured in **this** repository:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Until those secrets are present, the workflow intentionally skips deployment
instead of failing.

## Domains

Canonical:

```text
https://camelatoe.com/
```

Redirect aliases, preserving path and query:

```text
https://www.camelatoe.com/
https://camelatoe.pl/
https://www.camelatoe.pl/
```

All aliases should 301 to `https://camelatoe.com`. Do not serve a second copy
on `www`, `.pl`, or `pages.dev`. Cloudflare Pages `_redirects` does not support
domain-level redirects, so manage hostname redirects with Cloudflare Redirect
Rules/Bulk Redirects. The `_headers` file provides a second line of defense by
marking `camela-toe.pages.dev` as `noindex`.

## Notes

Keep the homepage public-safe and creator-focused. The private/paid content call
to action should point to Fanvue without explicit public-page wording.

Keep topic articles useful, original, body-positive, and reviewed by a person.
Do not mass-produce keyword variants or promise health outcomes. The operating
roadmap and measurement plan live in `docs/WEBSITE_SEO_PLAN.md`.
