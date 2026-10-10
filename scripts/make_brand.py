"""Regenerate the brand assets (header, footer, palette card, social preview).

Run from the repo root:  python3 scripts/make_brand.py
Logo paths are read from brand/logo.svg; colours and fonts live in the constants below.
"""
import random
import re

PRIMARY, ACCENT, ROYAL = "#1F6BFF", "#3DA5FF", "#0A5BFF"
BG, SURFACE, FG, MUTED = "#050B18", "#0B1428", "#F4F7FF", "#9AA8C3"
SANS = "'Plus Jakarta Sans','Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Consolas,monospace"
random.seed(5)

logo = open("brand/logo.svg").read()
LOGO_BODY = re.search(r"<svg[^>]*>(.*)</svg>", logo, re.S).group(1)
LOGO_VB = "140 255 995 765"


def logo_at(x, y, w):
    h = w * 765 / 995
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h:.0f}" viewBox="{LOGO_VB}" fill="none">{LOGO_BODY}</svg>'


def defs():
    return f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{SURFACE}"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{PRIMARY}" stop-opacity=".55"/><stop offset="1" stop-color="{PRIMARY}" stop-opacity="0"/></radialGradient>
<linearGradient id="w0" x1="0" x2="1"><stop offset="0" stop-color="{ROYAL}"/><stop offset="1" stop-color="{ACCENT}"/></linearGradient>
<linearGradient id="w1" x1="0" x2="1"><stop offset="0" stop-color="{ACCENT}"/><stop offset="1" stop-color="{PRIMARY}"/></linearGradient>
<linearGradient id="w2" x1="0" x2="1"><stop offset="0" stop-color="{PRIMARY}"/><stop offset="1" stop-color="{ROYAL}"/></linearGradient>
<linearGradient id="tx" x1="0" x2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="{ACCENT}"/></linearGradient>
</defs>'''


def waves(h, base, animate=True):
    out = ""
    for i, (op, dur, amp) in enumerate([(0.2, 9, 22), (0.32, 7, 16), (0.5, 5, 10)]):
        y = base + i * 14
        d, x = f"M-200,{y} ", -200
        while x < 1400:
            d += f"q150,{-amp} 300,0 t300,0 "
            x += 600
        anim = (f'<animateTransform attributeName="transform" type="translate" from="0 0" to="-600 0" dur="{dur * 2}s" repeatCount="indefinite"/>' if animate else "")
        out += f'<path d="{d}V{h} H-200 Z" fill="url(#w{i})" opacity="{op}">{anim}</path>\n'
    return out


def stars(n, w, h):
    s = ""
    for _ in range(n):
        s += (f'<circle cx="{random.randint(0, w)}" cy="{random.randint(0, h)}" r="{random.choice([1, 1.3, 1.8])}" fill="#fff">'
              f'<animate attributeName="opacity" values="0.1;0.9;0.1" dur="{random.uniform(2, 5):.1f}s" begin="{random.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>\n')
    return s


# ---- header -------------------------------------------------------------
header = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="280" viewBox="0 0 1000 280" role="img" aria-label="Mohamed Selim - Full-Stack Developer">
{defs()}
<rect width="1000" height="280" rx="14" fill="url(#bg)"/>
<circle cx="190" cy="125" r="190" fill="url(#glow)"><animate attributeName="opacity" values="0.55;1;0.55" dur="5s" repeatCount="indefinite"/></circle>
<g>{stars(40, 1000, 190)}</g>
<g>{waves(280, 215)}</g>
{logo_at(70, 50, 240)}
<line x1="350" y1="62" x2="350" y2="190" stroke="{ACCENT}" stroke-opacity=".4" stroke-width="2"/>
<g font-family="{SANS}">
<text x="385" y="108" font-size="52" font-weight="800" fill="url(#tx)" letter-spacing="1">MOHAMED SELIM<animate attributeName="opacity" values="0;1" dur="1.2s" fill="freeze"/></text>
<text x="387" y="146" font-size="19" fill="#cfe0ff" letter-spacing="2.5">FULL-STACK DEVELOPER  •  WEB &amp; ML<animate attributeName="opacity" values="0;1" dur="2s" fill="freeze"/></text>
<text x="387" y="178" font-size="15" fill="{ACCENT}" font-family="{MONO}">&lt;/&gt; I build things that actually work<animate attributeName="opacity" values="0;1" dur="2.8s" fill="freeze"/></text>
</g></svg>'''

