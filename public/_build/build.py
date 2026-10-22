#!/usr/bin/env python3
"""Static site assembler for the Lendvue rebuild.
Combines _build/head.html + _build/pages/<slug>.html + _build/foot.html
into finished pages under the project root (Cloudflare Pages pretty-URL
layout: <slug>/index.html)."""
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "_build")


def file_hash(path, length=8):
    """Short content hash used to cache-bust /assets/* files that are served
    with a 1-year `immutable` Cache-Control header (see /_headers). Without
    this, redeploying new CSS/JS under the same filename leaves every browser
    (and Cloudflare's edge cache) serving the old cached copy indefinitely."""
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:length]


CSS_VER = file_hash(os.path.join(ROOT, "assets", "css", "style.css"))
JS_VER = file_hash(os.path.join(ROOT, "assets", "js", "main.js"))

with open(os.path.join(BUILD, "head.html"), encoding="utf-8") as f:
    HEAD = f.read().replace("$CSS_VER", CSS_VER)
with open(os.path.join(BUILD, "foot.html"), encoding="utf-8") as f:
    FOOT = f.read().replace("$JS_VER", JS_VER)

NAV_KEYS = ["equipment", "loans", "vendor", "about", "contact"]

# slug: output path relative to ROOT ("" = homepage -> index.html)
PAGES = [
    {
        "slug": "",
        "out": "index.html",
        "title": "Equipment Financing, Business Loans & Vendor Financing | Lendvue",
        "meta_desc": "Lendvue is a national online lender offering equipment financing, business loans, and vendor financing. Soft-pull pre-qualify in minutes, funded fast.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/",
        "og_title": "Small Business Financing Made Easy | Lendvue",
        "nav_active": None,
        "cta_band": True,
    },
    {
        "slug": "equipment-financing",
        "out": "equipment-financing/index.html",
        "title": "Equipment Financing | Terms from 24-72 Months | Lendvue",
        "meta_desc": "Equipment financing with little to no money down: 24-72 month terms, soft credit pull, and fast funding for construction, medical & commercial equipment.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/equipment-financing/",
        "og_title": "Equipment Financing Made Easy | Lendvue",
        "nav_active": "equipment",
        "cta_band": True,
    },
    {
        "slug": "business-loans",
        "out": "business-loans/index.html",
        "title": "Business Loans with Next-Day Funding | Lendvue",
        "meta_desc": "Unlock working capital with Lendvue's unsecured business loans. Flexible 3-18 month terms, soft credit pull, and funding as fast as next day.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/business-loans/",
        "og_title": "Business Loans with Next Day Funding | Lendvue",
        "nav_active": "loans",
        "cta_band": True,
    },
    {
        "slug": "vendor-partners",
        "out": "vendor-partners/index.html",
        "title": "Vendor Financing Partners | Boost Sales with Lendvue",
        "meta_desc": "Become a Lendvue vendor partner and offer in-house financing to your customers. Same-day approvals, 100% prefunding, and real-time transaction reporting.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/vendor-partners/",
        "og_title": "Generate More Sales with Lendvue Vendor Financing",
        "nav_active": "vendor",
        "cta_band": True,
    },
    {
        "slug": "about",
        "out": "about/index.html",
        "title": "About Lendvue | 20+ Years of Business Financing",
        "meta_desc": "Lendvue has funded over $250MM in equipment financing since 2002. A+ BBB rated, California licensed lender serving businesses in all 50 states.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/about/",
        "og_title": "About Lendvue | Small Business Financing Made Easy",
        "nav_active": "about",
        "cta_band": True,
    },
    {
        "slug": "contact",
        "out": "contact/index.html",
        "title": "Contact Lendvue | 800-866-7231",
        "meta_desc": "Contact Lendvue to explore tailored financing solutions in equipment financing, business loans, and vendor financing designed for your growth.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/contact/",
        "og_title": "Contact Lendvue",
        "nav_active": "contact",
        "cta_band": True,
    },
    {
        "slug": "apply-now",
        "out": "apply-now/index.html",
        "title": "Apply Now | Get Approved Today | Lendvue",
        "meta_desc": "Apply for equipment financing or a business loan with Lendvue. No obligation, no hard credit inquiries, and a decision within 24 hours.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/apply-now/",
        "og_title": "Get Approved Today | Lendvue",
        "nav_active": None,
        "cta_band": True,
        "extra_modals": True,
    },
    {
        "slug": "current-inventory",
        "out": "current-inventory/index.html",
        "title": "Equipment We Finance | Industries Served | Lendvue",
        "meta_desc": "See the full range of equipment Lendvue finances, from agricultural and construction to medical, manufacturing, and commercial vehicles.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/current-inventory/",
        "og_title": "Equipment We Finance | Lendvue",
        "nav_active": "equipment",
        "cta_band": True,
    },
    {
        "slug": "get-equipment-financing",
        "out": "get-equipment-financing/index.html",
        "title": "Equipment Financing Made Easy | Lendvue",
        "meta_desc": "Explore Lendvue for equipment financing solutions tailored to help your business acquire essential machinery, vehicles, and technology.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/equipment-financing/",
        "og_title": "Equipment Financing Made Easy | Lendvue",
        "nav_active": "equipment",
        "landing_header": True,
        "cta_band": True,
    },
    {
        "slug": "get-equipment-financing-2",
        "out": "get-equipment-financing-2/index.html",
        "title": "Equipment Financing Made Easy | Lendvue",
        "meta_desc": "Explore Lendvue for equipment financing solutions tailored to help your business acquire essential machinery, vehicles, and technology.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/equipment-financing/",
        "og_title": "Equipment Financing Made Easy | Lendvue",
        "nav_active": "equipment",
        "landing_header": True,
        "cta_band": True,
    },
    {
        "slug": "privacy-policy",
        "out": "privacy-policy/index.html",
        "title": "Privacy Policy | Lendvue",
        "meta_desc": "Read Lendvue's consumer and business privacy policy covering how we collect, use, and protect your personal and business information.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/privacy-policy/",
        "og_title": "Privacy Policy | Lendvue",
        "nav_active": None,
        "cta_band": False,
    },
    {
        "slug": "terms-of-use",
        "out": "terms-of-use/index.html",
        "title": "Terms of Use | Lendvue",
        "meta_desc": "Review the terms and conditions that govern your access to and use of the Lendvue website and services.",
        "robots": "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
        "canonical": "https://www.lendvue.com/terms-of-use/",
        "og_title": "Terms of Use | Lendvue",
        "nav_active": None,
        "cta_band": False,
    },
    {
        "slug": "thank-you",
        "out": "thank-you/index.html",
        "title": "Thank You | Lendvue",
        "meta_desc": "Thank you for contacting Lendvue. A member of our team will be in touch shortly.",
        "robots": "noindex, follow",
        "canonical": "https://www.lendvue.com/thank-you/",
        "og_title": "Thank You | Lendvue",
        "nav_active": None,
        "landing_header": True,
        "landing_cta": "/apply-now/",
        "cta_band": True,
    },
    {
        "slug": "thank-you-for-your-info",
        "out": "thank-you-for-your-info/index.html",
        "title": "Thank You | Lendvue",
        "meta_desc": "Thank you for submitting your information to Lendvue. We'll follow up shortly with your quote.",
        "robots": "noindex, follow",
        "canonical": "https://www.lendvue.com/thank-you-for-your-info/",
        "og_title": "Thank You | Lendvue",
        "nav_active": None,
        "cta_band": True,
    },
    {
        "slug": "thank-you-for-your-feedback",
        "out": "thank-you-for-your-feedback/index.html",
        "title": "Thank You | Lendvue",
        "meta_desc": "Thank you for your feedback. We appreciate you taking the time to reach out to Lendvue.",
        "robots": "noindex, follow",
        "canonical": "https://www.lendvue.com/thank-you-for-your-feedback/",
        "og_title": "Thank You | Lendvue",
        "nav_active": None,
        "cta_band": True,
    },
    {
        "slug": "404",
        "out": "404.html",
        "title": "Page Not Found | Lendvue",
        "meta_desc": "The page you're looking for may have moved or doesn't exist. Return to the Lendvue homepage or contact us for help.",
        "robots": "noindex, follow",
        "canonical": "https://www.lendvue.com/",
        "og_title": "Page Not Found | Lendvue",
        "nav_active": None,
        "cta_band": False,
        "body_source": "404",
    },
]


