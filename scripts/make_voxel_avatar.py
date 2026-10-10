"""Generate assets/avatar-3d.svg: an animated 3D voxel (pixel) portrait on a plain background.

Requires: pillow, numpy, opencv-python-headless
Usage: python3 scripts/make_voxel_avatar.py path/to/avatar.jpg [N]

The subject is cut out with GrabCut, which is seeded for a head-and-shoulders portrait
(face centred, shoulders along the bottom edge). Adjust the seeds for a different photo.
"""
import math
import random
import sys

import cv2
import numpy as np
from PIL import Image, ImageEnhance

src = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 56
S = 8.0            # screen size of one pixel (front face)
DEPTH = 15.0       # max extrusion
SHIFT = 0.27       # depth -> up/right offset of the front face
BUCKETS = 16
BG = "#101216"     # plain backdrop
random.seed(11)


def cutout(path):
    im = cv2.imread(path)
    side = min(im.shape[:2])
    im = im[:side, (im.shape[1] - side) // 2:(im.shape[1] - side) // 2 + side]
    h, w = im.shape[:2]
    m = np.full((h, w), cv2.GC_BGD, np.uint8)
    cv2.ellipse(m, (w // 2, int(h * .36)), (int(w * .27), int(h * .33)), 0, 0, 360, cv2.GC_PR_FGD, -1)
    cv2.ellipse(m, (w // 2, int(h * .64)), (int(w * .16), int(h * .14)), 0, 0, 360, cv2.GC_PR_FGD, -1)
    poly = np.array([[0, .80], [.30, .66], [.40, .60], [.66, .60], [.76, .62], [1, .76], [1, 1], [0, 1]]) * [w, h]
    cv2.fillPoly(m, [poly.astype(np.int32)], cv2.GC_PR_FGD)
    cv2.ellipse(m, (w // 2, int(h * .42)), (int(w * .14), int(h * .20)), 0, 0, 360, cv2.GC_FGD, -1)
    cv2.ellipse(m, (w // 2, int(h * .68)), (int(w * .08), int(h * .08)), 0, 0, 360, cv2.GC_FGD, -1)
    cv2.rectangle(m, (0, int(h * .88)), (w, h), cv2.GC_FGD, -1)
    cv2.grabCut(im, m, None, np.zeros((1, 65)), np.zeros((1, 65)), 10, cv2.GC_INIT_WITH_MASK)
    fg = np.where((m == 1) | (m == 3), 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
    return Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)), fg


img, fg = cutout(src)


def tone(img, stops=((0.0, (14, 15, 18)), (0.5, (128, 132, 140)), (1.0, (248, 249, 251)))):
    """Single-hue (white/grey) portrait: CLAHE on luminance, then map through a gradient."""
    g = np.asarray(img.convert("L"))
    g = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(6, 6)).apply(g).astype(float) / 255
    g = np.clip((g - 0.08) / 0.84, 0, 1) ** 1.15
    out = np.zeros(g.shape + (3,))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (g >= a) & (g <= b)
        t = ((g - a) / (b - a))[m][:, None]
        out[m] = np.array(ca) * (1 - t) + np.array(cb) * t
    return Image.fromarray(out.astype(np.uint8))


img = tone(img)
small = img.resize((N, N), Image.LANCZOS)
mask = cv2.resize(fg, (N, N), interpolation=cv2.INTER_AREA) > 127
dist = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 3)
dist = np.minimum(1.0, dist / (N * 0.16))
gray = np.asarray(small.convert("L"), dtype=float) / 255
gray = cv2.GaussianBlur(gray, (0, 0), 1.8)

PAD = 24
SHMAX = DEPTH * SHIFT
W = int(N * S + SHMAX + 2 * PAD)
H = W


def shade(c, k):
    return "#%02x%02x%02x" % tuple(min(255, int(v * k)) for v in c)


cells, drift, palette = [], [], []
for j in range(N):
    for i in range(N):
        c = small.getpixel((i, j))
        if not mask[j, i]:
            # sparse floating pixels just outside the silhouette
            near = mask[max(0, j - 2):j + 3, max(0, i - 2):i + 3].any()
            if near and random.random() < 0.05:
                drift.append((i, j, None))
            continue
        edge = not mask[max(0, j - 1):j + 2, max(0, i - 1):i + 2].all()
        if edge and j < N - 3 and random.random() < 0.18:
            drift.append((i, j, c))
            palette.append(c)
            continue
        depth = 1.5 + (gray[j, i] ** 1.4) * DEPTH * 0.35 + dist[j, i] * DEPTH * 0.65
        k = 1.0
        cells.append((i, j, tuple(min(255, int(v * k)) for v in c), depth))
cells.sort(key=lambda t: (round(t[3]), t[1], t[0]))

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mohamed Selim - 3D pixel avatar">',
     '<style>',
     '.f{animation:float 6s ease-in-out infinite alternate}',
     '@keyframes float{from{transform:translateY(-3px)}to{transform:translateY(4px)}}',
     '.s{animation:sweep 5s ease-in-out infinite}',
     '@keyframes sweep{0%{transform:translateX(-' + str(W) + 'px)}60%,100%{transform:translateX(' + str(int(W * 1.6)) + 'px)}}',
     '.p{animation:drift 6s ease-in-out infinite alternate}',
     '@keyframes drift{from{transform:translate(0,0);opacity:.9}to{transform:translate(8px,-18px);opacity:.25}}']
o.append('</style>')
o.append(f'''<defs>
<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="cp"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26"/></clipPath>
</defs>''')
o.append(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="26" fill="{BG}" stroke="#ffffff" stroke-opacity=".22" stroke-width="2"/>')
o.append('<g clip-path="url(#cp)"><g class="f">')
for i, j, c in drift:
    c = c or random.choice(palette)
    x = PAD + i * S + random.uniform(-8, 8)
    y = PAD + SHMAX + j * S - random.uniform(4, 22)
    sz = S * random.choice([0.5, 0.7, 0.9])
    o.append(f'<rect class="p" x="{x:.1f}" y="{y:.1f}" width="{sz:.1f}" height="{sz:.1f}" fill="{shade(c, 1.1)}"/>')
for i, j, c, dp in cells:
    x = PAD + i * S
    y = PAD + SHMAX + j * S
    sh = dp * SHIFT
    fx, fy = x + sh, y - sh
    left = f"{x:.1f},{y:.1f} {fx:.1f},{fy:.1f} {fx:.1f},{fy + S:.1f} {x:.1f},{y + S:.1f}"
    bottom = f"{x:.1f},{y + S:.1f} {fx:.1f},{fy + S:.1f} {fx + S:.1f},{fy + S:.1f} {x + S:.1f},{y + S:.1f}"
    o.append(f'<g><polygon points="{left}" fill="{shade(c, .88)}"/><polygon points="{bottom}" fill="{shade(c, .72)}"/><rect x="{fx:.1f}" y="{fy:.1f}" width="{S + .35:.1f}" height="{S + .35:.1f}" fill="{shade(c, 1.04)}"/></g>')
o.append('</g>')
o.append(f'<rect class="s" x="{-W * 0.2:.0f}" y="0" width="{W * 0.2:.0f}" height="{H}" fill="url(#sw)" transform="skewX(-18)"/></g>')
o.append('</svg>')
open("assets/avatar-3d.svg", "w").write("\n".join(o))
print(len(cells), "voxels,", len(drift), "particles,", W, H)
