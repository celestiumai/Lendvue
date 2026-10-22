# Lendvue Website — Static Rebuild

This is a full rebuild of lendvue.com as plain HTML/CSS/JS — no WordPress, no theme
bloat, no plugins. It's built for **Cloudflare Pages** and designed so you (or Claude)
can keep editing it directly as code going forward.

## What's here

```
/                          - homepage
/equipment-financing/      - service page
/business-loans/           - service page
/vendor-partners/          - service page + inline application form
/about/
/contact/                  - contact form
/apply-now/                - the two "Get My Free Quote" modal forms
/current-inventory/        - equipment/industries directory
/get-equipment-financing/  - legacy landing page (canonical -> /equipment-financing/)
/get-equipment-financing-2/ - legacy landing page (canonical -> /equipment-financing/)
/privacy-policy/
/terms-of-use/
/thank-you/, /thank-you-for-your-info/, /thank-you-for-your-feedback/  - noindex confirmation pages
/404.html
/assets/css/style.css      - the entire design system, one file
/assets/js/main.js         - mobile nav, modal system, multi-step form logic, AJAX submit
/assets/images/            - real images pulled from your current media library, compressed to WebP
/functions/api/submit-form.js  - Cloudflare Pages Function that emails form submissions
/sitemap.xml, /robots.txt, /_headers, /_redirects
/_build/                   - the source templates (see "Editing the site" below)
```

## 1. Deploying to Cloudflare Pages

1. Push this folder to a GitHub/GitLab repo (or use `wrangler pages deploy` directly from
   this folder — no build command needed, it's already static HTML).
2. In the Cloudflare dashboard: **Workers & Pages → Create → Pages → Connect to Git**
   (or Direct Upload if you don't want to use a repo).
3. Build settings: **no framework, no build command, output directory = `/`** (project root).
4. Add your custom domain (`www.lendvue.com` and `lendvue.com`) under the Pages project's
   **Custom Domains** tab, and point your DNS at Cloudflare per their instructions.

## 2. Making the contact forms work (Resend)

The site is deployed as a **Cloudflare Worker** (`wrangler.jsonc` at the repo root).
Pages in `public/` are served as static assets; only `/api/submit-form` runs code
(`worker/submit-form.js`), which emails each submission to you via
[Resend](https://resend.com) (free tier: 100 emails/day). `public/.assetsignore` keeps
`_build/`, `_incoming/` and this README from being published.

To activate it:

1. Create a free Resend account and verify `lendvue.com` by adding the DNS records
   Resend gives you (add them next to your existing records — don't replace any).
2. Create an API key in Resend (sending access). It starts with `re_`.
3. Cloudflare dashboard -> Workers & Pages -> **lendvue** -> Settings -> Variables and
   Secrets, add:
   - `RESEND_API_KEY` — type **Secret**, the key from step 2
   - `TO_EMAIL` — inbox that receives leads (e.g. `info@lendvue.com`)
   - `FROM_EMAIL` — address on the verified domain (e.g. `forms@lendvue.com`)
   `ALLOWED_ORIGIN` is already set in `wrangler.jsonc` (www.lendvue.com, lendvue.com and
   the workers.dev preview). Add any new domain there.
4. Submit each form once to confirm the emails arrive.

Deploys: every push to `main` on GitHub is built and deployed by Cloudflare
(Workers Builds, deploy command `npx wrangler deploy`, root directory = repo root).

## 3. Chatbot (Voiceflow)

Your Voiceflow widget is wired into every page (`_build/foot.html`, near the bottom).
I couldn't pull your live Project ID automatically (the browser tooling blocks extracting
what looks like an API credential, even a public client-side one). Open your Voiceflow
dashboard, copy your **Project ID**, and paste it in:

```
_build/foot.html   ->  verify: { projectID: 'YOUR_VOICEFLOW_PROJECT_ID' }
```

then run `python3 _build/build.py` again to regenerate every page (see below).

## 4. Images

Images actually used across the site (logo, trust badges, hero photo, industry photos,
icons, rating badge) were pulled from the media zip you uploaded, compressed, and
converted to WebP in `assets/images/`. Unused files from that zip were left out per your
instructions. If you add new photos later, drop them in `assets/images/`, keep them under
~150KB (WebP, `quality=75-85` is a good default), and reference them with `loading="lazy"`
unless they're above the fold.

## 5. SEO notes

- Every page has a unique title/meta description, a single H1, self-referencing canonical
  tag, Open Graph + Twitter card tags, and JSON-LD (sitewide `FinancialService`
  Organization schema, plus per-page `Service`/`BreadcrumbList`/`ContactPage` schema).
- `/get-equipment-financing/` and `/get-equipment-financing-2/` are kept live (in case
  they have inbound links or ad traffic pointing at them) but canonicalize to
  `/equipment-financing/` to avoid duplicate-content issues.
- The old `/test/` page (empty WordPress scratch page) was dropped and 301-redirected
  to the homepage.
- Thank-you pages are `noindex` and excluded from `sitemap.xml`, which is standard
  practice for post-form confirmation pages.
- I did **not** add review/rating schema (`AggregateRating`) since I don't have a real,
  verifiable review count — fabricated rating markup is treated as spam by Google. Add it
  once you have a real number from Google Business Profile or similar (see the comment in
  `_build/schema/home.html`).
- Copy, layout, and imagery were checked page-by-page directly against the live
  lendvue.com and corrected to match: header/footer, the blue post-hero badge strip,
  the full-bleed "Our Services" cards, the icon-top "Reasons to Choose Lendvue" grid,
  the light-blue "Three Simple Steps" card, the testimonials layout, and the CTA/footer
  bar all follow the real site's structure rather than a stylistic reinterpretation.

## 6. Editing the site going forward

Every page is built from three pieces so the header/footer/nav only need to change in one
place:

- `_build/head.html` — shared `<head>` + header/nav (has `$TITLE`, `$META_DESC`, etc.
  placeholders)
- `_build/pages/<name>.html` — that page's unique body content
- `_build/foot.html` — shared footer + scripts
- `_build/partials/<name>.html` — shared blocks (testimonials, industry tiles, landing-page
  header/body, SVG icons) inserted with `<!--#include name-->`
- `_build/legal/*.txt` — Privacy Policy / Terms text; run `python3 _build/legal/gen.py`
  after editing them

After editing any of those, regenerate the actual site files with:

```
python3 _build/build.py
```

This overwrites `index.html`, `about/index.html`, etc. from the templates (and refreshes
the cache-busting `?v=` hash on the CSS/JS) — it's safe to run any time. **Don't hand-edit
the generated `index.html` files**: the next build overwrites them. Always edit `_build/`
and rebuild.

## 7. Security

- `_headers` sets HSTS, a Content-Security-Policy, X-Frame-Options, and long-cache
  headers for static assets.
- Forms have a honeypot field plus server-side field-length/shape validation in the
  Cloudflare Function.
- No inline secrets anywhere in the codebase — the Resend key lives only in Cloudflare's
  environment variables.
- If the chatbot or any third-party script stops working after deploy, it's most likely
  the CSP in `_headers` being stricter than that script needs — loosen the relevant
  `script-src`/`connect-src` entry rather than removing the header entirely.