def render_head(cfg):
    html = HEAD
    schema_path = os.path.join(BUILD, "schema", f"{cfg['slug'] or 'home'}.html")
    schema = ""
    if os.path.exists(schema_path):
        with open(schema_path, encoding="utf-8") as f:
            schema = f.read()
    repl = {
        "$TITLE": cfg["title"],
        "$META_DESC": cfg["meta_desc"],
        "$ROBOTS": cfg["robots"],
        "$CANONICAL": cfg["canonical"],
        "$OG_TITLE": cfg["og_title"],
        "$SCHEMA": schema,
    }
    for key in NAV_KEYS:
        placeholder = "$NAV_" + key.upper()
        repl[placeholder] = ' aria-current="page"' if cfg.get("nav_active") == key else ""
    for k, v in repl.items():
        html = html.replace(k, v)
    if cfg.get("landing_header"):
        # PPC landing pages / funnel thank-you page use the live site's in-page anchor menu
        with open(os.path.join(BUILD, "partials", "landing-header.html"), encoding="utf-8") as f:
            landing = f.read().replace("$LANDING_CTA", cfg.get("landing_cta", "#getfinancing"))
        html = re.sub(r'<header class="site-header">.*?</header>\n', landing, html, flags=re.S)
    return html


def render_foot(cfg):
    html = FOOT
    cta_band = ""
    if cfg.get("cta_band"):
        cta_band = """<section class="contact-strip">
  <div class="container">
    <div class="contact-strip-text">
      <span class="contact-strip-icon">
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.01"><path d="M6.189,13.611C8.134,15.525 11.097,18.239 13.867,18.257C16.47,18.275 18.2,16.241 18.2,16.241L14.509,12.551L11.539,13.639L6.189,8.29L7.313,5.355L3.76,1.8C3.76,1.8 1.732,3.537 1.7,6.092C1.667,8.809 4.347,11.738 6.189,13.611"/></svg>
      </span>
      <div>
        <h3>Questions? Give us a call at <a href="tel:+18008667231">800-866-7231</a></h3>
        <p>We are available Monday through Friday, 9AM to 5PM PST</p>
      </div>
    </div>
    <a class="btn btn-primary" href="/contact/">Get in Touch</a>
  </div>
</section>"""
    extra_modals = ""
    if cfg.get("extra_modals"):
        modal_path = os.path.join(BUILD, "pages", "apply-now-modals.html")
        with open(modal_path, encoding="utf-8") as f:
            extra_modals = f.read()
    html = html.replace("$CTA_BAND", cta_band)
    html = html.replace("$EXTRA_MODALS", extra_modals)
    return html


INCLUDE_RE = re.compile(r"<!--#include ([\w-]+)-->")


def expand_includes(html):
    """Replace <!--#include name--> with _build/partials/name.html so shared
    blocks (testimonials, etc.) live in one file instead of being pasted per page."""
    def sub(m):
        with open(os.path.join(BUILD, "partials", m.group(1) + ".html"), encoding="utf-8") as f:
            return f.read().rstrip("\n")
    for _ in range(5):  # partials may include other partials
        if not INCLUDE_RE.search(html):
            break
        html = INCLUDE_RE.sub(sub, html)
    return html


def main():
    for cfg in PAGES:
        body_slug = cfg.get("body_source", cfg["slug"] or "home")
        body_path = os.path.join(BUILD, "pages", f"{body_slug}.html")
        with open(body_path, encoding="utf-8") as f:
            body = f.read()
        body = expand_includes(body)
        full = render_head(cfg) + body + render_foot(cfg)
        out_path = os.path.join(ROOT, cfg["out"])
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full)
        print("Built", cfg["out"])


if __name__ == "__main__":
    main()
