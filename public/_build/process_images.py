import os
from PIL import Image, ImageOps

SRC = "/home/claude/lendvue-site/_incoming"
DST = "/home/claude/lendvue-site/assets/images"
os.makedirs(DST, exist_ok=True)

def save_webp(im, path, quality=82, max_w=None):
    im = im.convert("RGBA") if im.mode in ("P", "LA") else im
    if max_w and im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), Image.LANCZOS)
    if im.mode == "RGBA":
        im.save(path, "WEBP", quality=quality, method=6)
    else:
        im.convert("RGB").save(path, "WEBP", quality=quality, method=6)
    print(path, im.size, os.path.getsize(path), "bytes")

def save_png(im, path, max_w=None):
    if max_w and im.width > max_w:
        ratio = max_w / im.width
        im = im.resize((max_w, int(im.height * ratio)), Image.LANCZOS)
    im.save(path, "PNG", optimize=True)
    print(path, im.size, os.path.getsize(path), "bytes")

MAP = [
    # (source relative path, dest filename, max_w, format)
    ("2023/06/lvlogo.webp", "lendvue-logo.webp", 320, "webp"),
    ("2024/02/Lendvue-Logo-white-small.png", "lendvue-logo-white.webp", 320, "webp"),
    ("2023/09/Favicon2.png", "favicon-32.png", None, "png"),
    ("2023/06/4.5-stars.webp", "rating-4-5-stars.webp", 300, "webp"),
    ("2023/07/ssl.webp", "badge-ssl.webp", 240, "webp"),
    ("2023/07/dbo.webp", "badge-dbo.webp", 240, "webp"),
    ("2023/07/bbb.webp", "badge-bbb.webp", 240, "webp"),
    ("2023/07/google.webp", "badge-google.webp", 240, "webp"),
    ("2023/07/docusign.webp", "badge-docusign.webp", 240, "webp"),
    ("2026/07/24-year-small.png", "badge-24-years-bbb.png", 400, "png"),
    ("2023/11/FOUROFFIVE-Silver.png", "badge-four-of-five-approved.png", 400, "png"),
    ("2023/08/equipmentfinancingguy.webp", "service-equipment-financing.webp", 700, "webp"),
    ("2023/06/home20page202_edited.webp", "service-business-loans.webp", 700, "webp"),
    ("2023/06/71416533_5_edited.webp", "service-vendor-partners.webp", 700, "webp"),
    ("2023/06/tractor_edited.webp", "industry-agricultural.webp", 700, "webp"),
    ("2023/06/Truck-driving-on-the-road_edited.webp", "industry-commercial-vehicle.webp", 700, "webp"),
    ("2023/09/Computer-Equipment.webp", "industry-computer.webp", 700, "webp"),
    ("2023/06/Cat_edited_edited.webp", "industry-construction.webp", 700, "webp"),
    ("2023/06/Making-Pasta_edited.webp", "industry-food-prep.webp", 700, "webp"),
    ("2023/06/Laser-Cutting_edited.webp", "industry-manufacturing.webp", 700, "webp"),
    ("2023/09/Medical-Equipment.webp", "industry-medical.webp", 700, "webp"),
    ("2023/06/Print-is-Alive_edited.webp", "industry-printing.webp", 700, "webp"),
    ("2023/06/checkmarkicon.webp", "icon-no-risk.webp", 120, "webp"),
    ("2023/06/clockturnaroundicon.webp", "icon-quick-turnaround.webp", 120, "webp"),
    ("2023/06/aplusratedicon.webp", "icon-a-plus-rated.webp", 120, "webp"),
    ("2023/06/licensedlendoricon.webp", "icon-licensed-lender.webp", 120, "webp"),
    ("2023/06/experienceicon.webp", "icon-experience.webp", 120, "webp"),
    ("2023/06/secureicon.webp", "icon-secure.webp", 120, "webp"),
    ("2023/06/fastflexibleicon.webp", "icon-fast-flexible.webp", 120, "webp"),
    ("2023/06/flexibletermsicon.webp", "icon-flexible-terms.webp", 120, "webp"),
    ("2023/06/taxsavingsicon.webp", "icon-tax-savings.webp", 120, "webp"),
    ("2023/06/prefundingicon.webp", "icon-prefunding.webp", 120, "webp"),
    ("2023/06/realtimereportingicon.webp", "icon-realtime-reporting.webp", 120, "webp"),
    ("2023/06/signatureicon.webp", "icon-signature.webp", 120, "webp"),
    ("2023/06/widecreditwindowicon.webp", "icon-wide-credit-window.webp", 120, "webp"),
]

for src_rel, dest_name, max_w, fmt in MAP:
    src_path = os.path.join(SRC, src_rel)
    if not os.path.exists(src_path):
        print("MISSING:", src_path)
        continue
    im = Image.open(src_path)
    dest_path = os.path.join(DST, dest_name)
    if fmt == "webp":
        save_webp(im, dest_path, max_w=max_w)
    else:
        save_png(im, dest_path, max_w=max_w)
