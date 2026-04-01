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

# ── Handle query params (back / restart / goto home) ──────────────────────────
if st.query_params.get("action") in ("back", "restart"):
    st.query_params.clear()
    st.session_state.payment_start = None
    st.switch_page("app.py")

if st.query_params.get("goto") == "home":
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

html, body, .stApp {
    overflow: hidden !important;
    height: 100% !important;
    margin: 0 !important;
}
section[data-testid="stAppViewContainer"],
section[data-testid="stAppViewContainer"] > div {
    height: 100vh !important;
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
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
div[data-testid="stSpinner"],
.stButton > button { display: none !important; }

/* ── Layout utama ── */
.pay-outer {
    width: 100%;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 2rem;
    box-sizing: border-box;
}
.pay-card {
    background: #2a2a32;
    border-radius: 24px;
    padding: 1.2rem 1.8rem 1.5rem;
    width: 100%;
    max-width: 700px;
    box-shadow: 0 40px 80px rgba(0,0,0,0.5);
    position: relative;
    box-sizing: border-box;
}

/* ── Header ── */
.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.header-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    color: #888899;
    letter-spacing: 5px;
}
.timer-wrap {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 2px;
}

/* ── Body ── */
.card-body {
    display: flex;
    gap: 1.2rem;
    align-items: flex-start;
}

/* ── Kiri: QR ── */
.col-qr {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.qr-frame {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 14px;
    background-color: white;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    padding: 0.5rem;
    box-sizing: border-box;
    margin-bottom: 0.6rem;
}
.amount-label {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    text-align: center;
    margin-bottom: 0.2rem;
}
.order-chip {
    font-family: 'Space Mono', monospace;
    font-size: 0.48rem;
    color: #555566;
    letter-spacing: 1px;
    background: #1e1e25;
    padding: 2px 10px;
    border-radius: 20px;
    text-align: center;
}

/* ── Kanan: mascot + steps ── */
.col-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: stretch;
}
.mascot-wrap {
    width: 100%;
    height: 120px;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center bottom;
    margin-bottom: 0;
    position: relative;
    z-index: 1;
}
.steps-box {
    background: #1e1e25;
    border: 1px solid #3a3a45;
    border-radius: 16px;
    padding: 1rem 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
    position: relative;
    z-index: 1;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem;
    color: #888899;
}
.step-dot {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff4d8d, #e0005a);
    color: white;
    font-size: 0.55rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

/* ── Expired overlay ── */
.expired-overlay {
    position: absolute;
    inset: 0;
    background: rgba(13,13,15,0.85);
    border-radius: 24px;
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
    text-decoration: none;
}
.restart-btn:hover { background: #3a3a45; color: #aaaacc; }

/* ── No-session screen ── */
.nosession-outer {
    width: 100%;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}
.nosession-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
}
.nosession-btn {
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: #2a2a32;
    border: 1.5px solid #3a3a45;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.2s;
    text-decoration: none;
}
.nosession-btn:hover { background: #3a3a45; }
.nosession-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.55rem;
    color: #555566;
    letter-spacing: 3px;
}
</style>
""", unsafe_allow_html=True)

# ── No session: tampilkan tombol reload di tengah ─────────────────────────────
if not st.session_state.get("session_id"):
    st.markdown("""
    <div class="nosession-outer">
      <div class="nosession-wrap">
        <a class="nosession-btn" href="?goto=home" title="Kembali ke halaman awal">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M4 12C4 7.58 7.58 4 12 4C14.76 4 17.2 5.36 18.72 7.46L16 7.46"
              stroke="#888899" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20 12C20 16.42 16.42 20 12 20C9.24 20 6.8 18.64 5.28 16.54L8 16.54"
              stroke="#888899" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </a>
        <span class="nosession-label">MULAI ULANG</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Session valid: lanjut render halaman pembayaran ───────────────────────────
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

qr_b64     = base64.b64encode(make_qr(payment_url)).decode() if payment_url else ""
mascot_b64 = load_asset_b64("karakter.png")

back_svg = """<a href="?action=back" style="display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;opacity:0.7;text-decoration:none;">
  <svg width="34" height="34" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="10" stroke="#aaaacc" stroke-width="1.5"/>
    <path d="M13.5 8.5L9.5 12L13.5 15.5" stroke="#aaaacc" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</a>"""

expired_overlay = """
<div class="expired-overlay">
  <span class="expired-text">&#9201; WAKTU HABIS</span>
  <a class="restart-btn" href="?action=restart">MULAI ULANG</a>
</div>
""" if is_expired else ""

st.markdown(f"""
<div class="pay-outer">
<div class="pay-card">
  {expired_overlay}
  <div class="card-header">
    <div>{back_svg}</div>
    <span class="header-title">PEMBAYARAN</span>
    <div class="timer-wrap">
      <svg width="26" height="26" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="#3a3a45" stroke-width="9"/>
        <circle cx="50" cy="50" r="45" fill="none" stroke="{ring_color}" stroke-width="9"
          stroke-dasharray="283" stroke-dashoffset="{283 - pct}"
          stroke-linecap="round" transform="rotate(-90 50 50)"/>
      </svg>
      <span style="color:{ring_color}">{mins:02d}:{secs:02d}</span>
    </div>
  </div>
  <div class="card-body">
    <div class="col-qr">
      <div class="qr-frame" style="background-image:url('data:image/png;base64,{qr_b64}');"></div>
      <div class="amount-label">Rp 10.000</div>
      <div class="order-chip">{order_id}</div>
    </div>
    <div class="col-info">
      <div class="mascot-wrap" style="background-image:url('data:image/png;base64,{mascot_b64}');"></div>
      <div class="steps-box">
        <div class="step-item"><div class="step-dot">1</div><span>Buka e-wallet atau m-banking</span></div>
        <div class="step-item"><div class="step-dot">2</div><span>Pilih menu Scan / QRIS</span></div>
        <div class="step-item"><div class="step-dot">3</div><span>Scan QR di sebelah kiri</span></div>
        <div class="step-item"><div class="step-dot">4</div><span>Konfirmasi Rp 10.000</span></div>
        <div class="step-item"><div class="step-dot">5</div><span>Tunggu redirect otomatis</span></div>
      </div>
    </div>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

if not is_expired:
    time.sleep(0.8)
    st.rerun()