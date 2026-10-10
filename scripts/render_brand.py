"""Render the brand SVGs in brand/ to PNG with headless Chromium (needs pillow).

Run from the repo root:  python3 scripts/render_brand.py
"""
import glob
import os
import re
import subprocess
import tempfile

from PIL import Image

CHROME = glob.glob("/opt/pw-browsers/chromium*/chrome-linux*/chrome")[0]
JOBS = {  # svg -> (png, width, height)
    "brand/avatar.svg": ("brand/avatar.png", 1000, 1000),
    "brand/favicon.svg": ("brand/favicon-180.png", 180, 180),
    "brand/linkedin-banner.svg": ("brand/linkedin-banner.png", 1584, 396),
    "brand/business-card-front.svg": ("brand/business-card-front.png", 1050, 600),
    "brand/business-card-back.svg": ("brand/business-card-back.png", 1050, 600),
    "brand/social-preview.svg": ("brand/social-preview.png", 1280, 640),
}
for src, (dst, w, h) in JOBS.items():
    svg = re.sub(r"<animate[^>]*/>", "", open(src).read())
    with tempfile.TemporaryDirectory() as d:
        sp, shot = os.path.join(d, "a.svg"), os.path.join(d, "a.png")
        # scale the root svg to the target size so small icons stay sharp
        svg = re.sub(r'width="\d+" height="\d+"', f'width="{w}" height="{h}"', svg, count=1)
        open(sp, "w").write(svg)
        subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        f"--screenshot={shot}", f"--window-size={w},{h + 200}", "file://" + sp],
                       check=True, capture_output=True)
        Image.open(shot).crop((0, 0, w, h)).save(dst)
    print("rendered", dst)
