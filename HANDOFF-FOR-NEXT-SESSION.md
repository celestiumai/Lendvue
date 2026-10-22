# Lendvue Site Rebuild — Handoff Doc

Read this first. This project is a from-scratch static rebuild of **www.lendvue.com**
(currently WordPress) as plain HTML/CSS/JS — no WordPress, no theme bloat, no plugins —
deployed as a Cloudflare Worker (static assets + one /api route; see wrangler.jsonc), using best SEO practices, with working contact/apply forms.
This zip is a snapshot of that work so far, handed off from a previous session.

## Start here

1. Read `README.md` in this zip — it explains the folder structure, how to deploy to
   Cloudflare Pages, and how the contact forms work (Cloudflare Pages Function + Resend,
   replacing Gravity Forms).
2. Read `claude/site-rebuild-status.md` — the detailed running log of what's been fixed
   and why, including exact measured CSS values pulled from the live site.
3. Read `claude/Calebs-SEO-Knowledgebase.md` — the SEO knowledge base this rebuild is
   supposed to follow.
4. Then read this doc's "Current status" and "How to continue" sections below.

## Current status (updated Oct 22, 2026)

**Every page has had the computed-style fidelity pass** against the live site at a 1905px
viewport: home, equipment-financing, business-loans, vendor-partners, about, contact,
apply-now (+ both quote modals), current-inventory, privacy-policy, terms-of-use, the
landing funnel (/get-equipment-financing/, /get-equipment-financing-2/) and all three
thank-you pages. Section-by-section heights and key element positions match live to
within 1px. See `claude/site-rebuild-status.md` for what changed and the deliberate
deviations from live.

The repo is **github.com/celestiumai/Lendvue** (site lives in `public/`; these docs live
at the repo root so they are never deployed). Work is committed and pushed to `main`.

## The methodology that actually worked (use this, not screenshots)

Screenshot-based visual comparison was tried first and repeatedly missed real defects
(wrong font sizes, wrong colors, wrong image files) that *looked* plausible in a
screenshot but weren't pixel-accurate. What actually worked: opening the real
**www.lendvue.com** page in a browser and running JavaScript against the live DOM to
extract exact values, e.g.:

```js
const el = document.querySelector('...');
const cs = getComputedStyle(el);
({ fontSize: cs.fontSize, fontWeight: cs.fontWeight, color: cs.color,
   textTransform: cs.textTransform, letterSpacing: cs.letterSpacing });
el.getBoundingClientRect(); // exact px width/height
```

Then matching those exact numbers in `assets/css/style.css`. This caught things like:
buttons inheriting the wrong CSS rule because of an overly broad selector, a whole brand
color (`#008AFC`) that wasn't in the design system at all, body text that should be pure
black `#000` instead of the design system's gray, and a background image applied via a
`data-src` attribute (UIkit lazy-load pattern) that plain `computed.backgroundImage`
inspection completely missed.

**If the next environment can drive a real browser (e.g. has Chrome/Playwright/DevTools
access), repeat this exact technique page by page**: for every element the site owner
flags as wrong, measure the real element on lendvue.com first, then match the CSS. Don't
trust a screenshot-only comparison — it isn't precise enough for "exact copy" fidelity,
which is explicitly what's been asked for.

If the next environment can't drive a browser, ask the user for exact measurements/colors
(or new screenshots with a ruler/inspector open), rather than guessing.

## Known site-wide facts already discovered (reuse these — don't re-derive)

- Two distinct blues: `--color-navy-light: #366796` (H2 headings, "Our Services" card
  overlay tint) vs. the newer `--color-accent-blue: #008AFC` (icons, step numbers, footer
  column headings). Don't conflate them.
- Most body/description text on the real site is pure black `#000`, not gray.
- Real nav links: `#303030`, 14px, uppercase, weight 500, normal letter-spacing (not the
  heavier styling that was originally guessed).
- Site was apparently migrated from Wix at some point — asset filenames in the media
  library follow a `xxxxxx_hash_mv2.webp` Wix naming convention even though the current
  site is WordPress/UIkit/YOOtheme. Useful when searching the source media zip contents
  for a specific live-site image (match by hash in the filename, read via the live DOM's
  `data-src`/`src` attributes, strip query strings before comparing).
- Source photography/graphics live under `_incoming/` in this zip (extracted from the
  user's WordPress media library export) — check there before assuming an image doesn't
  exist. Assets already promoted into `assets/images/` are the ones currently in use;
  everything else in `_incoming/` is unprocessed raw material for pages not yet fixed.

## Build process (don't skip this)

This is a templated static site, not hand-written HTML per page:

```
_build/head.html + _build/pages/<slug>.html + _build/foot.html  →  <slug>/index.html
```

Shared blocks live in `_build/partials/` and are pulled in with `<!--#include name-->`
(partials may include partials): testimonials, industry-tiles, landing-header,
landing-body, and every SVG icon (`icon-*.html`, copied path-for-path from live).
Legal pages are generated from plain text: edit `_build/legal/privacy.txt` /
`terms.txt`, run `python3 _build/legal/gen.py`, then `python3 _build/build.py`.

After ANY change to a page, template, or `assets/css/style.css` / `assets/js/main.js`,
re-run from the project root:

```
python3 _build/build.py
```

This regenerates every page AND recomputes the cache-busting hash on the CSS/JS URLs
(`?v=<hash>` — see `_build/build.py`). **Never hand-edit the generated `index.html` files
directly** — edit the templates in `_build/` and rebuild, or your changes will be
overwritten and out of sync.

If you edit an image in place under an *existing* filename, rename it (add a `-v2`
suffix or similar) and update its references — `/_headers` sets 1-year immutable caching
on all image extensions, so same-filename edits won't be visible to returning visitors
after deploy.

## Outstanding items

- (done) Voiceflow chatbot `projectID` set to 64d40070fec0d1000682be7e — was a placeholder
  (`YOUR_VOICEFLOW_PROJECT_ID`) — needs the real project ID from the site owner, then
  rebuild.
- Current Inventory: live embeds www.currentinventory.net, which has lapsed (GoDaddy
  parking page). The embed was dropped; ask the owner if there is a replacement feed.
- Forms need RESEND_API_KEY (secret) / TO_EMAIL / FROM_EMAIL set on the **lendvue Worker**
  (Settings -> Variables and Secrets). Preview URL: https://lendvue.brian-b4c.workers.dev/
