"""pages/3_shoot.py — Sesi foto landscape 3-panel"""

import streamlit as st
import time
from PIL import Image
from utils import mirror_image, pil_to_bytes, FRAMES, build_strip, apply_filter
from db import upload_photo, update_session
from style import GLOBAL_CSS, step_bar

st.set_page_config(page_title="Gamma PhotoBooth · Foto", page_icon="📸",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.block-container { padding: 1rem 1.5rem !important; max-width: 100% !important; }

/* Timer besar */
.big-timer {
    font-size: 5rem;
    font-weight: 900;
    color: #ff4d8d !important;
    line-height: 1;
    text-align: center;
    text-shadow: 0 4px 20px rgba(255,77,141,0.3);
}
.big-timer.warn { color: #fb8c00 !important; text-shadow: 0 4px 20px rgba(251,140,0,0.3); }
.big-timer.danger { color: #e53935 !important; animation: bigpulse 0.5s infinite; }
@keyframes bigpulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }

/* Countdown overlay */
.countdown-num {
    font-size: 8rem;
    font-weight: 900;
    color: #ff4d8d !important;
    text-align: center;
    line-height: 1;
    animation: countpop 0.5s ease-out;
    text-shadow: 0 0 40px rgba(255,77,141,0.5);
}
@keyframes countpop {
    0% { transform: scale(1.5); opacity: 0.5; }
    100% { transform: scale(1); opacity: 1; }
}

/* Slot indicator */
.slot-row { display:flex; gap:8px; justify-content:center; margin:0.5rem 0; }
.slot-dot {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 800;
    border: 2px solid #e8e8f0;
    color: #9a9aaa !important;
    background: white;
}
.slot-dot.done { background: #ff4d8d; color: white !important; border-color: #ff4d8d; }
.slot-dot.active { background: white; border-color: #ff4d8d; color: #ff4d8d !important;
    box-shadow: 0 0 0 3px #ffb3ce; animation: pulsedot 1.2s ease-in-out infinite; }
@keyframes pulsedot { 0%,100%{box-shadow:0 0 0 3px #ffb3ce} 50%{box-shadow:0 0 0 6px #ffe0eb} }

/* Camera panel */
.cam-panel {
    background: white;
    border-radius: 24px;
    padding: 1rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border: 1.5px solid #f0f0f0;
    position: relative;
}
.cam-header {
    font-size: 0.8rem;
    font-weight: 800;
    color: #9a9aaa;
    letter-spacing: 2px;
    text-align: center;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

/* Preview panel */
.preview-panel {
    background: white;
    border-radius: 24px;
    padding: 1rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border: 1.5px solid #f0f0f0;
}
.preview-header {
    font-size: 0.75rem;
    font-weight: 800;
    color: #9a9aaa;
    letter-spacing: 2px;
    text-align: center;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
}

/* Mirror flip */
div[data-testid="stCameraInput"] video,
div[data-testid="stCameraInput"] img { transition: transform 0.2s; }
.mirror-active div[data-testid="stCameraInput"] video,
.mirror-active div[data-testid="stCameraInput"] img { transform: scaleX(-1) !important; }

/* Action buttons */
.btn-retake > button {
    background: white !important;
    color: #ff4d8d !important;
    border: 2px solid #ffb3ce !important;
    font-size: 0.85rem !important;
    font-weight: 800 !important;
    box-shadow: none !important;
    padding: 0.6rem !important;
}
.btn-retake > button:hover { background: #fff0f5 !important; transform: none !important; box-shadow: none !important; }

.btn-next > button {
    background: linear-gradient(135deg, #ff4d8d, #e0005a) !important;
    font-size: 0.9rem !important;
    font-weight: 900 !important;
    padding: 0.7rem !important;
    box-shadow: 0 4px 15px rgba(255,77,141,0.4) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("session_id"):
    st.warning("Sesi tidak valid.")
    if st.button("← Home"):
        st.switch_page("app.py")
    st.stop()

frame_choice = st.session_state.get("frame_choice", list(FRAMES.keys())[0])
frame = FRAMES[frame_choice]
N = frame["n_photos"]
mirror = st.session_state.get("mirror", False)

# Init state
if "photos" not in st.session_state or not isinstance(st.session_state.photos, list) or len(st.session_state.photos) != N:
    st.session_state.photos = [None] * N
if "active_slot" not in st.session_state or st.session_state.active_slot is None:
    st.session_state.active_slot = 0
if "countdown_active" not in st.session_state or st.session_state.countdown_active is None:
    st.session_state.countdown_active = False
if "countdown_start" not in st.session_state:
    st.session_state.countdown_start = None
if "phase" not in st.session_state:
    st.session_state.phase = "shooting"  # shooting | review

photos = st.session_state.photos
active = st.session_state.active_slot
filled = sum(1 for p in photos if p is not None)
phase = st.session_state.phase

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(step_bar(3), unsafe_allow_html=True)

h_back, h_title, h_info = st.columns([1, 4, 1])
with h_back:
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("← BACK"):
        st.switch_page("pages/2_frame.py")
    st.markdown('</div>', unsafe_allow_html=True)
with h_title:
    st.markdown(f'<h2 style="text-align:center; font-size:1.3rem; font-weight:900; letter-spacing:3px; margin:0; color:#2a2a3a;">{frame_choice} · {"🪞 Mirror" if mirror else "📷 Normal"}</h2>', unsafe_allow_html=True)
with h_info:
    st.markdown(f'<p style="text-align:right; font-size:0.8rem; font-weight:800; color:#ff4d8d; margin:0;">{filled}/{N} Foto</p>', unsafe_allow_html=True)

# Slot indicator
dots_html = '<div class="slot-row">'
for i in range(N):
    if photos[i] is not None:
        cls = "done"
        lbl = "✓"
    elif i == active and phase == "shooting":
        cls = "active"
        lbl = str(i+1)
    else:
        cls = ""
        lbl = str(i+1)
    dots_html += f'<div class="slot-dot {cls}">{lbl}</div>'
dots_html += '</div>'
st.markdown(dots_html, unsafe_allow_html=True)

st.markdown("<hr class='divider' style='margin:0.5rem 0;'>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE: REVIEW (semua foto sudah diambil)
# ═══════════════════════════════════════════════════════════════════════════════
if phase == "review":
    st.markdown('<h3 style="text-align:center; font-size:1.1rem; font-weight:900; color:#2a2a3a; margin:0.5rem 0;">Review Foto Kamu</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:0.8rem; color:#9a9aaa; margin-bottom:1rem;">Mau retake foto mana? Atau langsung next ke filter.</p>', unsafe_allow_html=True)

    # Tampilkan semua foto
    photo_cols = st.columns(N, gap="small")
    for i in range(N):
        with photo_cols[i]:
            if photos[i] is not None:
                st.image(photos[i], use_container_width=True, caption=f"Foto {i+1}")
                st.markdown('<div class="btn-retake">', unsafe_allow_html=True)
                if st.button(f"🔄 Retake {i+1}", key=f"rev_rt_{i}", use_container_width=True):
                    photos[i] = None
                    st.session_state.photos = photos
                    st.session_state.active_slot = i
                    st.session_state.phase = "shooting"
                    st.session_state.countdown_active = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    _, next_col, _ = st.columns([1, 2, 1])
    with next_col:
        st.markdown('<div class="btn-next">', unsafe_allow_html=True)
        if st.button("✨  NEXT — Pilih Filter", use_container_width=True):
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

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE: SHOOTING
# ═══════════════════════════════════════════════════════════════════════════════
else:
    col_cam, col_preview = st.columns([3, 2], gap="medium")

    with col_cam:
        st.markdown('<div class="cam-panel">', unsafe_allow_html=True)
        st.markdown(f'<div class="cam-header">📸 Foto {active+1} dari {N}</div>', unsafe_allow_html=True)

        # Mirror CSS
        if mirror:
            st.markdown("""
            <style>
            div[data-testid="stCameraInput"] video,
            div[data-testid="stCameraInput"] img { transform: scaleX(-1) !important; }
            </style>
            """, unsafe_allow_html=True)

        # Camera input
        cam_img = st.camera_input(
            f"Foto {active+1}",
            key=f"cam_{active}_{frame_choice}",
            label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Countdown & action
        if cam_img is not None:
            raw = Image.open(cam_img).convert("RGB")
            if mirror:
                raw = mirror_image(raw)

            if not st.session_state.countdown_active:
                # Tampilkan preview + tombol
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                btn_c1, btn_c2 = st.columns(2, gap="small")
                with btn_c1:
                    st.markdown('<div class="btn-retake">', unsafe_allow_html=True)
                    if st.button("🔄 Retake", key="retake_btn", use_container_width=True):
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with btn_c2:
                    st.markdown('<div class="btn-next">', unsafe_allow_html=True)
                    if st.button("✓ Simpan & Lanjut", key="save_btn", use_container_width=True):
                        photos[active] = raw
                        st.session_state.photos = photos
                        next_empty = next((j for j in range(N) if photos[j] is None), None)
                        if next_empty is not None:
                            st.session_state.active_slot = next_empty
                        else:
                            st.session_state.phase = "review"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Countdown otomatis 5 detik
            if not st.session_state.countdown_active:
                _, cd_col, _ = st.columns([1, 2, 1])
                with cd_col:
                    if st.button("📸  Mulai Countdown 5 Detik", use_container_width=True):
                        st.session_state.countdown_active = True
                        st.session_state.countdown_start = time.time()
                        st.rerun()
            else:
                elapsed_cd = time.time() - (st.session_state.countdown_start or time.time())
                remaining_cd = max(0, 5 - elapsed_cd)
                count_num = math.ceil(remaining_cd) if remaining_cd > 0 else 0

                if count_num > 0:
                    st.markdown(f'<div class="countdown-num">{count_num}</div>', unsafe_allow_html=True)
                    st.markdown('<p style="text-align:center; font-size:0.85rem; color:#9a9aaa; font-weight:700;">Bersiap...</p>', unsafe_allow_html=True)
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.session_state.countdown_active = False
                    st.session_state.countdown_start = None
                    st.markdown('<p style="text-align:center; font-size:1rem; color:#ff4d8d; font-weight:800;">📸 Foto sekarang!</p>', unsafe_allow_html=True)
                    st.rerun()

    with col_preview:
        st.markdown('<div class="preview-panel">', unsafe_allow_html=True)
        st.markdown('<div class="preview-header">✦ Preview Strip</div>', unsafe_allow_html=True)

        # Build strip dengan foto yang sudah ada
        strip_preview = build_strip(photos, frame_choice, "Natural")
        st.image(strip_preview, use_container_width=True)

        # Info
        st.markdown(f"""
        <div style="background:#fafafa; border-radius:12px; padding:0.8rem; margin-top:0.8rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                <span style="font-size:0.7rem; color:#9a9aaa; font-weight:700;">FRAME</span>
                <span style="font-size:0.75rem; font-weight:800; color:#2a2a3a;">{frame_choice}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                <span style="font-size:0.7rem; color:#9a9aaa; font-weight:700;">MODE</span>
                <span style="font-size:0.75rem; font-weight:800; color:#ff4d8d;">{"🪞 Mirror" if mirror else "📷 Normal"}</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:0.7rem; color:#9a9aaa; font-weight:700;">PROGRESS</span>
                <span style="font-size:0.75rem; font-weight:800; color:#ff4d8d;">{filled}/{N}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

import math