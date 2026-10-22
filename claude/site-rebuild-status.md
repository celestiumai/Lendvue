# Lendvue Site Rebuild — Status

## Latest pass (Oct 22, 2026): whole-site fidelity pass, every page

Method: live DOM measured in Chrome (getComputedStyle / getBoundingClientRect at 1905px),
local build measured the same way with Playwright (`/home/claude/qa/measure.py` in that
session), then matched. Section heights now equal live on every page.

**Site-wide corrections (affected the homepage too):** UIkit container (1200 content,
15/30/40px gutters), body 16/24 #000, p margin 20, h2 line-height 1.3, sections 70px,
`--color-bg-alt` #FAFAFA, buttons 55px tall (14px/600, 0 40px), header 60px and NOT
sticky (live isn't), nav hover #666 / active #333 (no red underline), footer 3 equal
columns + 3-column bottom bar (13px #999, links #1E87F0), contact strip gradient
#366797→#0388F7 @74%, UIkit fraction math for 1/3–2/3 and 3/5 grids.

**Homepage fixes the previous pass got wrong:** hero 140px padding with no overlay
(live has none); service cards are hover tiles (no scrim at rest — scrim, zoom and
description only on hover); trust badges are the 2023/07 PNGs in a 5-column grid; steps
box is full-width text over a right-aligned background photo, sticking out 40px left;
testimonials section is white (not alt) and DOES show the word "Excellent"; feature
icons are the live inline SVGs (50px), not 24px webp files.

**Per page:** EF (hero photo 646add_1dbc…, 9 hover tiles with live photos + text),
BL (womanchefsmiling hero, 40px eligibility gap), VP (centered 210px hero, form band with
white 185px overlap strip, Gravity-style card form), About (gradient title band),
Contact (600/600 split card + map), Apply Now (program panels + both modals rebuilt
field-for-field from the live Gravity Forms), Current Inventory, legal pages (word-for-
word incl. the SMS Policy section ours was missing), landing funnel + thank-you pages
(previously plain EF copies).

**Deliberate deviations from live (tell the owner if asked):**
- Fixed obvious typos in copy ("Sounds Booths", "Telhandlers", "Concrete Pump, Trucks",
  "Doucsign", About's address labelled "By Phone" → "By Address").
- Current Inventory drops the dead currentinventory.net iframe.
- Contact map is a Google Maps embed (live: Leaflet/OSM) for the local-SEO signal.
- Thank-you pages: live repeats the testimonials block twice; included once. Thank-you
  pages stay noindex (live indexes them).
- Phone number in the contact strip is a tel: link styled as plain text.

**Form behaviour:** all forms validate before sending (were sending empty with
`novalidate`). Quote modals and the landing page email step-1 contact details
immediately (partial-entry equivalent). Landing step 2 includes step-1 details. gclid /
utm_* captured on arrival and attached to every submission as `attr_*` fields.
`/apply-now/#equipmentfinancing` and `#workingcapital` open the modals directly.


## Latest pass: pixel-exact homepage fidelity (computed-style methodology)

After the caching fix (below), the user did a fresh, properly-loaded comparison against
the real lendvue.com homepage and found the rebuild was still visually far off — wrong
button size/color, wrong hero photo with wrong shading, wrong icon sizes, wrong font
sizes/colors throughout, misaligned card titles, wrong steps photo, hand-built star icons
instead of the real Google-review graphics, wrong phone icon, wrong footer sizing.

**Methodology change**: instead of continuing screenshot-based comparison (which had
already been tried and still missed real defects), switched to extracting exact
`getComputedStyle()` / `getBoundingClientRect()` values directly from the live
lendvue.com DOM via browser JS, then matching those numbers precisely in our CSS. This
approach found things screenshots couldn't, including:

- The homepage hero photo was flat-out the wrong image. Found the real one by reading the
  `data-src` attribute off the live site's UIkit background-image div (no `<img>` tag, so
  `getComputedStyle().backgroundImage` alone couldn't find it):
  `34b8d7_2ae0ef88bffc4540bca71042ae936dd4mv2-2.webp` — a print-shop worker with safety
  glasses, arms crossed, blue machinery. This exact file was in the user's uploaded media
  zip. Saved as `assets/images/hero-print-shop-v2.webp` (new filename, not overwriting the
  old wrong one, both for cache-busting and to leave a paper trail).
- The "Get Financing in Three Simple Steps" photo should be `tarozenribg.webp` — a
  transparent-background (RGBA) cutout of a blonde woman in a cardigan holding a
  clipboard — not a rectangular bled photo. Saved as `assets/images/steps-photo-v2.webp`.
- The real site's testimonial "Excellent"/stars/Google-logo block isn't hand-built SVG —
  it's three real image assets: `rating-4-5-stars.webp` (150×22, already had a matching
  file on hand), a combined "Google Reviews ★★★★★" badge `wdv.webp` → saved as
  `assets/images/google-reviews-badge.webp` (99×40), and a plain 5-star row image
  `5stars.webp` → saved as `assets/images/stars-5.webp` (125×18, used identically on all
  three testimonial cards). There's no literal "Excellent" text on the real site — that
  was invented in an earlier pass and has been removed.
- New brand color discovered and added: `--color-accent-blue: #008AFC` (bright blue),
  distinct from the existing `--color-navy-light: #366796`. Used on: feature icons
  (50×50px), "Step 1/2/3" headings (24px/700), and footer "Explore"/"Contact" column
  headings (20px/700). `--color-navy-light` stays reserved for H2 section headings and the
  "Our Services" card overlay tint.
- Most body/description text on the real site is pure black `#000`, not the design
  system's `--color-muted` gray — fixed across `.lede`, `.feature-top p`, `.step p`,
  footer text.
- `.main-nav a` was a CSS scoping bug: the selector matched the "Apply Now" button too
  (nested inside `.main-nav`), so it inherited uppercase+letter-spacing meant only for the
  text nav links. Rescoped to `.main-nav ul a`; header button now gets its own
  `.header-cta .btn` rule (40px height, 0 30px padding, 14px font, no uppercase).
- "Our Services" cards: real site overlay is a full-card `rgba(54,103,150,0.8)` scrim
  (not a bottom-only gradient) with the title absolutely centered both axes at 24px/700 —
  fixed via `.service-card-overlay::after` + flex centering.
- Contact/CTA strip: real gradient is `--color-navy-light → --color-accent-blue` (was two
  unrelated blues), phone icon is a plain outline SVG with no circular border at 80×80
  (was a small circled icon) — replaced with the exact SVG path read off the live DOM,
  heading 24px/700 white, body 16px white.
- Trust-bar badges: 68px tall (was 40px). Footer logo: 159×35 to match the header (was
  28px tall). Footer headings: 20px/700/#008AFC (was ~17px/navy-light).
- Feature icons (`icon-no-risk.webp` etc.) were recolored in place from their old
  muted blue to the exact `rgb(0,138,252)` measured off the live site's SVG icons, sized
  to 50×50 in CSS. These files are shared across several pages (about, business-loans,
  equipment-financing, current-inventory), so the recolor is sitewide, which is correct
  since it's the real site's actual icon color everywhere, not homepage-specific.

Rebuilt, verified locally with Playwright (had to scroll the full page before capturing
since native `loading="lazy"` doesn't trigger for below-the-fold images in a single
full-page screenshot otherwise — the images themselves were fine, just an artifact of the
QA screenshot method), repackaged, and delivered the updated zip.

## Root cause found (prior pass): stale asset caching, not a CSS bug

`/_headers` sets `Cache-Control: public, max-age=31536000, immutable` on `/assets/*` and
image extensions with no cache-busting filenames, so redeployed CSS/JS under the same
filename kept being served stale to any browser that had loaded the site before.

**Fix**: `_build/build.py` now computes an MD5 hash of `assets/css/style.css` and
`assets/js/main.js` at build time and appends it as a `?v=<hash>` query string to their
tags in `_build/head.html` / `_build/foot.html`. Any content change automatically busts
the cache. Images edited in place must still be renamed (or suffixed) since they aren't
hash-versioned — this convention was used again in the latest pass (`-v2` suffixes).

## Next steps

- Once the homepage is confirmed correct against the live site, the same
  computed-style-extraction methodology should be applied page-by-page to
  equipment-financing, business-loans, vendor-partners, about, contact, apply-now, and
  current-inventory (explicit user sequencing: homepage first, fully correct, then the
  rest).
- Privacy Policy, Terms of Use, and the three thank-you pages still haven't been part of
  any visual audit pass.
- Voiceflow chatbot `projectID` is still a placeholder in `_build/foot.html` — needs the
  user's real Voiceflow Project ID pasted in, then re-run `python3 _build/build.py`.

## Workflow reminder

Any template/page/CSS/JS edit requires re-running `python3 _build/build.py` from the
project root (refreshes the CSS/JS cache-busting hash) before re-zipping/deploying. Image
edits under an existing filename need a renamed/suffixed file, not an in-place overwrite.
