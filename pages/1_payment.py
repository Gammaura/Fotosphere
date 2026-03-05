"""pages/1_payment.py — Halaman QRIS payment"""

import streamlit as st
import time
import qrcode
import io
import base64
import os
from payment import check_payment_status
from db import update_session
from datetime import datetime
from style import GLOBAL_CSS, step_bar

st.set_page_config(page_title="Fotosphere · Bayar", page_icon="💳",
                   layout="wide", initial_sidebar_state="collapsed")

if st.query_params.get("action") in ("back", "restart"):
    st.query_params.clear()
    st.session_state.payment_start = None
    st.switch_page("app.py")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_asset_b64(filename):
    path = os.path.join(ROOT_DIR, "assets", filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');

html, body {
    overflow: hidden !important;
    overscroll-behavior: none !important;
    height: 100% !important;
    margin: 0 !important;
}
.stApp {
    height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    overscroll-behavior: none !important;
}
.stApp > .main {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
section[data-testid="stAppViewContainer"] {
    height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
section[data-testid="stAppViewContainer"] > div {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}
.block-container {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    max-width: 100% !important;
    min-height: 100vh !important;
    overflow: hidden !important;
}
.block-container > div {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    flex: 1 !important;
}
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stSpinner"] { display: none !important; }
.stButton > button { display: none !important; }

.pay-outer {
    width: 100%;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem 2rem;
    box-sizing: border-box;
}
.pay-card {
    background: #2a2a32;
    border-radius: 28px;
    padding: 1.5rem 2rem;
    width: 100%;
    max-width: 760px;
    margin: 0 auto;
    box-shadow: 0 40px 80px rgba(0,0,0,0.5);
    
    position: relative;
}
@keyframes slideUp {
    from { opacity:0; transform:translateY(24px); }
    to   { opacity:1; transform:translateY(0); }
}
.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.header-left { flex: 1; display: flex; align-items: center; }
.header-right { flex: 1; display: flex; align-items: center; justify-content: flex-end; }
.header-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: #888899;
    letter-spacing: 5px;
}
.timer-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 2px;
}
.card-body {
    display: flex;
    gap: 2rem;
    align-items: flex-start;
}
.col-qr {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.qr-frame {
    width: 100%;
    aspect-ratio: 1/1;
    border-radius: 16px;
    margin-bottom: 0.8rem;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    background-color: white;
    padding: 0.8rem;
    box-sizing: border-box;
}
.amount-label {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    margin-bottom: 0.3rem;
}
.order-chip {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem;
    color: #555566;
    letter-spacing: 1px;
    background: #1e1e25;
    padding: 3px 10px;
    border-radius: 20px;
    text-align: center;
}
.col-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    align-self: flex-start;
    margin-top: 2.5rem;
}
.steps-box {
    background: #1e1e25;
    border: 1px solid #3a3a45;
    border-radius: 16px;
    padding: 1.2rem 1rem;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: #888899;
    margin-bottom: 0.6rem;
}
.step-item:last-child { margin-bottom: 0; }
.step-dot {
    width: 22px; height: 22px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff4d8d, #e0005a);
    color: white;
    font-size: 0.62rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

/* ── Status box animasi ── */
.status-box {
    border-radius: 12px;
    padding: 0.65rem 1rem;
    text-align: center;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 1px;
    position: relative;
    overflow: hidden;
}
.status-expire { background:#1a1a20; border:1px solid #3a3a45; color:#555566; }
.status-ok     { background:#0e1e12; border:1px solid #1a4025; color:#4caf50; }

/* Waiting — animasi shimmer + pulse border */
.status-wait {
    background: #1e1a10;
    border: 1px solid #fb8c00;
    color: #fb8c00;
    
}

/* Shimmer sweep */
.status-wait::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(251,140,0,0.12), transparent);
    animation: shimmer 2s ease-in-out infinite;
}
@keyframes shimmer {
    0%   { left: -60%; }
    100% { left: 160%; }
}

/* Titik animasi di dalam teks */
.wait-dots::after {
    content: '';
    animation: dots 1.4s steps(4, end) infinite;
}
@keyframes dots {
    0%   { content: ''; }
    25%  { content: '.'; }
    50%  { content: '..'; }
    75%  { content: '...'; }
}

/* ── Expired overlay ── */
.expired-overlay {
    position: absolute;
    inset: 0;
    background: rgba(13,13,15,0.85);
    border-radius: 28px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    backdrop-filter: blur(4px);
    z-index: 10;
}
.expired-text {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    color: #555566;
    letter-spacing: 3px;
}
.restart-btn {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 0.7rem 2rem;
    border-radius: 60px;
    background: #2a2a35;
    color: #888899;
    border: 1px solid #3a3a45;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
}
.restart-btn:hover { background: #3a3a45; color: #aaaacc; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("session_id"):
    st.warning("Sesi tidak ditemukan.")
    if st.button("← Kembali"):
        st.switch_page("app.py")
    st.stop()

session_id  = st.session_state.session_id
order_id    = st.session_state.order_id
payment_url = st.session_state.payment_url

PAYMENT_TIMEOUT = 120
if "payment_start" not in st.session_state or st.session_state.payment_start is None:
    st.session_state.payment_start = time.time()

elapsed   = time.time() - st.session_state.payment_start
remaining = max(0, PAYMENT_TIMEOUT - elapsed)
mins, secs = int(remaining // 60), int(remaining % 60)
pct        = int((remaining / PAYMENT_TIMEOUT) * 283)
ring_color = "#e53935" if remaining <= 20 else ("#fb8c00" if remaining <= 45 else "#ff4d8d")
is_expired = remaining <= 0

def make_qr(url):
    qr = qrcode.QRCode(version=2, box_size=8, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0d0d0f", back_color="#ffffff")
    buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()

if not is_expired and payment_url:
    try:
        status = check_payment_status(order_id)
        if status == "paid":
            update_session(session_id, status="paid", paid_at=datetime.utcnow().isoformat())
            st.session_state.payment_start = None
            st.switch_page("pages/2_frame.py")
    except Exception as e:
        st.error(f"Gagal cek status: {e}")

qr_b64 = base64.b64encode(make_qr(payment_url)).decode() if payment_url else ""

back_svg = """<a href="?action=back" style="display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;opacity:0.7;text-decoration:none;">
  <svg style="width:38px;height:38px;" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="10" stroke="#aaaacc" stroke-width="1.5"/>
    <path d="M13.5 8.5L9.5 12L13.5 15.5" stroke="#aaaacc" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</a>"""

restart_url = "?action=restart"

expired_overlay = f"""
<div class="expired-overlay">
  <span class="expired-text">⏱ WAKTU HABIS</span>
  <a class="restart-btn" href="{restart_url}">MULAI ULANG</a>
</div>
""" if is_expired else ""

if is_expired:
    status_class = "status-expire"
    status_inner = "⏱ WAKTU HABIS"
else:
    status_class = "status-wait"
    status_inner = "⏳ MENUNGGU PEMBAYARAN<span class='wait-dots'></span>"

st.markdown(f"""
<div class="pay-outer">
<div class="pay-card">
  {expired_overlay}
  <div class="card-header">
    <div class="header-left">{back_svg}</div>
    <span class="header-title">PEMBAYARAN</span>
    <div class="header-right">
      <div class="timer-wrap">
        <svg width="32" height="32" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="45" fill="none" stroke="#3a3a45" stroke-width="9"/>
          <circle cx="50" cy="50" r="45" fill="none" stroke="{ring_color}" stroke-width="9"
            stroke-dasharray="283" stroke-dashoffset="{283 - pct}"
            stroke-linecap="round" transform="rotate(-90 50 50)"/>
        </svg>
        <span style="color:{ring_color};font-family:'Space Mono',monospace;">{mins:02d}:{secs:02d}</span>
      </div>
    </div>
  </div>
  <div class="card-body">
    <div class="col-qr">
      <div class="qr-frame" style="background-image:url('data:image/png;base64,{qr_b64}');"></div>
      <div class="amount-label">Rp 10.000</div>
      <div class="order-chip">{order_id}</div>
    </div>
    <div class="col-info">
      <div class="steps-box">
        <div class="step-item"><div class="step-dot">1</div><span>Buka e-wallet atau m-banking</span></div>
        <div class="step-item"><div class="step-dot">2</div><span>Pilih menu Scan / QRIS</span></div>
        <div class="step-item"><div class="step-dot">3</div><span>Scan QR di sebelah kiri</span></div>
        <div class="step-item"><div class="step-dot">4</div><span>Konfirmasi Rp 10.000</span></div>
        <div class="step-item"><div class="step-dot">5</div><span>Tunggu redirect otomatis</span></div>
      </div>
      <div class="status-box {status_class}">{status_inner}</div>
    </div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

if not is_expired:
    time.sleep(0.8)
    st.rerun()