"""pages/1_payment.py — Halaman pembayaran"""

import streamlit as st
import time
import qrcode
import io
from payment import check_payment_status
from db import update_session
from datetime import datetime
from style import GLOBAL_CSS, step_indicator

st.set_page_config(page_title="PhotoBooth · Bayar", page_icon="💳", layout="centered", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

if not st.session_state.get("session_id"):
    st.warning("Sesi tidak ditemukan.")
    if st.button("← Kembali"):
        st.switch_page("app.py")
    st.stop()

session_id = st.session_state.session_id
order_id = st.session_state.order_id
payment_url = st.session_state.payment_url

def make_qr(url):
    qr = qrcode.QRCode(version=1, box_size=7, border=3,
                       error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#e91e8c", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# Header
st.markdown(step_indicator(1), unsafe_allow_html=True)
st.markdown("""
<div class="page-title">
    <span class="emoji">💳</span>
    <h1>Pembayaran</h1>
    <p>Scan QR di bawah untuk membayar</p>
</div>
""", unsafe_allow_html=True)

# Amount card
st.markdown(f"""
<div class="card" style="text-align:center; background:linear-gradient(135deg,#fff0f6,#f3eaff);">
    <p style="font-size:0.75rem; color:#a68ab0; font-weight:700; letter-spacing:2px; margin:0 0 0.3rem;">TOTAL PEMBAYARAN</p>
    <p style="font-size:2.8rem; font-weight:900; color:#e91e8c; margin:0; line-height:1.1;">Rp 10.000</p>
    <p style="font-size:0.72rem; color:#a68ab0; margin:0.3rem 0 0;">{order_id}</p>
</div>
""", unsafe_allow_html=True)

# QR + instructions
col_qr, col_info = st.columns([1, 1], gap="large")
with col_qr:
    st.markdown('<div class="card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.75rem; font-weight:700; color:#a68ab0; margin-bottom:0.8rem;">SCAN UNTUK BAYAR</p>', unsafe_allow_html=True)
    if payment_url:
        st.image(make_qr(payment_url), use_container_width=True)
        st.markdown(f'<a href="{payment_url}" target="_blank" style="font-size:0.7rem; color:#f06292;">Atau klik di sini →</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_info:
    st.markdown("""
    <div class="card">
        <p style="font-size:0.75rem; font-weight:800; color:#7b5ea7; margin:0 0 0.8rem;">Cara Bayar</p>
        <div style="display:flex; flex-direction:column; gap:0.7rem;">
            <div style="display:flex; gap:10px; align-items:flex-start;">
                <div style="background:#f8bbd0; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:800; color:#e91e8c; flex-shrink:0;">1</div>
                <p style="font-size:0.8rem; color:#3d2c3e; margin:0;">Scan QR atau klik link</p>
            </div>
            <div style="display:flex; gap:10px; align-items:flex-start;">
                <div style="background:#f8bbd0; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:800; color:#e91e8c; flex-shrink:0;">2</div>
                <p style="font-size:0.8rem; color:#3d2c3e; margin:0;">Pilih metode pembayaran</p>
            </div>
            <div style="display:flex; gap:10px; align-items:flex-start;">
                <div style="background:#f8bbd0; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:800; color:#e91e8c; flex-shrink:0;">3</div>
                <p style="font-size:0.8rem; color:#3d2c3e; margin:0;">Selesaikan pembayaran</p>
            </div>
            <div style="display:flex; gap:10px; align-items:flex-start;">
                <div style="background:#f8bbd0; border-radius:50%; width:24px; height:24px; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:800; color:#e91e8c; flex-shrink:0;">4</div>
                <p style="font-size:0.8rem; color:#3d2c3e; margin:0;">Klik tombol <b>Cek Status</b></p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

status_ph = st.empty()
status_ph.markdown('<p style="text-align:center; color:#a68ab0; font-size:0.8rem;">⏳ Menunggu pembayaran...</p>', unsafe_allow_html=True)

_, col_btn, _ = st.columns([1, 4, 1])
with col_btn:
    if st.button("🔄  Cek Status Pembayaran", use_container_width=True):
        with st.spinner("Mengecek..."):
            status = check_payment_status(order_id)
            if status == "paid":
                update_session(session_id, status="paid", paid_at=datetime.utcnow().isoformat())
                status_ph.success("✅ Pembayaran berhasil!")
                time.sleep(1)
                st.switch_page("pages/2_frame.py")
            elif status == "failed":
                st.error("Pembayaran gagal atau expired.")
            else:
                st.warning("Belum diterima. Coba beberapa saat lagi.")

    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("← Batal", use_container_width=True):
        st.switch_page("app.py")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<p style="text-align:center; color:#c9a8d4; font-size:0.7rem; margin-top:1rem;">⏱ Pembayaran expire dalam 10 menit</p>', unsafe_allow_html=True)