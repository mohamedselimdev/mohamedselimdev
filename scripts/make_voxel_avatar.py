"""Generate assets/avatar-3d.svg: an animated 3D voxel (pixel) portrait from an avatar.

Usage: python3 scripts/make_voxel_avatar.py path/to/avatar.jpg [N]
"""
import math
import random
import sys
from PIL import Image, ImageEnhance, ImageFilter

src = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 56
S = 8.0            # screen size of one pixel (front face)
DEPTH = 15.0       # max extrusion
SHIFT = 0.27       # depth -> up/right offset of the front face
BUCKETS = 16
random.seed(11)

img = Image.open(src).convert("RGB")
w, h = img.size
side = min(w, h)
img = img.crop(((w - side) // 2, 0, (w - side) // 2 + side, side))
img = ImageEnhance.Contrast(img).enhance(1.18)
img = ImageEnhance.Color(img).enhance(1.25)
img = ImageEnhance.Sharpness(img).enhance(1.4)
small = img.resize((N, N), Image.LANCZOS)
smooth = img.convert("L").filter(ImageFilter.GaussianBlur(side / N * 0.9)).resize((N, N), Image.LANCZOS)

PAD = 26
SHMAX = DEPTH * SHIFT
W = int(N * S + SHMAX + 2 * PAD)
H = W
R = N / 2


def shade(c, k):
    return "#%02x%02x%02x" % tuple(min(255, int(v * k)) for v in c)


cells, drift = [], []
for i in range(N):
    for j in range(N):
        d = math.hypot(i + 0.5 - R, j + 0.5 - R) / R
        if d > 1.0:
            continue
        if d > 0.86 and random.random() < (d - 0.86) / 0.14 * 0.85:
            if random.random() < 0.18:
                drift.append((i, j, small.getpixel((i, j))))
            continue
        c = small.getpixel((i, j))
        lum = smooth.getpixel((i, j)) / 255
        dome = max(0.0, 1 - d * d)
        depth = 1.5 + (lum ** 1.4) * DEPTH * 0.7 + dome * DEPTH * 0.3
        # soft vignette on colour, lighter in the upper-left
        k = 1.06 - 0.22 * d * d + 0.08 * (1 - (i + j) / (2 * N))
        c = tuple(min(255, int(v * k)) for v in c)
        cells.append((i, j, c, depth))
cells.sort(key=lambda t: (round(t[3]), t[1], t[0]))

o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mohamed Selim - 3D pixel avatar">',
     '<style>',
     '.v{animation:rise 10s cubic-bezier(.2,.8,.2,1) infinite backwards}',
     '@keyframes rise{0%{transform:translate(-26px,46px) scale(.4);opacity:0}14%{transform:none;opacity:1}90%{transform:none;opacity:1}100%{transform:none;opacity:0}}',
     '.f{animation:float 6s ease-in-out infinite alternate}',
     '@keyframes float{from{transform:translateY(-4px)}to{transform:translateY(5px)}}',
     '.g{animation:glow 4s ease-in-out infinite alternate}',
     '@keyframes glow{from{opacity:.4}to{opacity:.95}}',
     '.s{animation:sweep 5s ease-in-out infinite}',
     '@keyframes sweep{0%{transform:translateX(-' + str(W) + 'px)}60%,100%{transform:translateX(' + str(W * 1.6) + 'px)}}',
     '.p{animation:drift 6s ease-in-out infinite alternate}',
     '@keyframes drift{from{transform:translate(0,0);opacity:.9}to{transform:translate(8px,-18px);opacity:.25}}']
for b in range(BUCKETS):
    o.append(f'.d{b}{{animation-delay:{b * 0.11:.2f}s}}')
o.append('</style>')
o.append(f'''<defs>
<radialGradient id="gl" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#00e5ff" stop-opacity=".6"/><stop offset=".6" stop-color="#7c4dff" stop-opacity=".25"/><stop offset="1" stop-color="#7c4dff" stop-opacity="0"/></radialGradient>
<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".32"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="sh"><stop offset="0" stop-color="#000" stop-opacity=".5"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
<clipPath id="cp"><circle cx="{W / 2:.1f}" cy="{H / 2:.1f}" r="{W / 2 - PAD + 6:.1f}"/></clipPath>
</defs>''')
o.append(f'<circle class="g" cx="{W / 2:.1f}" cy="{H / 2:.1f}" r="{W / 2:.1f}" fill="url(#gl)"/>')
o.append(f'<ellipse cx="{W / 2:.1f}" cy="{H - PAD + 6:.1f}" rx="{W * 0.32:.1f}" ry="{PAD * 0.6:.1f}" fill="url(#sh)"/>')
o.append('<g class="f">')
for i, j, c in drift:
    x = PAD + i * S + random.uniform(-10, 10)
    y = PAD + SHMAX + j * S - random.uniform(6, 26)
    sz = S * random.choice([0.5, 0.7, 0.9])
    o.append(f'<rect class="p d{random.randrange(BUCKETS)}" x="{x:.1f}" y="{y:.1f}" width="{sz:.1f}" height="{sz:.1f}" fill="{shade(c, 1.1)}"/>')
maxs = 2 * (N - 1)
for i, j, c, dp in cells:
    x = PAD + i * S
    y = PAD + SHMAX + j * S
    sh = dp * SHIFT
    fx, fy = x + sh, y - sh
    bk = min(BUCKETS - 1, int(math.hypot(i - R, j - R) / R * BUCKETS))
    left = f"{x:.1f},{y:.1f} {fx:.1f},{fy:.1f} {fx:.1f},{fy + S:.1f} {x:.1f},{y + S:.1f}"
    bottom = f"{x:.1f},{y + S:.1f} {fx:.1f},{fy + S:.1f} {fx + S:.1f},{fy + S:.1f} {x + S:.1f},{y + S:.1f}"
    o.append(f'<g class="v d{bk}"><polygon points="{left}" fill="{shade(c, .88)}"/><polygon points="{bottom}" fill="{shade(c, .72)}"/><rect x="{fx:.1f}" y="{fy:.1f}" width="{S + .35:.1f}" height="{S + .35:.1f}" fill="{shade(c, 1.04)}"/></g>')
o.append('</g>')
o.append(f'<g clip-path="url(#cp)"><rect class="s" x="{-W * 0.2:.0f}" y="0" width="{W * 0.2:.0f}" height="{H}" fill="url(#sw)" transform="skewX(-18)"/></g>')
o.append('</svg>')
open("assets/avatar-3d.svg", "w").write("\n".join(o))
print(len(cells), "voxels,", len(drift), "particles,", W, H)
