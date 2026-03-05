"""pages/4_filter.py — Filter & download"""

import streamlit as st
import qrcode
import io
from utils import FILTERS, build_strip, pil_to_bytes, FRAMES
from db import update_session, upload_strip
from datetime import datetime
from style import GLOBAL_CSS, step_bar

st.set_page_config(page_title="Gamma PhotoBooth · Filter", page_icon="✨",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.block-container { padding: 1.5rem 2.5rem !important; max-width: 1200px !important; }

.filter-card {
    background: white;
    border: 2.5px solid #e8e8f0;
    border-radius: 16px;
    padding: 0.8rem 0.5rem;
    text-align: center;
    transition: all 0.2s;
    margin-bottom: 6px;
}
.filter-card.sel {
    border-color: #ff4d8d !important;
    background: #fff5f8 !important;
    box-shadow: 0 4px 15px rgba(255,77,141,0.2) !important;
}
.f-icon { font-size: 1.5rem; display: block; margin-bottom: 4px; }
.f-name { font-size: 0.72rem; font-weight: 800; color: #4a4a5a; }

.qr-card {
    background: white;
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.08);
    border: 1.5px solid #f0f0f0;
    text-align: center;
}
.btn-print > button {
    background: linear-gradient(135deg, #ff4d8d, #e0005a) !important;
    font-size: 1.1rem !important;
    font-weight: 900 !important;
    letter-spacing: 2px !important;
    padding: 1rem !important;
    box-shadow: 0 6px 25px rgba(255,77,141,0.45) !important;
}
.btn-home > button {
    background: white !important;
    color: #9a9aaa !important;
    border: 2px solid #e8e8f0 !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}
.btn-home > button:hover { color: #ff4d8d !important; border-color: #ffb3ce !important; transform: none !important; box-shadow: none !important; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("session_id") or not st.session_state.get("final_photos"):
    st.warning("Sesi tidak valid.")
    if st.button("← Home"):
        st.switch_page("app.py")
    st.stop()

photos = st.session_state.final_photos
frame_choice = st.session_state.get("frame_choice", list(FRAMES.keys())[0])

if "selected_filter" not in st.session_state or st.session_state.selected_filter is None:
    st.session_state.selected_filter = "Natural"
if "strip_ready" not in st.session_state or st.session_state.strip_ready is None:
    st.session_state.strip_ready = False
if "strip_url" not in st.session_state:
    st.session_state.strip_url = None

FILTER_ICONS = {
    "Natural":"🎞️","Soft":"🌸","Warm":"🌅","Cool":"🧊",
    "B&W":"🖤","Vintage":"📷","Vivid":"🌈","Faded":"🌫️"
}

st.markdown(step_bar(4), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# DONE SCREEN
# ══════════════════════════════════════════════════════
if st.session_state.strip_ready:
    h_back, h_title, _ = st.columns([1, 4, 1])
    with h_back:
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("← Ubah Filter"):
            st.session_state.strip_ready = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with h_title:
        st.markdown('<h2 style="text-align:center; font-size:1.5rem; font-weight:900; letter-spacing:3px; margin:0; color:#2a2a3a;">STRIP SIAP! 🎉</h2>', unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col_strip, col_dl = st.columns([1, 1], gap="large")

    with col_strip:
        strip = build_strip(photos, frame_choice, st.session_state.selected_filter)
        st.image(strip, use_container_width=True)
        st.markdown(f"""
        <div style="background:#fafafa; border-radius:12px; padding:0.8rem; margin-top:0.8rem; display:flex; justify-content:space-around;">
            <div style="text-align:center;">
                <div style="font-size:0.65rem; color:#9a9aaa; font-weight:700;">FILTER</div>
                <div style="font-size:0.85rem; font-weight:800; color:#ff4d8d;">{FILTER_ICONS.get(st.session_state.selected_filter,'')} {st.session_state.selected_filter}</div>
            </div>
            <div style="width:1px; background:#e8e8f0;"></div>
            <div style="text-align:center;">
                <div style="font-size:0.65rem; color:#9a9aaa; font-weight:700;">FRAME</div>
                <div style="font-size:0.85rem; font-weight:800; color:#2a2a3a;">{frame_choice}</div>
            </div>
            <div style="width:1px; background:#e8e8f0;"></div>
            <div style="text-align:center;">
                <div style="font-size:0.65rem; color:#9a9aaa; font-weight:700;">FOTO</div>
                <div style="font-size:0.85rem; font-weight:800; color:#2a2a3a;">{len(photos)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_dl:
        strip_url = st.session_state.get("strip_url")

        if strip_url:
            def make_qr(url):
                qr = qrcode.QRCode(version=2, box_size=9, border=3,
                                   error_correction=qrcode.constants.ERROR_CORRECT_M)
                qr.add_data(url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="#1a1a2e", back_color="#ffffff")
                buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()

            st.markdown('<div class="qr-card">', unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size:2rem; margin-bottom:0.5rem;">📱</div>
            <p style="font-size:0.8rem; font-weight:800; color:#9a9aaa; letter-spacing:3px; margin-bottom:1rem;">SCAN UNTUK DOWNLOAD</p>
            """, unsafe_allow_html=True)
            st.image(make_qr(strip_url), use_container_width=True)
            st.markdown(f"""
            <div style="background:#fafafa; border-radius:12px; padding:1rem; margin-top:1rem; text-align:left;">
                <p style="font-size:0.75rem; font-weight:800; color:#4a4a5a; margin:0 0 0.6rem;">Cara Download:</p>
                <p style="font-size:0.78rem; color:#9a9aaa; line-height:2; margin:0;">
                    1. Scan QR dengan kamera HP<br>
                    2. Foto terbuka di browser<br>
                    3. Tekan & tahan → Simpan Gambar
                </p>
            </div>
            <a href="{strip_url}" target="_blank"
               style="display:block; margin-top:0.8rem; font-size:0.75rem; color:#ff4d8d; font-weight:700; text-decoration:none;">
               Atau klik link ini →
            </a>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            fallback = st.session_state.get("strip_bytes_fallback")
            if fallback:
                st.markdown('<div class="btn-print">', unsafe_allow_html=True)
                st.download_button("⬇️  Download Strip", data=fallback,
                                   file_name="gamma_photobooth.png", mime="image/png",
                                   use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-home">', unsafe_allow_html=True)
        if st.button("🏠  Sesi Baru", use_container_width=True):
            for k in ["session_id","order_id","payment_url","photos","final_photos",
                      "frame_choice","mirror","selected_filter","strip_ready","strip_url",
                      "strip_bytes_fallback","start_time","active_slot","n_photos",
                      "countdown_active","current_shot","shot_photos","phase",
                      "countdown_start","payment_start"]:
                st.session_state[k] = None
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# FILTER SELECTION SCREEN
# ══════════════════════════════════════════════════════
else:
    h_back, h_title, h_next = st.columns([1, 4, 1])
    with h_back:
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("← BACK"):
            st.switch_page("pages/3_shoot.py")
        st.markdown('</div>', unsafe_allow_html=True)
    with h_title:
        st.markdown('<h2 style="text-align:center; font-size:1.5rem; font-weight:900; letter-spacing:3px; margin:0; color:#2a2a3a;">PILIH FILTER</h2>', unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col_filters, col_preview = st.columns([1, 1], gap="large")

    with col_filters:
        st.markdown('<p style="font-size:0.75rem; font-weight:800; color:#9a9aaa; letter-spacing:2px; margin-bottom:0.8rem;">FILTER</p>', unsafe_allow_html=True)
        filter_list = list(FILTER_ICONS.items())
        rows = [filter_list[:4], filter_list[4:]]
        for row in rows:
            fcols = st.columns(4, gap="small")
            for ci, (fname, ficon) in enumerate(row):
                with fcols[ci]:
                    is_sel = st.session_state.selected_filter == fname
                    st.markdown(f"""
                    <div class="filter-card {'sel' if is_sel else ''}">
                        <span class="f-icon">{ficon}</span>
                        <div class="f-name" style="color:{'#ff4d8d' if is_sel else '#4a4a5a'};">{fname}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if is_sel:
                        st.markdown('<div class="btn-sel">', unsafe_allow_html=True)
                    if st.button("✓" if is_sel else "Pilih", key=f"flt_{fname}", use_container_width=True):
                        st.session_state.selected_filter = fname
                        st.rerun()
                    if is_sel:
                        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-print">', unsafe_allow_html=True)
        if st.button("🖨️  CETAK STRIP", use_container_width=True):
            with st.spinner("Memproses..."):
                strip = build_strip(photos, frame_choice, st.session_state.selected_filter)
                strip_bytes = pil_to_bytes(strip)
                try:
                    url = upload_strip(st.session_state.session_id, strip_bytes)
                    st.session_state.strip_url = url
                except Exception:
                    st.session_state.strip_bytes_fallback = strip_bytes
                    st.session_state.strip_url = None
                update_session(
                    st.session_state.session_id,
                    filter_choice=st.session_state.selected_filter,
                    strip_url=st.session_state.strip_url,
                    status="completed",
                    completed_at=datetime.utcnow().isoformat(),
                )
                st.session_state.strip_ready = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_preview:
        st.markdown('<p style="font-size:0.75rem; font-weight:800; color:#9a9aaa; letter-spacing:2px; margin-bottom:0.8rem;">PREVIEW</p>', unsafe_allow_html=True)
        strip = build_strip(photos, frame_choice, st.session_state.selected_filter)
        st.image(strip, use_container_width=True)