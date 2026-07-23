# Camela Toe SEO Goal and Operating Plan

Last updated: 2026-07-23

## North-star goal

Build `https://camelatoe.com` into the clearest official source for the Camela
Toe brand and a genuinely useful, body-positive source for the search topic
“camel toe.”

Ranking first for the exact generic phrase is a long-term stretch goal. That
result is dominated by established dictionaries and reference sites, so the
practical sequence is:

1. Rank first for the exact brand name `Camela Toe`.
2. Earn visibility for specific questions such as `what does camel toe mean`
   and `camel toe in leggings`.
3. Expand authority and qualified search traffic before treating the generic
   head term as a realistic primary KPI.

No ranking is guaranteed. Success depends on indexing, usefulness, authority,
competition, and continued editorial work—not a one-time technical score.

## Implemented foundation

- One canonical origin: `https://camelatoe.com`.
- Self-referencing canonical and Open Graph URLs on indexable pages.
- Public positioning leads with full-body acceptance, natural confidence, and
  the freedom to feel comfortable in your own skin. Avoid `fictional Krakow
  persona`, `virtual creator`, `fake creator`, and AI-led ordinary profile
  copy. Use creator-project or brand framing instead of inventing a verified
  human biography.
- A real crawler-readable `robots.txt` and XML sitemap.
- A real `404.html`, preventing unknown URLs from returning homepage content.
- `noindex` on legal utility pages and the `camela-toe.pages.dev` mirror.
- `WebSite`, `ProfilePage`, `Organization`, `Article`, `BreadcrumbList`, and
  appropriate FAQ structured data.
- A topic hub plus two independently useful supporting guides.
- Descriptive internal links between the creator profile, topic hub, definition,
  and leggings guide.
- A 1200×630 social-sharing image.
- `scripts/validate_site_seo.py` enforced by the website deployment workflow.

## Immediate external setup

These are account/dashboard actions and must be checked after every domain or
hosting migration. The initial setup was completed on 2026-07-23:

1. **Google Search Console**
   - Domain property for `camelatoe.com`: **verified**.
   - Sole verified owner: **the Camela brand Google account**. Never use a
     NailedIT Games account for Camela website or search services.
   - Google DNS TXT verification for the Camela account: **installed through
     Cloudflare authorization**.
   - Previous non-Camela access and DNS token: **removed; 0 unused ownership
     tokens remain**.
   - `https://camelatoe.com/sitemap.xml`: **submitted successfully; 4 pages discovered**.
   - Initial indexing requests: **submitted for the homepage and all 3 guides**.
   - Do not repeatedly resubmit unchanged pages.
2. **Canonical hostname**
   - Cloudflare Redirect Rule is **active** so
     `https://www.camelatoe.com/*` returns a permanent redirect to
     `https://camelatoe.com/*`, preserving path and query string.
   - Keep the existing `.pl` redirect aliases pointed at the `.com` apex.
3. **Measurement**
   - Cloudflare Web Analytics: **enabled for the `camela-toe` Pages project
     and activated by a production deployment on 2026-07-23**.
   - The live `https://camelatoe.com/` response was verified to contain
     Cloudflare's injected analytics beacon.
   - Record Search Console queries, pages, countries, clicks, and impressions
     monthly. Cloudflare request counts are not a substitute for search data.

## Editorial roadmap

### Approval-first weekly automation

The private `ludek88/cemelatoe` repository owns the recurring editorial
orchestration. Once per week it may inspect Search Console, the current site,
and public search results, then update an existing guide or open one draft pull
request in this repository.

- Skip the run when another SEO editorial pull request remains open.
- Prefer improving an existing page when it already satisfies the query intent.
- Create at most one new article in a run and no more frequently than every
  seven days.
- Require original research or a clearly useful editorial contribution; do not
  publish a rewritten summary of competing pages.
- Add the sitemap entry, bidirectional internal links, metadata, structured
  data, and an existing approved first-party image or a separately reviewed
  public-safe editorial image.
- Run `python3 scripts/validate_site_seo.py` before opening the draft.
- Never auto-merge. Human approval of the draft PR is the publication gate;
  the existing `main` workflow then deploys the reviewed source.
- Link research may create a private opportunity report and outreach drafts,
  but sending messages or creating backlinks is never automatic.

### First 30 days

- Confirm all four sitemap URLs are indexed.
- Improve any page Google chooses not to index before creating more pages.
- Publish at most one or two strong additions based on real Search Console
  queries, not guessed keyword variants.
- Link to the relevant guide from new public social posts when it naturally
  answers the post’s topic.

### Days 31–90

- Review queries with impressions but low click-through rate; rewrite titles
  and descriptions only where they better match the page.
- Add original supporting material only when it supplies new value: garment
  construction diagrams, a photographed comparison, or a reviewed glossary.
- Seek legitimate citations and mentions from relevant fashion, activewear,
  body-positive, or creator publications. Do not buy bulk backlinks,
  exchange spammy links, or automate outreach comments.

### Months 4–12

- Update existing guides when they can become materially better.
- Build topical depth around proven demand rather than publishing hundreds of
  near-duplicate pages.
- Consider Polish, German, or Turkish versions only with fluent human review,
  separate URLs, self-canonicals, and correct `hreflang`.
- Reassess the generic head-term opportunity using actual Search Console and
  competitor data.

## Scorecard

Track monthly:

| Metric | First milestone | Later milestone |
|---|---:|---:|
| Valid sitemap pages indexed | 4 of 4 | Maintain 95%+ |
| Brand query position | Top 3 | Position 1 |
| Non-brand queries with impressions | Baseline | Sustained monthly growth |
| Long-tail queries in top 10 | First 3 | 20+ qualified queries |
| Organic clicks to Fanvue/Instagram CTAs | Baseline | Positive 3-month trend |
| Technical validation | 100% pass | Pass every deployment |

Also review conversions and engaged visits. A large request count can include
bots, asset requests, or low-intent traffic and is not the north-star metric.

## Editorial guardrails

- Write for an adult reader’s question, not for a keyword density target.
- Keep public pages non-graphic, respectful, body-positive, and medically
  cautious.
- Keep identity wording accurate without making AI terminology the focus of
  unrelated public copy; retain any legally or platform-required disclosure.
- Use original text and sources only where they genuinely help verification.
- Do not publish thin location pages, spun synonyms, hidden text, doorway pages,
  or artificial link schemes.
- Review every page visually and factually before deployment.
