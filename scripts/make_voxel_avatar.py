"""Generate assets/avatar-3d.svg: an animated isometric voxel (3D pixel) version of an avatar.

Usage: python3 scripts/make_voxel_avatar.py path/to/avatar.jpg [N]
"""
import math
import sys
from PIL import Image

src = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 38
S = 12.0                  # screen size of one pixel (front face)
HMIN, HMAX = 2.0, 17.0    # extrusion depth range driven by brightness
SHIFT = 0.42              # how far depth shifts the front face (up-right)
BUCKETS = 14

img = Image.open(src).convert("RGB")
w, h = img.size
side = min(w, h)
img = img.crop(((w - side) // 2, 0, (w - side) // 2 + side, side)).resize((N, N), Image.LANCZOS)

PAD = 14
SHMAX = HMAX * SHIFT
W, H = int(N * S + SHMAX + 2 * PAD), int(N * S + SHMAX + 2 * PAD)


def shade(c, k):
    return "#%02x%02x%02x" % tuple(int(v * k) for v in c)


r = N / 2 - 0.3
cells = []
for i in range(N):
    for j in range(N):
        if math.hypot(i + 0.5 - N / 2, j + 0.5 - N / 2) > r:
            continue
        c = img.getpixel((i, j))
        lum = (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255
        cells.append((i, j, c, HMIN + lum * (HMAX - HMIN)))
cells.sort(key=lambda t: (t[3], t[1], t[0]))

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mohamed Selim - 3D pixel avatar">',
       '<style>',
       '.v{animation:rise 9s ease-out infinite backwards}',
       '@keyframes rise{0%{transform:translate(-30px,40px);opacity:0}16%{transform:translate(0,0);opacity:1}88%{transform:translate(0,0);opacity:1}100%{transform:translate(0,0);opacity:0}}',
       '.f{animation:float 5s ease-in-out infinite alternate}',
       '@keyframes float{from{transform:translateY(-3px)}to{transform:translateY(4px)}}',
       '.g{animation:glow 4s ease-in-out infinite alternate}',
       '@keyframes glow{from{opacity:.35}to{opacity:.8}}']
for b in range(BUCKETS):
    out.append(f'.d{b}{{animation-delay:{b * 0.13:.2f}s}}')
out.append('</style>')
out.append('<defs><radialGradient id="gl"><stop offset="0" stop-color="#00e5ff" stop-opacity=".55"/><stop offset="1" stop-color="#7c4dff" stop-opacity="0"/></radialGradient></defs>')
out.append(f'<circle class="g" cx="{W / 2:.0f}" cy="{H / 2:.0f}" r="{W / 2:.0f}" fill="url(#gl)"/>')
out.append('<g class="f">')
for i, j, c, ht in cells:
    x = PAD + i * S
    y = PAD + SHMAX + j * S
    sh = ht * SHIFT
    fx, fy = x + sh, y - sh
    bk = min(BUCKETS - 1, int((i + j) / (2 * (N - 1)) * BUCKETS))
    left = f"{x:.1f},{y:.1f} {fx:.1f},{fy:.1f} {fx:.1f},{fy + S:.1f} {x:.1f},{y + S:.1f}"
    bottom = f"{x:.1f},{y + S:.1f} {fx:.1f},{fy + S:.1f} {fx + S:.1f},{fy + S:.1f} {x + S:.1f},{y + S:.1f}"
    out.append(f'<g class="v d{bk}"><polygon points="{left}" fill="{shade(c, .78)}"/><polygon points="{bottom}" fill="{shade(c, .6)}"/><rect x="{fx:.1f}" y="{fy:.1f}" width="{S + .3:.1f}" height="{S + .3:.1f}" fill="{shade(c, 1)}"/></g>')
out.append('</g></svg>')
open("assets/avatar-3d.svg", "w").write("\n".join(out))
print(len(cells), "voxels", W, H)
