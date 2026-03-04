"""pages/4_filter.py — Filter & cetak"""

import streamlit as st
import qrcode
import io
from utils import FILTERS, build_strip, pil_to_bytes, FRAMES
from db import update_session, upload_strip
from datetime import datetime
from style import GLOBAL_CSS, step_indicator

st.set_page_config(page_title="PhotoBooth · Filter", page_icon="✨", layout="centered", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.filter-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 1rem; }
.filter-card {
    background: white;
    border: 2px solid #ebd5f0;
    border-radius: 14px;
    padding: 0.8rem 0.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
}
.filter-card.sel {
    border-color: #9c7bb5 !important;
    background: #f3eaff !important;
    box-shadow: 0 4px 12px rgba(156,123,181,0.2) !important;
}
.f-icon { font-size: 1.4rem; display: block; margin-bottom: 4px; }
.f-name { font-size: 0.65rem; font-weight: 800; color: #7b5ea7; }

.qr-card {
    background: linear-gradient(135deg, #fff0f6, #f3eaff);
    border: 2px solid #f8bbd0;
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 30px rgba(240,98,146,0.15);
}
.success-title { font-size: 1.8rem; font-weight: 900; color: #e91e8c; margin: 0.5rem 0 0.3rem; }
.success-sub { font-size: 0.8rem; color: #a68ab0; margin: 0; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("session_id") or not st.session_state.get("final_photos"):
    st.warning("Sesi tidak valid.")
    if st.button("← Home"):
        st.switch_page("app.py")
    st.stop()

photos = st.session_state.final_photos
frame_choice = st.session_state.get("frame_choice", list(FRAMES.keys())[0])

if "selected_filter" not in st.session_state:
    st.session_state.selected_filter = "Original"
if "strip_ready" not in st.session_state:
    st.session_state.strip_ready = False
if "strip_url" not in st.session_state:
    st.session_state.strip_url = None

FILTER_ICONS = {
    "Original":"🎞️","Grayscale":"🖤","Vintage":"📷","Film Noir":"🎬",
    "Warm Glow":"🌅","Cool Tone":"🧊","Faded":"🌫️","Vivid":"🌈"
}

st.markdown(step_indicator(4), unsafe_allow_html=True)

if not st.session_state.strip_ready:
    st.markdown("""
    <div class="page-title">
        <span class="emoji">✨</span>
        <h1>Pilih Filter</h1>
        <p>Pilih filter yang kamu suka, lalu cetak!</p>
    </div>
    """, unsafe_allow_html=True)

    # Filter grid
    st.markdown('<span class="sec-label">Filter Foto</span>', unsafe_allow_html=True)
    filter_list = list(FILTER_ICONS.items())
    row1 = filter_list[:4]
    row2 = filter_list[4:]

    for row in [row1, row2]:
        cols = st.columns(4, gap="small")
        for i, (fname, ficon) in enumerate(row):
            with cols[i]:
                is_sel = st.session_state.selected_filter == fname
                st.markdown(f"""
                <div class="filter-card {'sel' if is_sel else ''}">
                    <span class="f-icon">{ficon}</span>
                    <div class="f-name">{fname}</div>
                </div>
                """, unsafe_allow_html=True)
                if is_sel:
                    st.markdown('<div class="btn-selected">', unsafe_allow_html=True)
                if st.button("✓" if is_sel else "Pilih", key=f"flt_{fname}", use_container_width=True):
                    st.session_state.selected_filter = fname
                    st.rerun()
                if is_sel:
                    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Preview strip
    st.markdown('<span class="sec-label">👁 Preview Strip</span>', unsafe_allow_html=True)
    strip = build_strip(photos, frame_choice, st.session_state.selected_filter)
    _, prev_col, _ = st.columns([1, 2, 1])
    with prev_col:
        st.image(strip, use_container_width=True)

    st.markdown(f"""
    <div style="background:white; border:1.5px solid #ebd5f0; border-radius:14px; padding:1rem; margin:1rem 0; display:flex; justify-content:space-around; text-align:center;">
        <div><div style="font-size:0.65rem; color:#a68ab0; font-weight:700;">FILTER</div><div style="font-size:0.85rem; font-weight:800; color:#7b5ea7;">{FILTER_ICONS.get(st.session_state.selected_filter,'')} {st.session_state.selected_filter}</div></div>
        <div style="width:1px; background:#ebd5f0;"></div>
        <div><div style="font-size:0.65rem; color:#a68ab0; font-weight:700;">FRAME</div><div style="font-size:0.85rem; font-weight:800; color:#7b5ea7;">{frame_choice}</div></div>
        <div style="width:1px; background:#ebd5f0;"></div>
        <div><div style="font-size:0.65rem; color:#a68ab0; font-weight:700;">FOTO</div><div style="font-size:0.85rem; font-weight:800; color:#7b5ea7;">{len(photos)} slot</div></div>
    </div>
    """, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 4, 1])
    with btn_col:
        if st.button("🖨️  Cetak Strip Sekarang!", use_container_width=True):
            with st.spinner("Memproses strip..."):
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

else:
    # ── Done screen ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-title">
        <span class="emoji">🎉</span>
        <h1>Strip Siap!</h1>
        <p>Scan QR untuk download foto kamu</p>
    </div>
    """, unsafe_allow_html=True)

    strip_url = st.session_state.get("strip_url")

    if strip_url:
        def make_qr(url):
            qr = qrcode.QRCode(version=1, box_size=8, border=3,
                                error_correction=qrcode.constants.ERROR_CORRECT_L)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#e91e8c", back_color="#ffffff")
            buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()

        _, qr_col, _ = st.columns([1, 2, 1])
        with qr_col:
            st.markdown('<div class="qr-card">', unsafe_allow_html=True)
            st.markdown('<p style="font-size:0.75rem; font-weight:800; color:#a68ab0; margin-bottom:0.8rem; letter-spacing:2px;">📱 SCAN UNTUK DOWNLOAD</p>', unsafe_allow_html=True)
            st.image(make_qr(strip_url), use_container_width=True)
            st.markdown(f'<a href="{strip_url}" target="_blank" style="font-size:0.75rem; color:#f06292; font-weight:700;">Atau buka link ini →</a>', unsafe_allow_html=True)
            st.markdown("""
            <div style="background:white; border-radius:10px; padding:0.8rem; margin-top:0.8rem; text-align:left;">
                <p style="font-size:0.7rem; font-weight:800; color:#7b5ea7; margin:0 0 0.5rem;">Cara Download:</p>
                <p style="font-size:0.72rem; color:#a68ab0; margin:0; line-height:1.8;">
                    1. Scan QR atau buka link<br>
                    2. Tekan & tahan gambar<br>
                    3. Pilih "Simpan Gambar"
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        fallback = st.session_state.get("strip_bytes_fallback")
        if fallback:
            _, dl_col, _ = st.columns([1, 3, 1])
            with dl_col:
                st.download_button("⬇️  Download Strip", data=fallback,
                                   file_name="photobooth_strip.png", mime="image/png",
                                   use_container_width=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    _, c1, c2, _ = st.columns([1, 2, 2, 1])
    with c1:
        st.markdown('<div class="btn-sec">', unsafe_allow_html=True)
        if st.button("← Ubah Filter", use_container_width=True):
            st.session_state.strip_ready = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("🏠 Sesi Baru", use_container_width=True):
            for k in ["session_id","order_id","payment_url","photos","final_photos",
                      "frame_choice","mirror","selected_filter","strip_ready",
                      "strip_url","strip_bytes_fallback","start_time","active_slot"]:
                st.session_state.pop(k, None)
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)