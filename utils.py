"""
utils.py — Filter, Frame, Strip builder untuk PhotoBooth
"""

from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw, ImageFont
import numpy as np
import io
from datetime import datetime
import os

# ── Filters ───────────────────────────────────────────────────────────────────

FILTERS = ["Original", "Grayscale", "Vintage", "Film Noir", "Warm Glow", "Cool Tone", "Faded", "Vivid"]

def apply_filter(img: Image.Image, filter_name: str) -> Image.Image:
    img = img.convert("RGB")
    if filter_name == "Grayscale":
        img = ImageOps.grayscale(img).convert("RGB")
    elif filter_name == "Vintage":
        img = ImageOps.grayscale(img).convert("RGB")
        r, g, b = img.split()
        r = r.point(lambda i: min(255, int(i * 1.15)))
        b = b.point(lambda i: int(i * 0.85))
        img = Image.merge("RGB", (r, g, b))
        img = ImageEnhance.Contrast(img).enhance(0.85)
        img = ImageEnhance.Color(img).enhance(0.6)
    elif filter_name == "Film Noir":
        img = ImageOps.grayscale(img).convert("RGB")
        img = ImageEnhance.Contrast(img).enhance(1.8)
        img = ImageEnhance.Brightness(img).enhance(0.75)
    elif filter_name == "Warm Glow":
        r, g, b = img.split()
        r = r.point(lambda i: min(255, int(i * 1.2)))
        g = g.point(lambda i: min(255, int(i * 1.05)))
        b = b.point(lambda i: int(i * 0.8))
        img = Image.merge("RGB", (r, g, b))
        img = ImageEnhance.Saturation(img).enhance(1.3)
    elif filter_name == "Cool Tone":
        r, g, b = img.split()
        r = r.point(lambda i: int(i * 0.85))
        b = b.point(lambda i: min(255, int(i * 1.2)))
        img = Image.merge("RGB", (r, g, b))
    elif filter_name == "Faded":
        img = ImageEnhance.Contrast(img).enhance(0.65)
        img = ImageEnhance.Color(img).enhance(0.5)
        img = ImageEnhance.Brightness(img).enhance(1.15)
    elif filter_name == "Vivid":
        img = ImageEnhance.Color(img).enhance(2.0)
        img = ImageEnhance.Contrast(img).enhance(1.3)
    return img


# ── Frames ────────────────────────────────────────────────────────────────────

FRAMES = {
    "🌸 Blossom": {
        "desc": "Pink pastel dengan bunga di sudut",
        "bg": (255, 240, 245),
        "border": (255, 182, 193),
        "text_color": (220, 100, 130),
        "style": "floral",
        "emoji_corners": ["🌸", "🌷", "🌺", "💐"],
    },
    "🌙 Midnight": {
        "desc": "Dark navy elegan",
        "bg": (10, 10, 40),
        "border": (100, 100, 255),
        "text_color": (180, 180, 255),
        "style": "dark",
        "emoji_corners": ["⭐", "🌙", "✨", "💫"],
    },
    "🍋 Citrus": {
        "desc": "Kuning cerah dan segar",
        "bg": (255, 253, 220),
        "border": (255, 200, 0),
        "text_color": (180, 130, 0),
        "style": "bright",
        "emoji_corners": ["🍋", "🌻", "🍊", "🌼"],
    },
    "🤍 Minimal": {
        "desc": "Putih bersih, garis tipis",
        "bg": (250, 250, 250),
        "border": (200, 200, 200),
        "text_color": (100, 100, 100),
        "style": "minimal",
        "emoji_corners": ["○", "○", "○", "○"],
    },
    "🎀 Y2K": {
        "desc": "Retro 2000s, warna-warni",
        "bg": (230, 210, 255),
        "border": (180, 80, 255),
        "text_color": (120, 0, 200),
        "style": "y2k",
        "emoji_corners": ["💜", "⚡", "🦋", "💎"],
    },
    "🌿 Nature": {
        "desc": "Hijau earthy, tenang",
        "bg": (240, 248, 240),
        "border": (100, 160, 100),
        "text_color": (60, 110, 60),
        "style": "nature",
        "emoji_corners": ["🍃", "🌿", "🌱", "🍀"],
    },
}


# ── Strip builder ─────────────────────────────────────────────────────────────

STRIP_W = 520
PHOTO_W = 440
PHOTO_H = 330
GAP = 12
TOP_PAD = 50
BOTTOM_PAD = 70
SIDE_PAD = (STRIP_W - PHOTO_W) // 2


def _load_font(size: int):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def build_strip(photos: list[Image.Image], frame_key: str, selected_filter: str) -> Image.Image:
    """Build 4-photo vertical strip dengan frame pilihan."""
    n = min(len(photos), 4)
    frame = FRAMES[frame_key]

    canvas_h = TOP_PAD + n * PHOTO_H + (n - 1) * GAP + BOTTOM_PAD
    canvas = Image.new("RGB", (STRIP_W, canvas_h), frame["bg"])
    draw = ImageDraw.Draw(canvas)

    # ── Border luar ──
    border_thickness = 6
    draw.rectangle(
        [(border_thickness // 2, border_thickness // 2),
         (STRIP_W - border_thickness // 2, canvas_h - border_thickness // 2)],
        outline=frame["border"], width=border_thickness
    )

    # ── Header label ──
    font_title = _load_font(20)
    title = "✦ PHOTOBOOTH ✦"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((STRIP_W - tw) // 2, 14), title, fill=frame["text_color"], font=font_title)

    # ── Photos ──
    for i, photo in enumerate(photos[:4]):
        filtered = apply_filter(photo, selected_filter)
        ph = filtered.resize((PHOTO_W, PHOTO_H), Image.LANCZOS)
        y = TOP_PAD + i * (PHOTO_H + GAP)
        canvas.paste(ph, (SIDE_PAD, y))

        # Inner border per foto
        draw.rectangle(
            [(SIDE_PAD, y), (SIDE_PAD + PHOTO_W - 1, y + PHOTO_H - 1)],
            outline=frame["border"], width=2
        )

    # ── Footer ──
    font_small = _load_font(13)
    ts = datetime.now().strftime("%d %b %Y  %H:%M")
    bbox2 = draw.textbbox((0, 0), ts, font=font_small)
    tw2 = bbox2[2] - bbox2[0]
    footer_y = TOP_PAD + n * PHOTO_H + (n - 1) * GAP + 16
    draw.text(((STRIP_W - tw2) // 2, footer_y), ts, fill=frame["text_color"], font=font_small)

    # Corner emojis (teks sederhana sebagai pengganti emoji render)
    corners = frame.get("emoji_corners", [])
    font_corner = _load_font(15)
    margin = 16
    positions = [
        (margin, margin),
        (STRIP_W - margin - 20, margin),
        (margin, canvas_h - margin - 20),
        (STRIP_W - margin - 20, canvas_h - margin - 20),
    ]
    for pos, char in zip(positions, corners):
        draw.text(pos, char, fill=frame["border"], font=font_corner)

    return canvas


def pil_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def mirror_image(img: Image.Image) -> Image.Image:
    return ImageOps.mirror(img)
