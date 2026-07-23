# Camela Toe Website Deployment

Last reviewed: 2026-07-23

## Project Boundary

The public website source lives in `site/` in the standalone repository:

```text
GitHub: https://github.com/ludek88/cemelatoe-pages
Local:  /Users/maciej/Documents/cemelatoe-pages
```

The related private content and publishing automation project is:

```text
GitHub: https://github.com/ludek88/cemelatoe
Local:  /Users/maciej/Documents/cemelatoe
```

Website HTML, CSS, images, SEO, legal pages, and deployment belong here.
Providers, media generation, captions, comments, schedulers, Telegram, and
social publishing belong in the private sibling repository. Read both
`AGENTS.md` files for requests that span the boundary.

## Production

- Canonical site: `https://camelatoe.com`
- Cloudflare Pages project: `camela-toe`
- Production branch: `main`
- Build output directory: `site`
- Framework preset: none
- Canonical Search Console property: `camelatoe.com`

Redirect-only aliases:

```text
https://www.camelatoe.com
https://camelatoe.pl
https://www.camelatoe.pl
```

All aliases must return a permanent redirect to the same path and query on
`https://camelatoe.com`. Do not serve a second website copy from an alias.

## Local Validation

Run:

```bash
python3 scripts/validate_site_seo.py
```

Preview locally:

```bash
python3 -m http.server 9876 --bind 127.0.0.1 --directory site
```

Open `http://127.0.0.1:9876/`.

The validator discovers all indexable `index.html` pages and checks unique
metadata, self-canonical URLs, Open Graph data, JSON-LD, internal links, image
dimensions, exact sitemap coverage, robots rules, a real 404 page, and
`pages.dev` noindex protection.

## Manual Cloudflare Deployment

From the website repository:

```bash
npx --yes wrangler pages deploy site \
  --project-name camela-toe \
  --branch main
```

Wrangler must be authenticated to the Camela Cloudflare account. Never commit
credentials, tokens, account IDs, browser sessions, or local Wrangler state.
For token-based local authentication, copy `.env.example` to `.env`, add the
two values locally, and export them into the current shell before running
Wrangler. Alternatively, use `wrangler login`; no `.env` file is required for
browser-based Wrangler authentication.

macOS or Linux:

```bash
export CLOUDFLARE_ACCOUNT_ID="your-account-id"
export CLOUDFLARE_API_TOKEN="your-scoped-api-token"
```

Windows PowerShell:

```powershell
$env:CLOUDFLARE_ACCOUNT_ID = "your-account-id"
$env:CLOUDFLARE_API_TOKEN = "your-scoped-api-token"
```

After deployment, verify:

```bash
curl -fsS https://camelatoe.com/robots.txt
curl -fsS https://camelatoe.com/sitemap.xml
curl -I https://camelatoe.com/does-not-exist
curl -I https://camela-toe.pages.dev/
curl -I https://www.camelatoe.com/
```

Expected:

- `robots.txt` is plain text and declares the canonical sitemap.
- `sitemap.xml` contains only canonical public pages.
- an unknown path returns HTTP 404.
- the `pages.dev` response includes `X-Robots-Tag: noindex, nofollow`.
- `www` permanently redirects to the apex while preserving path and query.

## GitHub Actions

The workflow is `.github/workflows/deploy-site.yml`.

It validates relevant pushes to `main` and then deploys `site/`. The deploy
fails visibly instead of silently skipping when either required Actions secret
is missing:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

GitHub secrets do not transfer between repositories. Use a dedicated
account-scoped API token with only Cloudflare Pages Read and Pages Write
permissions for the Camela account. Never reuse an R2 access key or a broader
personal token. The two repository secrets were configured on 2026-07-23;
rotate them in GitHub and Cloudflare together when required.

Do not also enable Cloudflare dashboard Git integration unless duplicate
production deploy systems are intentional.

## Search Console

Completed on 2026-07-23:

- the Domain property is verified under the Camela brand Google account;
- no non-Camela owner or unused ownership token remains;
- `https://camelatoe.com/sitemap.xml` was submitted successfully;
- Search Console discovered four canonical pages;
- initial indexing requests were submitted for all four pages;
- the live homepage test reported that the URL is available to Google.

Search Console may need time to process indexing data. Do not repeatedly submit
unchanged URLs. Use `docs/WEBSITE_SEO_PLAN.md` for the ongoing roadmap.

## Public Repository Safety

This repository is public. Keep operational notes free of:

- personal Google account identifiers;
- Cloudflare account IDs and API tokens;
- DNS ownership-verification values;
- cookies, OAuth tokens, or local browser state;
- private content media or machine-local runtime files.

Generic mail-routing facts may be documented when needed, but mailbox access
details belong in the private content repository or the operator's password
manager.
