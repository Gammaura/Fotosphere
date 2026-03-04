"""pages/3_shoot.py — Sesi foto"""

import streamlit as st
import time
from PIL import Image
from utils import mirror_image, pil_to_bytes, FRAMES
from db import upload_photo, update_session
from style import GLOBAL_CSS, step_indicator

st.set_page_config(page_title="PhotoBooth · Foto", page_icon="📸", layout="centered", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.timer-box {
    background: linear-gradient(135deg, #fff0f6, #f3eaff);
    border: 2px solid #f8bbd0;
    border-radius: 16px;
    padding: 0.8rem 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}
.timer-num {
    font-size: 2.8rem;
    font-weight: 900;
    color: #e91e8c;
    line-height: 1;
    margin: 0;
}
.timer-num.warn { color: #fb8c00 !important; }
.timer-num.danger { color: #e53935 !important; animation: blink 0.6s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }
.timer-label { font-size: 0.7rem; color: #a68ab0; margin-top: 4px; font-weight: 700; letter-spacing: 2px; }

.progress-wrap { margin-bottom: 1rem; }
.progress-label {
    display: flex; justify-content: space-between;
    font-size: 0.75rem; font-weight: 700; margin-bottom: 6px;
}
.progress-bar { background: #ebd5f0; border-radius: 10px; height: 8px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 10px; background: linear-gradient(90deg, #f06292, #9c7bb5); transition: width 0.4s ease; }

.slot-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 1rem 0; }
.slot-empty {
    background: white;
    border: 2px dashed #ebd5f0;
    border-radius: 12px;
    height: 80px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; color: #c9a8d4; font-weight: 700;
}
.slot-empty.active {
    border-color: #f06292 !important;
    background: #fff0f6 !important;
    color: #f06292 !important;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(240,98,146,0.3)} 50%{box-shadow:0 0 0 6px rgba(240,98,146,0)} }

.cam-wrapper {
    background: white;
    border: 2px solid #ebd5f0;
    border-radius: 20px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.cam-label {
    font-size: 0.8rem; font-weight: 800;
    color: #7b5ea7; margin-bottom: 0.6rem;
    text-align: center;
}

/* Mirror flip CSS */
.mirror-cam div[data-testid="stCameraInput"] video,
.mirror-cam div[data-testid="stCameraInput"] img {
    transform: scaleX(-1) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("session_id"):
    st.warning("Sesi tidak valid.")
    if st.button("← Home"):
        st.switch_page("app.py")
    st.stop()

SESSION_DURATION = 5 * 60

if "start_time" not in st.session_state or st.session_state.start_time is None:
    st.session_state.start_time = time.time()
if "photos" not in st.session_state or not isinstance(st.session_state.photos, list) or len(st.session_state.photos) != 4:
    st.session_state.photos = [None, None, None, None]
if "active_slot" not in st.session_state:
    st.session_state.active_slot = 0

photos = st.session_state.photos
mirror = st.session_state.get("mirror", False)
frame_choice = st.session_state.get("frame_choice", list(FRAMES.keys())[0])
filled = sum(1 for p in photos if p is not None)
active = st.session_state.active_slot

elapsed = time.time() - st.session_state.start_time
remaining = max(0, SESSION_DURATION - elapsed)
mins, secs = int(remaining // 60), int(remaining % 60)
timer_class = "danger" if remaining <= 30 else ("warn" if remaining <= 60 else "")

# ── Timeout ────────────────────────────────────────────────────────────────────
if remaining <= 0:
    st.markdown("""
    <div style="text-align:center; padding:2rem;">
        <div style="font-size:3rem;">⏱️</div>
        <h2 style="color:#e91e8c; font-size:1.5rem;">Waktu Habis!</h2>
    </div>
    """, unsafe_allow_html=True)
    valid = [p for p in photos if p is not None]
    if valid:
        st.info(f"Kamu punya {len(valid)} foto. Mau lanjut ke filter?")
        if st.button("Lanjut ke Filter →"):
            st.session_state.final_photos = valid
            st.switch_page("pages/4_filter.py")
    else:
        if st.button("← Mulai Ulang"):
            for k in ["session_id","start_time","photos","active_slot"]:
                st.session_state.pop(k, None)
            st.switch_page("app.py")
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(step_indicator(3), unsafe_allow_html=True)

# Timer
st.markdown(f"""
<div class="timer-box">
    <p class="timer-num {timer_class}">{mins:02d}:{secs:02d}</p>
    <p class="timer-label">SISA WAKTU</p>
</div>
""", unsafe_allow_html=True)

# Progress
st.markdown(f"""
<div class="progress-wrap">
    <div class="progress-label">
        <span style="color:#7b5ea7;">Progress Foto</span>
        <span style="color:#f06292;">{filled} / 4</span>
    </div>
    <div class="progress-bar">
        <div class="progress-fill" style="width:{filled*25}%"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Slot thumbnails ─────────────────────────────────────────────────────────────
slot_html = '<div class="slot-grid">'
for i in range(4):
    if photos[i] is not None:
        slot_html += f'<div style="border-radius:12px; overflow:hidden; border:2px solid #f8bbd0; height:80px;">foto{i}</div>'
    else:
        is_active = i == active
        label = "← Sini!" if is_active else f"Slot {i+1}"
        slot_html += f'<div class="slot-empty {"active" if is_active else ""}">{label}</div>'
slot_html += '</div>'
st.markdown(slot_html, unsafe_allow_html=True)

# Render actual photos in slots using columns
has_photos = any(p is not None for p in photos)
if has_photos:
    thumb_cols = st.columns(4, gap="small")
    for i in range(4):
        with thumb_cols[i]:
            if photos[i] is not None:
                st.image(photos[i], use_container_width=True)
                st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                if st.button(f"🔄 Retake", key=f"rt_{i}", use_container_width=True):
                    photos[i] = None
                    st.session_state.photos = photos
                    st.session_state.active_slot = i
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Camera ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="cam-wrapper {'mirror-cam' if mirror else ''}">
    <div class="cam-label">📸 Slot {active+1} dari 4 {'· 🪞 Mirror' if mirror else ''}</div>
""", unsafe_allow_html=True)

if mirror:
    st.markdown("""
    <style>
    div[data-testid="stCameraInput"] video,
    div[data-testid="stCameraInput"] img { transform: scaleX(-1) !important; }
    </style>
    """, unsafe_allow_html=True)

camera_img = st.camera_input(
    f"Ambil foto slot {active+1}",
    key=f"cam_{active}_{int(st.session_state.start_time)}",
    label_visibility="collapsed",
)
st.markdown('</div>', unsafe_allow_html=True)

if camera_img is not None:
    raw = Image.open(camera_img).convert("RGB")
    if mirror:
        raw = mirror_image(raw)

    _, prev_col, _ = st.columns([1, 3, 1])
    with prev_col:
        st.image(raw, use_container_width=True, caption=f"Preview Slot {active+1}")

    _, btn_col, _ = st.columns([1, 3, 1])
    with btn_col:
        if st.button(f"✅  Simpan Foto {active+1}", use_container_width=True):
            photos[active] = raw
            st.session_state.photos = photos
            next_empty = next((j for j in range(4) if photos[j] is None), None)
            if next_empty is not None:
                st.session_state.active_slot = next_empty
            st.rerun()

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Next ───────────────────────────────────────────────────────────────────────
_, next_col, _ = st.columns([1, 4, 1])
with next_col:
    if filled == 4:
        st.success("🎉 Semua foto terambil! Siap lanjut ke filter.")
        if st.button("✨  Lanjut ke Filter!", use_container_width=True):
            with st.spinner("Menyimpan foto..."):
                urls = []
                for idx, photo in enumerate(photos):
                    if photo is not None:
                        try:
                            url = upload_photo(st.session_state.session_id, idx, pil_to_bytes(photo))
                            urls.append(url)
                        except:
                            urls.append("")
                update_session(st.session_state.session_id, photo_urls=urls)
                st.session_state.final_photos = [p for p in photos if p is not None]
                st.switch_page("pages/4_filter.py")
    elif filled > 0:
        st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
        if st.button(f"Lanjut dengan {filled} foto →", use_container_width=True):
            with st.spinner("Menyimpan foto..."):
                urls = []
                for idx, photo in enumerate(photos):
                    if photo is not None:
                        try:
                            url = upload_photo(st.session_state.session_id, idx, pil_to_bytes(photo))
                            urls.append(url)
                        except:
                            urls.append("")
                update_session(st.session_state.session_id, photo_urls=urls)
                st.session_state.final_photos = [p for p in photos if p is not None]
                st.switch_page("pages/4_filter.py")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="text-align:center; color:#a68ab0; font-size:0.8rem;">Ambil minimal 1 foto untuk lanjut ⬆️</p>', unsafe_allow_html=True)

# Auto-refresh timer
st.markdown("<script>setTimeout(()=>window.location.reload(), 5000)</script>", unsafe_allow_html=True)