# ---- footer -------------------------------------------------------------
footer = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="130" viewBox="0 0 1000 130" aria-hidden="true">
{defs()}
{waves(130, 70)}
{logo_at(460, 6, 80)}
</svg>'''

# ---- palette / typography card -----------------------------------------
chips = [("Primary", PRIMARY), ("Accent", ACCENT), ("Royal", ROYAL), ("Background", BG), ("Surface", SURFACE), ("Foreground", FG), ("Muted", MUTED)]
cw = 124
chip_svg = ""
for k, (name, hexv) in enumerate(chips):
    x = 40 + k * (cw + 10)
    txt = "#050B18" if name in ("Foreground", "Muted", "Accent") else "#F4F7FF"
    chip_svg += (f'<rect x="{x}" y="150" width="{cw}" height="92" rx="12" fill="{hexv}" stroke="#ffffff" stroke-opacity=".14"/>'
                 f'<text x="{x + 12}" y="206" font-family="{SANS}" font-size="13" font-weight="700" fill="{txt}">{name}</text>'
                 f'<text x="{x + 12}" y="226" font-family="{MONO}" font-size="12" fill="{txt}" opacity=".85">{hexv}</text>')
palette = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="400" viewBox="0 0 1000 400" role="img" aria-label="Brand palette and typography">
<rect width="1000" height="400" rx="16" fill="{BG}" stroke="#ffffff" stroke-opacity=".12"/>
{logo_at(40, 26, 128)}
<g font-family="{SANS}">
<text x="200" y="64" font-size="26" font-weight="800" fill="{FG}">Mohamed Selim — Brand Identity</text>
<text x="200" y="90" font-size="14" fill="{MUTED}">Blue on deep navy. Sharp, technical, confident.</text>
<text x="40" y="142" font-size="12" font-weight="700" fill="{ACCENT}" letter-spacing="2">COLOUR</text>
</g>
{chip_svg}
<g font-family="{SANS}">
<text x="40" y="276" font-size="12" font-weight="700" fill="{ACCENT}" letter-spacing="2">TYPOGRAPHY</text>
<text x="40" y="316" font-size="30" font-weight="800" fill="{FG}">Plus Jakarta Sans</text><text x="40" y="340" font-size="12" fill="{MUTED}">Headings · 600 / 700 / 800</text>
<text x="340" y="316" font-size="30" font-weight="500" fill="{FG}" font-family="Inter,{SANS}">Inter</text><text x="340" y="340" font-size="12" fill="{MUTED}">Body text · 400 / 500</text>
<text x="520" y="316" font-size="21" fill="{FG}" font-family="{MONO}">&lt;/&gt; JetBrains Mono</text><text x="520" y="340" font-size="12" fill="{MUTED}">Code and labels</text>
<text x="790" y="316" font-size="26" fill="{FG}" font-family="'IBM Plex Sans Arabic',{SANS}">محمد سليم</text><text x="790" y="340" font-size="12" fill="{MUTED}">IBM Plex Sans Arabic</text>
</g>
<rect x="40" y="362" width="920" height="3" rx="1.5" fill="url(#w0)"/>
{defs()}
</svg>'''

# ---- social preview (1280x640) -----------------------------------------
social = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640">
{defs()}
<rect width="1280" height="640" fill="url(#bg)"/>
<circle cx="330" cy="300" r="380" fill="url(#glow)"/>
<g>{stars(70, 1280, 470)}</g>
<g transform="translate(0,360) scale(1.28,1)">{waves(280, 130, animate=False)}</g>
{logo_at(110, 150, 420)}
<line x1="590" y1="190" x2="590" y2="430" stroke="{ACCENT}" stroke-opacity=".4" stroke-width="3"/>
<g font-family="{SANS}">
<text x="640" y="278" font-size="74" font-weight="800" fill="url(#tx)">Mohamed Selim</text>
<text x="644" y="332" font-size="30" fill="#cfe0ff" letter-spacing="3">FULL-STACK DEVELOPER</text>
<text x="644" y="384" font-size="24" fill="{ACCENT}" font-family="{MONO}">&lt;/&gt; I build things that actually work</text>
</g></svg>'''

for path, body in [("assets/header.svg", header), ("assets/footer.svg", footer), ("assets/brand-palette.svg", palette), ("brand/social-preview.svg", social)]:
    open(path, "w").write(body)
    print("wrote", path, len(body))
