"""pages/2_frame.py — Pilih frame"""

import streamlit as st
import io
from utils import FRAMES, build_strip, pil_to_bytes
from db import update_session
from style import GLOBAL_CSS, step_bar

st.set_page_config(page_title="Gamma PhotoBooth · Frame", page_icon="🎨",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1300px !important; }

.frame-card {
    background: white;
    border: 2.5px solid #e8e8f0;
    border-radius: 20px;
    padding: 1rem;
    text-align: center;
    transition: all 0.2s ease;
    cursor: pointer;
    height: 100%;
}
.frame-card.sel {
    border-color: #ff4d8d !important;
    box-shadow: 0 6px 25px rgba(255,77,141,0.25) !important;
    background: #fff5f8 !important;
}
.frame-name {
    font-size: 0.95rem;
    font-weight: 900;
    color: #2a2a3a;
    margin: 0.6rem 0 0.2rem;
}
.frame-desc {
    font-size: 0.7rem;
    color: #9a9aaa;
    font-weight: 600;
}
.frame-badge {
    display: inline-block;
    background: #fff0f5;
    color: #ff4d8d;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.65rem;
    font-weight: 800;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("session_id"):
    st.warning("Sesi tidak valid.")
    if st.button("← Home"):
        st.switch_page("app.py")
    st.stop()

if "frame_choice" not in st.session_state or st.session_state.frame_choice is None:
    st.session_state.frame_choice = list(FRAMES.keys())[0]
if "mirror" not in st.session_state or st.session_state.mirror is None:
    st.session_state.mirror = False

frame_keys = list(FRAMES.keys())

# Header
st.markdown(step_bar(2), unsafe_allow_html=True)

col_back, col_title, col_next = st.columns([1, 4, 1])
with col_back:
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("← BACK", use_container_width=True):
        st.switch_page("pages/1_payment.py")
    st.markdown('</div>', unsafe_allow_html=True)
with col_title:
    st.markdown('<h2 style="text-align:center; font-size:1.5rem; font-weight:900; letter-spacing:3px; margin:0; color:#2a2a3a;">PILIH FRAME</h2>', unsafe_allow_html=True)
with col_next:
    if st.button("NEXT →", use_container_width=True):
        update_session(st.session_state.session_id,
                       frame_choice=st.session_state.frame_choice,
                       mirror=st.session_state.mirror)
        n = FRAMES[st.session_state.frame_choice]["n_photos"]
        st.session_state.photos = [None] * n
        st.session_state.n_photos = n
        st.session_state.start_time = None
        st.session_state.active_slot = 0
        st.session_state.current_shot = 0
        st.session_state.shot_photos = [None] * n
        st.switch_page("pages/3_shoot.py")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# Frame grid - 3 kolom x 2 baris
cols = st.columns(3, gap="medium")
for i, key in enumerate(frame_keys):
    frame = FRAMES[key]
    with cols[i % 3]:
        is_sel = st.session_state.frame_choice == key

        # Build preview strip kosong
        preview = build_strip([], key, "Natural")
        # Scale down untuk thumbnail
        thumb_w = 200
        ratio = thumb_w / preview.width
        thumb_h = int(preview.height * ratio)
        thumb = preview.resize((thumb_w, thumb_h))

        st.markdown(f'<div class="frame-card {"sel" if is_sel else ""}">', unsafe_allow_html=True)
        st.image(thumb, use_container_width=True)
        st.markdown(f"""
        <div class="frame-name">{key}</div>
        <div class="frame-desc">{frame['desc']}</div>
        <div class="frame-badge">{frame['n_photos']} Foto</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if is_sel:
            st.markdown('<div class="btn-sel">', unsafe_allow_html=True)
        if st.button("✓ Dipilih" if is_sel else "Pilih Frame", key=f"f_{i}", use_container_width=True):
            st.session_state.frame_choice = key
            st.rerun()
        if is_sel:
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# Mirror toggle di bawah
st.markdown('<p style="text-align:center; font-size:0.85rem; font-weight:800; color:#9a9aaa; letter-spacing:2px; margin-bottom:0.8rem;">MODE KAMERA</p>', unsafe_allow_html=True)
_, mc1, mc2, _ = st.columns([2, 1, 1, 2], gap="small")
is_m = st.session_state.mirror

with mc1:
    st.markdown(f"""
    <div style="background:{"#fff0f5" if is_m else "white"}; border:2px solid {"#ff4d8d" if is_m else "#e8e8f0"};
        border-radius:14px; padding:0.8rem; text-align:center; margin-bottom:6px;">
        <div style="font-size:1.3rem;">🪞</div>
        <div style="font-size:0.8rem; font-weight:800; color:{"#ff4d8d" if is_m else "#9a9aaa"};">Mirror</div>
        <div style="font-size:0.65rem; color:#9a9aaa;">Selfie mode</div>
    </div>
    """, unsafe_allow_html=True)
    if is_m:
        st.markdown('<div class="btn-sel">', unsafe_allow_html=True)
    if st.button("✓ Mirror" if is_m else "Pilih", key="m_on", use_container_width=True):
        st.session_state.mirror = True
        st.rerun()
    if is_m:
        st.markdown('</div>', unsafe_allow_html=True)

with mc2:
    st.markdown(f"""
    <div style="background:{"#fff0f5" if not is_m else "white"}; border:2px solid {"#ff4d8d" if not is_m else "#e8e8f0"};
        border-radius:14px; padding:0.8rem; text-align:center; margin-bottom:6px;">
        <div style="font-size:1.3rem;">📷</div>
        <div style="font-size:0.8rem; font-weight:800; color:{"#ff4d8d" if not is_m else "#9a9aaa"};">Normal</div>
        <div style="font-size:0.65rem; color:#9a9aaa;">Aslinya</div>
    </div>
    """, unsafe_allow_html=True)
    if not is_m:
        st.markdown('<div class="btn-sel">', unsafe_allow_html=True)
    if st.button("✓ Normal" if not is_m else "Pilih", key="m_off", use_container_width=True):
        st.session_state.mirror = False
        st.rerun()
    if not is_m:
        st.markdown('</div>', unsafe_allow_html=True)