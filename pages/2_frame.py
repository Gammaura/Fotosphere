"""pages/2_frame.py — Pilih frame & mirror"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from utils import FRAMES
from db import update_session
from style import GLOBAL_CSS, step_indicator

st.set_page_config(page_title="PhotoBooth · Frame", page_icon="🎨", layout="centered", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.frame-card {
    background: white;
    border: 2.5px solid #ebd5f0;
    border-radius: 16px;
    padding: 1rem 0.8rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 6px;
}
.frame-card.sel {
    border-color: #f06292 !important;
    background: #fff0f6 !important;
    box-shadow: 0 4px 15px rgba(240,98,146,0.2) !important;
}
.f-emoji { font-size: 1.8rem; display: block; margin-bottom: 5px; }
.f-name { font-size: 0.85rem; font-weight: 800; color: #3d2c3e; }
.f-desc { font-size: 0.65rem; color: #a68ab0; margin-top: 2px; }

.mode-card {
    background: white;
    border: 2.5px solid #ebd5f0;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 8px;
}
.mode-card.sel-mode {
    border-color: #9c7bb5 !important;
    background: #f3eaff !important;
}
.mode-icon { font-size: 1.5rem; display: block; margin-bottom: 4px; }
.mode-name { font-size: 0.85rem; font-weight: 800; color: #7b5ea7; }
.mode-desc { font-size: 0.65rem; color: #a68ab0; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("session_id"):
    st.warning("Sesi tidak valid.")
    if st.button("← Home"):
        st.switch_page("app.py")
    st.stop()

if "frame_choice" not in st.session_state:
    st.session_state.frame_choice = list(FRAMES.keys())[0]
if "mirror" not in st.session_state:
    st.session_state.mirror = False

frame_keys = list(FRAMES.keys())

st.markdown(step_indicator(2), unsafe_allow_html=True)
st.markdown("""
<div class="page-title">
    <span class="emoji">🎨</span>
    <h1>Pilih Frame</h1>
    <p>Pilih tema frame dan mode kamera kamu</p>
</div>
""", unsafe_allow_html=True)

# ── Frame grid ─────────────────────────────────────────────────────────────────
st.markdown('<span class="sec-label">🌸 Tema Frame</span>', unsafe_allow_html=True)

rows = [frame_keys[:3], frame_keys[3:]]
for row in rows:
    cols = st.columns(3, gap="small")
    for i, key in enumerate(row):
        frame = FRAMES[key]
        with cols[i]:
            is_sel = st.session_state.frame_choice == key
            st.markdown(f"""
            <div class="frame-card {'sel' if is_sel else ''}">
                <span class="f-emoji">{key.split()[0]}</span>
                <div class="f-name">{" ".join(key.split()[1:])}</div>
                <div class="f-desc">{frame['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if is_sel:
                st.markdown('<div class="btn-selected">', unsafe_allow_html=True)
            if st.button("✓ Dipilih" if is_sel else "Pilih", key=f"fb_{key}", use_container_width=True):
                st.session_state.frame_choice = key
                st.rerun()
            if is_sel:
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Preview strip ──────────────────────────────────────────────────────────────
st.markdown('<span class="sec-label">👁 Preview Strip</span>', unsafe_allow_html=True)

frame = FRAMES[st.session_state.frame_choice]
bg = frame["bg"]
border_c = frame["border"]
text_c = frame["text_color"]
corners = frame.get("emoji_corners", ["○","○","○","○"])

STRIP_W, SLOT_H, GAP = 320, 75, 8
TOP_PAD, BOT_PAD, SIDE = 48, 55, 18
canvas_h = TOP_PAD + 4 * SLOT_H + 3 * GAP + BOT_PAD

img = Image.new("RGB", (STRIP_W, canvas_h), bg)
draw = ImageDraw.Draw(img)
draw.rectangle([(2,2),(STRIP_W-3,canvas_h-3)], outline=border_c, width=3)

try:
    font_h = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    font_s = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except:
    font_h = ImageFont.load_default()
    font_s = font_h

title = "✦ PHOTOBOOTH ✦"
bb = draw.textbbox((0,0), title, font=font_h)
draw.text(((STRIP_W-(bb[2]-bb[0]))//2, 14), title, fill=text_c, font=font_h)

for i in range(4):
    y = TOP_PAD + i*(SLOT_H+GAP)
    draw.rectangle([(SIDE,y),(STRIP_W-SIDE,y+SLOT_H)], outline=border_c, width=2)
    label = f"Foto {i+1}"
    bb2 = draw.textbbox((0,0), label, font=font_s)
    draw.text(((STRIP_W-(bb2[2]-bb2[0]))//2, y+SLOT_H//2-7), label, fill=text_c, font=font_s)

draw.line([(SIDE, canvas_h-42),(STRIP_W-SIDE, canvas_h-42)], fill=border_c, width=1)
corner_str = "  ".join(corners)
bb3 = draw.textbbox((0,0), corner_str, font=font_s)
draw.text(((STRIP_W-(bb3[2]-bb3[0]))//2, canvas_h-32), corner_str, fill=text_c, font=font_s)

buf = io.BytesIO()
img.save(buf, format="PNG")

_, preview_col, _ = st.columns([1, 2, 1])
with preview_col:
    st.image(buf.getvalue(), use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Mirror toggle ──────────────────────────────────────────────────────────────
st.markdown('<span class="sec-label">🪞 Mode Kamera</span>', unsafe_allow_html=True)

mc1, mc2 = st.columns(2, gap="medium")
with mc1:
    is_m = st.session_state.mirror
    st.markdown(f"""
    <div class="mode-card {'sel-mode' if is_m else ''}">
        <span class="mode-icon">🪞</span>
        <div class="mode-name">Mirror</div>
        <div class="mode-desc">Seperti selfie, dicerminkan</div>
    </div>
    """, unsafe_allow_html=True)
    if is_m:
        st.markdown('<div class="btn-lav">', unsafe_allow_html=True)
    if st.button("✓ Mirror" if is_m else "Pilih Mirror", key="m_on", use_container_width=True):
        st.session_state.mirror = True
        st.rerun()
    if is_m:
        st.markdown('</div>', unsafe_allow_html=True)

with mc2:
    is_n = not st.session_state.mirror
    st.markdown(f"""
    <div class="mode-card {'sel-mode' if is_n else ''}">
        <span class="mode-icon">📷</span>
        <div class="mode-name">Normal</div>
        <div class="mode-desc">Sesuai aslinya</div>
    </div>
    """, unsafe_allow_html=True)
    if is_n:
        st.markdown('<div class="btn-lav">', unsafe_allow_html=True)
    if st.button("✓ Normal" if is_n else "Pilih Normal", key="m_off", use_container_width=True):
        st.session_state.mirror = False
        st.rerun()
    if is_n:
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

_, col, _ = st.columns([1, 4, 1])
with col:
    if st.button("📸  Mulai Foto Sekarang!", use_container_width=True):
        update_session(st.session_state.session_id,
                       frame_choice=st.session_state.frame_choice,
                       mirror=st.session_state.mirror)
        st.session_state.photos = [None, None, None, None]
        st.session_state.start_time = None
        st.session_state.active_slot = 0
        st.switch_page("pages/3_shoot.py")