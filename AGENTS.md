# Camela Toe Website Agent Instructions

## Project Role

- This repository is the standalone public website project for
  `https://camelatoe.com`.
- The public source lives in `site/`.
- Production hosting is Cloudflare Pages project `camela-toe`.
- The canonical GitHub repository is
  `https://github.com/ludek88/cemelatoe-pages`.
- The expected local checkout is
  `/Users/maciej/Documents/cemelatoe-pages`.

## Related Content-Automation Project

- The private content and publishing automation repository is
  `https://github.com/ludek88/cemelatoe`.
- Its expected sibling checkout is `/Users/maciej/Documents/cemelatoe`.
- Shared Camela skills are version-controlled only in the private sibling at
  `../cemelatoe/.agents/skills`. Install them from that repository with
  `scripts/install_project_skills.py` so Codex can discover the same workflows
  while working in this public website repository on macOS or Windows. Do not
  duplicate skill source in this public repository.
- Before changing automation, providers, publishing, Telegram, scheduling,
  Fanvue, Instagram, Hedra, ElevenLabs, or Affogato behavior, read the sibling
  repository's `AGENTS.md` and make the change there.
- When one user request genuinely spans both projects, inspect both instruction
  files and use separate commits, tests, and direct pushes to each repository's
  `main`. Do not create a pull request unless the user explicitly asks for one.
- Never copy `.env`, runtime files, provider tokens, API keys, browser sessions,
  or private media between repositories.

## Routing Rules

- Website pages, HTML, CSS, public images, SEO, structured data, robots,
  sitemap, legal pages, website redirects, and website deployment belong here.
- Content generation, social captions, comments, collaborators, media
  workflows, provider clients, schedulers, Telegram controls, and social
  publishing belong in the sibling `cemelatoe` repository.
- If the user starts in the wrong project, continue in the correct sibling
  checkout when it exists instead of duplicating the feature.
- Keep cross-project references repo-relative where possible and document any
  changed interface or deployment assumption in both projects.

## Website Defaults

- Lead public About and profile copy with Camela Toe's mission: full-body
  acceptance, natural confidence, and the freedom to feel comfortable in your
  own skin, expressed through playful glamour, fitness, and fashion.
- Do not describe Camela publicly as a `fictional Krakow persona`, `virtual
  creator`, or `fake creator`, and do not lead ordinary profile copy with AI
  terminology. Use creator-project or brand framing when identity context is
  necessary, never invent a verified human biography, and keep any legally or
  platform-required disclosure accurate.
- Do not label ordinary public images, captions, profiles, or editorial copy as
  `AI-assisted` or `AI-generated`. Mention AI only when disclosure is legally or
  platform-required, or when the user explicitly asks for that context.
- Prefer `Body-positive fashion and creator content` for broader public brand
  summaries.
- Use the Camela brand account for Search Console and related website services;
  never use a NailedIT Games account.
- Keep `camelatoe.com` canonical. `www.camelatoe.com`, `camelatoe.pl`, and
  `www.camelatoe.pl` are redirect-only aliases.
- Keep the `pages.dev` mirror out of search results.
- Validate with `python3 scripts/validate_site_seo.py` before deployment.
- Recurring SEO editorial work is orchestrated from the private sibling
  repository. After the website diff passes validation and safety review,
  commit it directly to local `main` and push `origin main` without
  force-pushing. Create a pull request only when the user explicitly asks for
  one, and publish at most one new article per weekly run.
- Every new indexable article must add a canonical sitemap entry, useful
  bidirectional internal links, original people-first copy, first-party social
  preview imagery, and valid Article/Breadcrumb structured data. The validator
  discovers indexable `index.html` pages automatically and requires the sitemap
  to match them exactly.
- Deploy manually with
  `npx --yes wrangler pages deploy site --project-name camela-toe --branch main`
  or use `.github/workflows/deploy-site.yml` after this repository has its own
  Cloudflare GitHub Actions secrets.
- Do not enable a second automatic production deployment system unless it is
  intentional.

## Safety

- This repository is public. Do not commit personal account identifiers,
  Cloudflare account IDs, DNS verification tokens, secrets, cookies, or
  operational credentials.
- Keep the site public-safe, body-positive, non-graphic, and truthful without
  inventing a verified real-world biography or human identity.
- Do not automate bulk outreach, paid links, reciprocal-link schemes, comment
  backlinks, directory spam, or fabricated citations. Automated link research
  may prepare a private opportunity report and personalized drafts, but sending
  outreach requires explicit operator approval.
