"""
utils.py — Frame builder, filter, strip renderer
6 frame lucu dengan layout & karakter berbeda, semua digambar pakai PIL
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import io
import os
import math
import random

# ── Font helper ───────────────────────────────────────────────────────────────
def _font(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def _font_r(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

# ── Filters ───────────────────────────────────────────────────────────────────
FILTERS = {
    "Natural":    lambda i: i,
    "Soft":       lambda i: _soft(i),
    "Warm":       lambda i: _warm(i),
    "Cool":       lambda i: _cool(i),
    "B&W":        lambda i: _bw(i),
    "Vintage":    lambda i: _vintage(i),
    "Vivid":      lambda i: _vivid(i),
    "Faded":      lambda i: _faded(i),
}

from PIL import ImageEnhance, ImageOps

def _soft(img):
    return ImageEnhance.Contrast(img).enhance(0.85)

def _warm(img):
    r, g, b = img.split()
    r = r.point(lambda x: min(255, int(x * 1.18)))
    g = g.point(lambda x: min(255, int(x * 1.05)))
    b = b.point(lambda x: int(x * 0.85))
    return Image.merge("RGB", (r, g, b))

def _cool(img):
    r, g, b = img.split()
    r = r.point(lambda x: int(x * 0.88))
    b = b.point(lambda x: min(255, int(x * 1.18)))
    return Image.merge("RGB", (r, g, b))

def _bw(img):
    return ImageOps.grayscale(img).convert("RGB")

def _vintage(img):
    img = ImageOps.grayscale(img).convert("RGB")
    r, g, b = img.split()
    r = r.point(lambda x: min(255, int(x * 1.12)))
    b = b.point(lambda x: int(x * 0.88))
    img = Image.merge("RGB", (r, g, b))
    return ImageEnhance.Contrast(img).enhance(0.88)

def _vivid(img):
    img = ImageEnhance.Color(img).enhance(1.9)
    return ImageEnhance.Contrast(img).enhance(1.2)

def _faded(img):
    img = ImageEnhance.Contrast(img).enhance(0.7)
    img = ImageEnhance.Color(img).enhance(0.6)
    return ImageEnhance.Brightness(img).enhance(1.1)

def apply_filter(img: Image.Image, name: str) -> Image.Image:
    fn = FILTERS.get(name, lambda i: i)
    return fn(img.convert("RGB"))

# ── Drawing helpers ───────────────────────────────────────────────────────────

def _circle(draw, cx, cy, r, fill, outline=None, width=2):
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill=fill, outline=outline, width=width)

def _star(draw, cx, cy, r, fill):
    pts = []
    for i in range(10):
        angle = math.pi * i / 5 - math.pi / 2
        radius = r if i % 2 == 0 else r * 0.45
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    draw.polygon(pts, fill=fill)

def _heart(draw, cx, cy, size, fill):
    pts = []
    for t in range(0, 360, 5):
        rad = math.radians(t)
        x = size * 16 * (math.sin(rad) ** 3)
        y = -size * (13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad))
        pts.append((cx + x, cy + y))
    draw.polygon(pts, fill=fill)

def _sparkle(draw, cx, cy, r, fill):
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        x1, y1 = cx + r*0.25*math.cos(rad-math.pi/2), cy + r*0.25*math.sin(rad-math.pi/2)
        x2, y2 = cx + r*math.cos(rad), cy + r*math.sin(rad)
        x3, y3 = cx + r*0.25*math.cos(rad+math.pi/2), cy + r*0.25*math.sin(rad+math.pi/2)
        draw.polygon([(cx,cy),(x1,y1),(x2,y2),(x3,y3)], fill=fill)

def _cloud(draw, cx, cy, w, h, fill):
    draw.ellipse([(cx-w//2, cy-h//3), (cx+w//2, cy+h//3)], fill=fill)
    draw.ellipse([(cx-w//3, cy-h//2), (cx+w//6, cy+h//6)], fill=fill)
    draw.ellipse([(cx, cy-h//2.5), (cx+w//2.5, cy+h//6)], fill=fill)

# ── Character drawers ──────────────────────────────────────────────────────────

def _draw_bunny(draw, cx, cy, size, color="#FFB7C5"):
    """Kelinci cute"""
    s = size
    # Telinga
    draw.ellipse([(cx-s*0.5, cy-s*1.6), (cx-s*0.15, cy-s*0.7)], fill=color, outline="#fff", width=1)
    draw.ellipse([(cx+s*0.15, cy-s*1.6), (cx+s*0.5, cy-s*0.7)], fill=color, outline="#fff", width=1)
    draw.ellipse([(cx-s*0.4, cy-s*1.5), (cx-s*0.2, cy-s*0.8)], fill="#ffcdd2")
    draw.ellipse([(cx+s*0.2, cy-s*1.5), (cx+s*0.4, cy-s*0.8)], fill="#ffcdd2")
    # Badan
    draw.ellipse([(cx-s*0.6, cy-s*0.7), (cx+s*0.6, cy+s*0.7)], fill=color)
    # Muka
    draw.ellipse([(cx-s*0.5, cy-s*0.9), (cx+s*0.5, cy+s*0.1)], fill=color)
    # Mata
    _circle(draw, cx-s*0.18, cy-s*0.5, s*0.09, "#2c1810")
    _circle(draw, cx+s*0.18, cy-s*0.5, s*0.09, "#2c1810")
    _circle(draw, cx-s*0.14, cy-s*0.54, s*0.04, "white")
    _circle(draw, cx+s*0.22, cy-s*0.54, s*0.04, "white")
    # Hidung
    _circle(draw, cx, cy-s*0.3, s*0.07, "#ff8fa3")
    # Pipi
    _circle(draw, cx-s*0.3, cy-s*0.2, s*0.12, "#ffcdd2", None)
    _circle(draw, cx+s*0.3, cy-s*0.2, s*0.12, "#ffcdd2", None)

def _draw_bear(draw, cx, cy, size, color="#b5906e"):
    """Beruang mungil"""
    s = size
    # Telinga
    _circle(draw, cx-s*0.42, cy-s*0.75, s*0.22, color)
    _circle(draw, cx+s*0.42, cy-s*0.75, s*0.22, color)
    _circle(draw, cx-s*0.42, cy-s*0.75, s*0.13, "#d4a87a")
    _circle(draw, cx+s*0.42, cy-s*0.75, s*0.13, "#d4a87a")
    # Kepala
    _circle(draw, cx, cy-s*0.4, s*0.55, color)
    # Moncong
    draw.ellipse([(cx-s*0.25, cy-s*0.2), (cx+s*0.25, cy+s*0.1)], fill="#d4a87a")
    # Mata
    _circle(draw, cx-s*0.2, cy-s*0.52, s*0.09, "#2c1810")
    _circle(draw, cx+s*0.2, cy-s*0.52, s*0.09, "#2c1810")
    _circle(draw, cx-s*0.16, cy-s*0.56, s*0.04, "white")
    _circle(draw, cx+s*0.24, cy-s*0.56, s*0.04, "white")
    # Hidung
    _circle(draw, cx, cy-s*0.12, s*0.07, "#7b4a2d")
    # Badan
    draw.ellipse([(cx-s*0.5, cy+s*0.1), (cx+s*0.5, cy+s*0.9)], fill=color)

def _draw_ghost(draw, cx, cy, size, color="#e8e0ff"):
    """Hantu lucu"""
    s = size
    # Badan
    pts = [
        (cx-s*0.45, cy+s*0.5),
        (cx-s*0.45, cy-s*0.2),
        (cx-s*0.3, cy-s*0.6),
        (cx, cy-s*0.75),
        (cx+s*0.3, cy-s*0.6),
        (cx+s*0.45, cy-s*0.2),
        (cx+s*0.45, cy+s*0.5),
        (cx+s*0.3, cy+s*0.35),
        (cx+s*0.15, cy+s*0.5),
        (cx, cy+s*0.35),
        (cx-s*0.15, cy+s*0.5),
        (cx-s*0.3, cy+s*0.35),
    ]
    draw.polygon(pts, fill=color)
    # Mata
    _circle(draw, cx-s*0.18, cy-s*0.2, s*0.1, "#7c5cbf")
    _circle(draw, cx+s*0.18, cy-s*0.2, s*0.1, "#7c5cbf")
    _circle(draw, cx-s*0.14, cy-s*0.24, s*0.04, "white")
    _circle(draw, cx+s*0.22, cy-s*0.24, s*0.04, "white")
    # Mulut
    draw.arc([(cx-s*0.15, cy-s*0.05), (cx+s*0.15, cy+s*0.12)], 0, 180, fill="#7c5cbf", width=3)

def _draw_frog(draw, cx, cy, size, color="#7ecb6e"):
    """Kodok lucu"""
    s = size
    # Badan
    _circle(draw, cx, cy+s*0.1, s*0.55, color)
    # Kepala
    _circle(draw, cx, cy-s*0.3, s*0.5, color)
    # Mata menonjol
    _circle(draw, cx-s*0.25, cy-s*0.7, s*0.2, color)
    _circle(draw, cx+s*0.25, cy-s*0.7, s*0.2, color)
    _circle(draw, cx-s*0.25, cy-s*0.7, s*0.13, "white")
    _circle(draw, cx+s*0.25, cy-s*0.7, s*0.13, "white")
    _circle(draw, cx-s*0.25, cy-s*0.72, s*0.08, "#1a1a2e")
    _circle(draw, cx+s*0.25, cy-s*0.72, s*0.08, "#1a1a2e")
    # Mulut
    draw.arc([(cx-s*0.2, cy-s*0.15), (cx+s*0.2, cy+s*0.05)], 0, 180, fill="#5aad4e", width=3)
    # Pipi
    _circle(draw, cx-s*0.32, cy-s*0.15, s*0.1, "#a5d97a")
    _circle(draw, cx+s*0.32, cy-s*0.15, s*0.1, "#a5d97a")

def _draw_cat(draw, cx, cy, size, color="#f9a8d4"):
    """Kucing manis"""
    s = size
    # Telinga segitiga
    draw.polygon([(cx-s*0.45, cy-s*0.6), (cx-s*0.6, cy-s*1.1), (cx-s*0.1, cy-s*0.75)], fill=color)
    draw.polygon([(cx+s*0.45, cy-s*0.6), (cx+s*0.6, cy-s*1.1), (cx+s*0.1, cy-s*0.75)], fill=color)
    draw.polygon([(cx-s*0.4, cy-s*0.65), (cx-s*0.52, cy-s*1.0), (cx-s*0.15, cy-s*0.75)], fill="#ffcdd2")
    draw.polygon([(cx+s*0.4, cy-s*0.65), (cx+s*0.52, cy-s*1.0), (cx+s*0.15, cy-s*0.75)], fill="#ffcdd2")
    # Kepala
    _circle(draw, cx, cy-s*0.4, s*0.55, color)
    # Mata
    _circle(draw, cx-s*0.2, cy-s*0.5, s*0.1, "#2d6a4f")
    _circle(draw, cx+s*0.2, cy-s*0.5, s*0.1, "#2d6a4f")
    _circle(draw, cx-s*0.16, cy-s*0.54, s*0.04, "white")
    _circle(draw, cx+s*0.24, cy-s*0.54, s*0.04, "white")
    # Hidung
    draw.polygon([(cx, cy-s*0.28), (cx-s*0.08, cy-s*0.18), (cx+s*0.08, cy-s*0.18)], fill="#e91e8c")
    # Kumis
    draw.line([(cx-s*0.5, cy-s*0.22), (cx-s*0.1, cy-s*0.22)], fill="#e91e8c", width=2)
    draw.line([(cx+s*0.1, cy-s*0.22), (cx+s*0.5, cy-s*0.22)], fill="#e91e8c", width=2)
    draw.line([(cx-s*0.48, cy-s*0.15), (cx-s*0.12, cy-s*0.18)], fill="#e91e8c", width=2)
    draw.line([(cx+s*0.12, cy-s*0.18), (cx+s*0.48, cy-s*0.15)], fill="#e91e8c", width=2)
    # Badan
    draw.ellipse([(cx-s*0.5, cy+s*0.1), (cx+s*0.5, cy+s*0.85)], fill=color)

def _draw_chick(draw, cx, cy, size, color="#ffe082"):
    """Anak ayam imut"""
    s = size
    # Badan bulat
    _circle(draw, cx, cy+s*0.15, s*0.5, color)
    # Kepala
    _circle(draw, cx, cy-s*0.35, s*0.42, color)
    # Sayap kecil
    draw.ellipse([(cx-s*0.7, cy+s*0.0), (cx-s*0.35, cy+s*0.45)], fill="#ffd54f")
    draw.ellipse([(cx+s*0.35, cy+s*0.0), (cx+s*0.7, cy+s*0.45)], fill="#ffd54f")
    # Mata
    _circle(draw, cx-s*0.18, cy-s*0.42, s*0.09, "#1a1a2e")
    _circle(draw, cx+s*0.18, cy-s*0.42, s*0.09, "#1a1a2e")
    _circle(draw, cx-s*0.14, cy-s*0.46, s*0.04, "white")
    _circle(draw, cx+s*0.22, cy-s*0.46, s*0.04, "white")
    # Paruh
    draw.polygon([(cx-s*0.08, cy-s*0.26), (cx+s*0.08, cy-s*0.26), (cx, cy-s*0.16)], fill="#ff8f00")
    # Jengger
    draw.ellipse([(cx-s*0.08, cy-s*0.78), (cx+s*0.08, cy-s*0.65)], fill="#ef5350")

# ═══════════════════════════════════════════════════════════════════════════════
# FRAME DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

FRAMES = {
    "🌸 Sakura Bunny": {
        "n_photos": 2,
        "layout": "vertical_2",
        "desc": "2 foto · Pink & bunga",
        "bg": "#fff5f7",
        "accent": "#ff8fab",
        "accent2": "#ffc2d1",
    },
    "⭐ Starry Bear": {
        "n_photos": 4,
        "layout": "vertical_4",
        "desc": "4 foto · Biru bintang",
        "bg": "#f0f4ff",
        "accent": "#7b9cff",
        "accent2": "#c5d5ff",
    },
    "🍭 Candy Ghost": {
        "n_photos": 6,
        "layout": "grid_2x3",
        "desc": "6 foto · Warna warni",
        "bg": "#fff8e7",
        "accent": "#ff9d6c",
        "accent2": "#ffd6b8",
    },
    "🌿 Forest Frog": {
        "n_photos": 2,
        "layout": "horizontal_2",
        "desc": "2 foto · Hijau daun",
        "bg": "#f0faf0",
        "accent": "#5aad4e",
        "accent2": "#b8e6b0",
    },
    "🎀 Ribbon Cat": {
        "n_photos": 4,
        "layout": "grid_2x2",
        "desc": "4 foto · Grid kucing",
        "bg": "#fef3ff",
        "accent": "#d47bdd",
        "accent2": "#f0c4f8",
    },
    "🐣 Chicky Strip": {
        "n_photos": 6,
        "layout": "strip_6",
        "desc": "6 foto · Strip ayam",
        "bg": "#fffde7",
        "accent": "#ffb300",
        "accent2": "#ffe082",
    },
}


def _draw_frame_decorations(draw, img, frame_key, W, H):
    """Gambar dekorasi & karakter di luar slot foto"""
    f = FRAMES[frame_key]
    acc = f["accent"]
    acc2 = f["accent2"]

    if "Sakura" in frame_key:
        # Confetti & bunga
        rng = random.Random(42)
        for _ in range(18):
            x, y = rng.randint(0, W), rng.randint(0, H)
            r = rng.randint(4, 10)
            col = rng.choice(["#ff8fab","#ffc2d1","#ffe0eb","#ffb3c6"])
            _circle(draw, x, y, r, col)
        # Bunga sudut
        for cx, cy in [(35, 35), (W-35, 35), (35, H-35), (W-35, H-35)]:
            for a in range(0, 360, 60):
                rad = math.radians(a)
                _circle(draw, cx+int(14*math.cos(rad)), cy+int(14*math.sin(rad)), 8, "#ffc2d1")
            _circle(draw, cx, cy, 6, "#ff8fab")
        # Bintang kecil
        for cx, cy in [(W//2, 22), (60, H//2), (W-60, H//2)]:
            _star(draw, cx, cy, 8, "#ffb3c6")
        # Karakter kelinci di pojok kanan atas & kiri bawah
        _draw_bunny(draw, W-50, 80, 28, "#FFB7C5")
        _draw_bunny(draw, 50, H-80, 22, "#ffcdd2")

    elif "Starry" in frame_key:
        # Background bintang
        rng = random.Random(7)
        for _ in range(25):
            x, y = rng.randint(0, W), rng.randint(0, H)
            _star(draw, x, y, rng.randint(4, 9), rng.choice(["#7b9cff","#c5d5ff","#fff","#a5b8ff"]))
        # Planet kecil
        _circle(draw, 40, 50, 18, "#7b9cff")
        _circle(draw, 40, 50, 12, "#5a7fff")
        draw.ellipse([(22, 62),(58, 70)], outline="#c5d5ff", width=2)
        # Bulan
        _circle(draw, W-45, 45, 18, "#ffe082")
        _circle(draw, W-38, 38, 15, "#f0f4ff")  # crescent
        # Karakter beruang astronot
        _draw_bear(draw, W-55, H-85, 28, "#a0b4e8")
        _draw_bear(draw, 55, 90, 22, "#7b9cff")
        # Sparkle
        for cx, cy in [(W//3, 30), (W*2//3, H-30), (25, H*2//3)]:
            _sparkle(draw, cx, cy, 10, "#c5d5ff")

    elif "Candy" in frame_key:
        # Permen & confetti warna warni
        rng = random.Random(13)
        colors = ["#ff6b9d","#ffa07a","#98d8c8","#ffda77","#b39ddb","#80cbc4"]
        for _ in range(20):
            x, y = rng.randint(0, W), rng.randint(0, H)
            r = rng.randint(5, 12)
            draw.ellipse([(x-r, y-r),(x+r, y+r)], fill=rng.choice(colors))
        # Permen lollipop kecil
        draw.line([(30, H-20),(30, H-55)], fill="#ff6b9d", width=3)
        _circle(draw, 30, H-60, 15, "#ff6b9d")
        _circle(draw, 30, H-60, 10, "#fff")
        _circle(draw, 30, H-60, 6, "#ff6b9d")
        draw.line([(W-30, 20),(W-30, 55)], fill="#98d8c8", width=3)
        _circle(draw, W-30, 60, 15, "#98d8c8")
        _circle(draw, W-30, 60, 10, "#fff")
        _circle(draw, W-30, 60, 6, "#98d8c8")
        # Hantu
        _draw_ghost(draw, 45, 70, 28, "#e8e0ff")
        _draw_ghost(draw, W-45, H-70, 22, "#ffd6b8")
        # Bintang
        for cx, cy in [(W//2, 22), (W-25, H//2)]:
            _star(draw, cx, cy, 9, "#ffda77")

    elif "Forest" in frame_key:
        # Daun & rumput
        rng = random.Random(21)
        for i in range(12):
            x = rng.randint(10, W-10)
            y = rng.randint(10, H-10)
            size = rng.randint(8, 18)
            angle = rng.randint(0, 360)
            draw.ellipse([(x-size//3, y-size), (x+size//3, y+size//3)], fill=rng.choice(["#7ecb6e","#5aad4e","#a5d97a","#c8e6c9"]))
        # Pohon kecil sudut
        for cx in [30, W-30]:
            draw.polygon([(cx, 20),(cx-18, 65),(cx+18, 65)], fill="#5aad4e")
            draw.polygon([(cx, 35),(cx-22, 72),(cx+22, 72)], fill="#7ecb6e")
            draw.rectangle([(cx-5, 65),(cx+5, 80)], fill="#8d6e63")
        # Karakter kodok
        _draw_frog(draw, W-50, H-80, 26, "#7ecb6e")
        _draw_frog(draw, 50, 90, 20, "#5aad4e")
        # Bunga
        for cx, cy, col in [(W//2, H-25, "#ffb3c6"),(W//2-40, 30, "#ffe082"),(W//2+40, 30, "#ffb3c6")]:
            for a in range(0, 360, 72):
                rad = math.radians(a)
                _circle(draw, cx+int(10*math.cos(rad)), cy+int(10*math.sin(rad)), 6, col)
            _circle(draw, cx, cy, 5, "#fff176")

    elif "Ribbon" in frame_key:
        # Bintang & hati
        rng = random.Random(33)
        for _ in range(15):
            x, y = rng.randint(0, W), rng.randint(0, H)
            _star(draw, x, y, rng.randint(5, 10), rng.choice(["#d47bdd","#f0c4f8","#ce93d8","#f8bbd0"]))
        # Pita di pojok
        for cx, cy in [(35, 35), (W-35, 35), (35, H-35), (W-35, H-35)]:
            draw.polygon([(cx-15, cy-8),(cx, cy),(cx-15, cy+8)], fill="#d47bdd")
            draw.polygon([(cx+15, cy-8),(cx, cy),(cx+15, cy+8)], fill="#d47bdd")
            _circle(draw, cx, cy, 5, "#f0c4f8")
        # Hati kecil
        for cx, cy, s in [(W//2, 22, 2.5),(W//4, H-25, 2),(W*3//4, H-25, 2)]:
            _heart(draw, cx, cy, s, "#f06292")
        # Karakter kucing
        _draw_cat(draw, W-52, 80, 26, "#f9a8d4")
        _draw_cat(draw, 52, H-85, 22, "#d47bdd")

    elif "Chicky" in frame_key:
        # Matahari & awan
        _circle(draw, 40, 40, 22, "#ffe082")
        for a in range(0, 360, 45):
            rad = math.radians(a)
            draw.line([(40+22*math.cos(rad), 40+22*math.sin(rad)),
                      (40+34*math.cos(rad), 40+34*math.sin(rad))],
                     fill="#ffb300", width=3)
        # Awan
        _cloud(draw, W-60, 40, 55, 28, "white")
        _cloud(draw, 70, H-40, 45, 22, "white")
        # Telur & ayam
        _draw_chick(draw, W-50, H-80, 26, "#ffe082")
        _draw_chick(draw, 50, 85, 20, "#ffd54f")
        # Bintang kecil
        for cx, cy in [(W//2-30, 25),(W//2+30, 25),(W-25, H//2),(25, H//2)]:
            _sparkle(draw, cx, cy, 8, "#ffb300")
        # Confetti kuning
        rng = random.Random(55)
        for _ in range(10):
            x, y = rng.randint(0, W), rng.randint(0, H)
            draw.ellipse([(x-4, y-4),(x+4, y+4)], fill=rng.choice(["#ffe082","#ffcc02","#fff9c4","#ffb300"]))


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD STRIP
# ═══════════════════════════════════════════════════════════════════════════════

def build_strip(photos: list, frame_key: str, filter_name: str = "Natural") -> Image.Image:
    """Build strip sesuai layout frame."""
    frame = FRAMES[frame_key]
    layout = frame["layout"]
    bg_color = frame["bg"]
    accent = frame["accent"]

    # Apply filter ke semua foto
    processed = [apply_filter(p, filter_name) if p else None for p in photos]

    if layout == "vertical_2":
        return _build_vertical_2(processed, frame_key, bg_color, accent)
    elif layout == "vertical_4":
        return _build_vertical_4(processed, frame_key, bg_color, accent)
    elif layout == "grid_2x3":
        return _build_grid_2x3(processed, frame_key, bg_color, accent)
    elif layout == "horizontal_2":
        return _build_horizontal_2(processed, frame_key, bg_color, accent)
    elif layout == "grid_2x2":
        return _build_grid_2x2(processed, frame_key, bg_color, accent)
    elif layout == "strip_6":
        return _build_strip_6(processed, frame_key, bg_color, accent)
    return Image.new("RGB", (400, 600), bg_color)


def _slot(img, w, h):
    """Resize foto ke slot, return putih kalau None."""
    if img is None:
        slot = Image.new("RGB", (w, h), "#f5f5f5")
        d = ImageDraw.Draw(slot)
        _circle(d, w//2, h//2, min(w,h)//5, "#e0e0e0")
        d.text((w//2-8, h//2-6), "📷", fill="#bdbdbd", font=_font(14))
        return slot
    return img.resize((w, h), Image.LANCZOS)


def _finalize(canvas, draw, frame_key, W, H):
    """Tambah dekorasi frame & watermark."""
    _draw_frame_decorations(draw, canvas, frame_key, W, H)
    f = FRAMES[frame_key]
    font = _font_r(11)
    ts_text = "✦ Gamma Photobooth ✦"
    bb = draw.textbbox((0,0), ts_text, font=font)
    tw = bb[2]-bb[0]
    draw.text(((W-tw)//2, H-18), ts_text, fill=f["accent"], font=font)
    return canvas


def _build_vertical_2(photos, fk, bg, accent):
    W, H = 420, 780
    PAD, GAP = 40, 16
    SW = W - 2*PAD
    SH = (H - 2*PAD - GAP - 50) // 2
    canvas = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(canvas)
    # Border luar
    draw.rounded_rectangle([(4,4),(W-5,H-5)], radius=20, outline=accent, width=3)
    # Header
    font = _font(18)
    bb = draw.textbbox((0,0), fk, font=font)
    draw.text(((W-(bb[2]-bb[0]))//2, 14), fk, fill=accent, font=font)
    # Slots
    for i, photo in enumerate(photos[:2]):
        y = PAD + 30 + i*(SH+GAP)
        slot_img = _slot(photo, SW, SH)
        canvas.paste(slot_img, (PAD, y))
        draw.rounded_rectangle([(PAD-2, y-2),(PAD+SW+2, y+SH+2)], radius=6, outline=accent, width=2)
    return _finalize(canvas, draw, fk, W, H)


def _build_vertical_4(photos, fk, bg, accent):
    W, H = 380, 900
    PAD, GAP = 32, 10
    SW = W - 2*PAD
    SH = (H - 2*PAD - 3*GAP - 55) // 4
    canvas = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(4,4),(W-5,H-5)], radius=20, outline=accent, width=3)
    font = _font(16)
    bb = draw.textbbox((0,0), fk, font=font)
    draw.text(((W-(bb[2]-bb[0]))//2, 14), fk, fill=accent, font=font)
    for i, photo in enumerate(photos[:4]):
        y = PAD + 32 + i*(SH+GAP)
        slot_img = _slot(photo, SW, SH)
        canvas.paste(slot_img, (PAD, y))
        draw.rounded_rectangle([(PAD-2, y-2),(PAD+SW+2, y+SH+2)], radius=5, outline=accent, width=2)
    return _finalize(canvas, draw, fk, W, H)


def _build_grid_2x3(photos, fk, bg, accent):
    W, H = 560, 680
    PAD, GAPX, GAPY = 35, 12, 12
    cols, rows = 2, 3
    SW = (W - 2*PAD - (cols-1)*GAPX) // cols
    SH = (H - 2*PAD - (rows-1)*GAPY - 55) // rows
    canvas = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(4,4),(W-5,H-5)], radius=20, outline=accent, width=3)
    font = _font(17)
    bb = draw.textbbox((0,0), fk, font=font)
    draw.text(((W-(bb[2]-bb[0]))//2, 14), fk, fill=accent, font=font)
    for i, photo in enumerate(photos[:6]):
        col = i % cols
        row = i // cols
        x = PAD + col*(SW+GAPX)
        y = PAD + 32 + row*(SH+GAPY)
        slot_img = _slot(photo, SW, SH)
        canvas.paste(slot_img, (x, y))
        draw.rounded_rectangle([(x-2, y-2),(x+SW+2, y+SH+2)], radius=5, outline=accent, width=2)
    return _finalize(canvas, draw, fk, W, H)


def _build_horizontal_2(photos, fk, bg, accent):
    W, H = 760, 420
    PAD, GAP = 35, 14
    SH = H - 2*PAD - 50
    SW = (W - 2*PAD - GAP) // 2
    canvas = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(4,4),(W-5,H-5)], radius=20, outline=accent, width=3)
    font = _font(18)
    bb = draw.textbbox((0,0), fk, font=font)
    draw.text(((W-(bb[2]-bb[0]))//2, 14), fk, fill=accent, font=font)
    for i, photo in enumerate(photos[:2]):
        x = PAD + i*(SW+GAP)
        y = PAD + 32
        slot_img = _slot(photo, SW, SH)
        canvas.paste(slot_img, (x, y))
        draw.rounded_rectangle([(x-2, y-2),(x+SW+2, y+SH+2)], radius=5, outline=accent, width=2)
    return _finalize(canvas, draw, fk, W, H)


def _build_grid_2x2(photos, fk, bg, accent):
    W, H = 560, 580
    PAD, GAP = 35, 12
    SW = (W - 2*PAD - GAP) // 2
    SH = (H - 2*PAD - GAP - 55) // 2
    canvas = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(4,4),(W-5,H-5)], radius=20, outline=accent, width=3)
    font = _font(17)
    bb = draw.textbbox((0,0), fk, font=font)
    draw.text(((W-(bb[2]-bb[0]))//2, 14), fk, fill=accent, font=font)
    for i, photo in enumerate(photos[:4]):
        col = i % 2
        row = i // 2
        x = PAD + col*(SW+GAP)
        y = PAD + 32 + row*(SH+GAP)
        slot_img = _slot(photo, SW, SH)
        canvas.paste(slot_img, (x, y))
        draw.rounded_rectangle([(x-2, y-2),(x+SW+2, y+SH+2)], radius=5, outline=accent, width=2)
    return _finalize(canvas, draw, fk, W, H)


def _build_strip_6(photos, fk, bg, accent):
    """3 kolom strip vertikal masing-masing 2 foto"""
    W, H = 680, 620
    PAD, GAPX, GAPY = 30, 10, 10
    cols, rows = 3, 2
    SW = (W - 2*PAD - (cols-1)*GAPX) // cols
    SH = (H - 2*PAD - GAPY - 55) // rows
    canvas = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle([(4,4),(W-5,H-5)], radius=20, outline=accent, width=3)
    font = _font(17)
    bb = draw.textbbox((0,0), fk, font=font)
    draw.text(((W-(bb[2]-bb[0]))//2, 14), fk, fill=accent, font=font)
    for i, photo in enumerate(photos[:6]):
        col = i % cols
        row = i // cols
        x = PAD + col*(SW+GAPX)
        y = PAD + 32 + row*(SH+GAPY)
        slot_img = _slot(photo, SW, SH)
        canvas.paste(slot_img, (x, y))
        draw.rounded_rectangle([(x-2, y-2),(x+SW+2, y+SH+2)], radius=5, outline=accent, width=2)
    return _finalize(canvas, draw, fk, W, H)


def pil_to_bytes(img: Image.Image, fmt="PNG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()

from PIL import ImageOps
def mirror_image(img: Image.Image) -> Image.Image:
    return ImageOps.mirror(img)