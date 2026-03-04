"""app.py — Landing page PhotoBooth"""

import streamlit as st
import uuid
from payment import create_payment, generate_order_id
from db import create_session
from style import GLOBAL_CSS

st.set_page_config(page_title="PhotoBooth 📸", page_icon="📸", layout="centered", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.hero-card {
    background: linear-gradient(135deg, #fff0f6, #f3eaff);
    border: 1.5px solid #f8bbd0;
    border-radius: 24px;
    padding: 2.5rem 2rem;
    text-align: center;
    box-shadow: 0 8px 40px rgba(240,98,146,0.15);
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 3.5rem !important;
    font-weight: 900 !important;
    color: #e91e8c !important;
    letter-spacing: 2px;
    margin: 0.5rem 0 0.3rem !important;
    line-height: 1.1 !important;
}
.hero-sub { font-size: 1rem; color: #a68ab0; margin: 0; }

.feat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 1rem 0; }
.feat-item {
    background: white;
    border: 1.5px solid #ebd5f0;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
}
.feat-icon { font-size: 1.5rem; display: block; margin-bottom: 5px; }
.feat-text { font-size: 0.78rem; font-weight: 700; color: #7b5ea7; }
.feat-sub { font-size: 0.65rem; color: #a68ab0; margin-top: 2px; }

.steps-row { display:flex; gap:0; margin: 1rem 0; }
.step-item { flex:1; text-align:center; position:relative; }
.step-item::after { content:'›'; position:absolute; right:0; top:50%; transform:translateY(-50%); color:#ebd5f0; font-size:1.2rem; }
.step-item:last-child::after { display:none; }
.step-circle {
    width:36px; height:36px; border-radius:50%;
    background: linear-gradient(135deg,#f06292,#e91e8c);
    display:flex; align-items:center; justify-content:center;
    margin:0 auto 5px; font-size:1rem;
    box-shadow: 0 4px 10px rgba(240,98,146,0.3);
}
.step-lbl { font-size:0.6rem; font-weight:800; color:#a68ab0; letter-spacing:1px; }
</style>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "order_id" not in st.session_state:
    st.session_state.order_id = None
if "payment_url" not in st.session_state:
    st.session_state.payment_url = None

# Hero
st.markdown("""
<div class="hero-card">
    <div style="font-size:3rem;">📸</div>
    <h1 class="hero-title">PhotoBooth</h1>
    <p class="hero-sub">Foto cantik, filter keren, langsung download!</p>
    <div style="display:inline-block; background:white; border:2px solid #f8bbd0; border-radius:50px; padding:0.5rem 1.5rem; margin:1rem 0 0.5rem;">
        <div style="font-size:1.8rem; font-weight:900; color:#f06292;">Rp 10.000</div>
        <div style="font-size:0.75rem; color:#a68ab0; margin-top:2px;">4 foto · 5 menit · download gratis</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Features
st.markdown("""
<div class="feat-grid">
    <div class="feat-item">
        <span class="feat-icon">🌸</span>
        <div class="feat-text">6 Frame Lucu</div>
        <div class="feat-sub">berbagai tema pilihan</div>
    </div>
    <div class="feat-item">
        <span class="feat-icon">✨</span>
        <div class="feat-text">8 Filter Foto</div>
        <div class="feat-sub">vintage, vivid & more</div>
    </div>
    <div class="feat-item">
        <span class="feat-icon">🔄</span>
        <div class="feat-text">Retake Bebas</div>
        <div class="feat-sub">sampai puas dalam 5 menit</div>
    </div>
    <div class="feat-item">
        <span class="feat-icon">📱</span>
        <div class="feat-text">QR Download</div>
        <div class="feat-sub">simpan langsung ke HP</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Steps
st.markdown("""
<div class="steps-row">
    <div class="step-item"><div class="step-circle">💳</div><div class="step-lbl">BAYAR</div></div>
    <div class="step-item"><div class="step-circle">🎨</div><div class="step-lbl">FRAME</div></div>
    <div class="step-item"><div class="step-circle">📸</div><div class="step-lbl">FOTO</div></div>
    <div class="step-item"><div class="step-circle">✨</div><div class="step-lbl">FILTER</div></div>
    <div class="step-item"><div class="step-circle">⬇️</div><div class="step-lbl">DOWNLOAD</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

_, col, _ = st.columns([1, 4, 1])
with col:
    st.markdown("""
    <style>
    /* Override button max width on landing only */
    div[data-testid="stButton"] button {
        max-width: 380px !important;
        margin: 0 auto !important;
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)
    if st.button("✨  Mulai Sesi Sekarang  ✨", use_container_width=True):
        with st.spinner("Mempersiapkan sesi..."):
            try:
                session_id = str(uuid.uuid4())
                order_id = generate_order_id()
                payment = create_payment(order_id, amount=10000)
                create_session(session_id, order_id)
                st.session_state.session_id = session_id
                st.session_state.order_id = order_id
                st.session_state.payment_url = payment["redirect_url"]
                st.switch_page("pages/1_payment.py")
            except Exception as e:
                st.error(f"Gagal membuat sesi: {e}")

st.markdown("<p style='text-align:center; color:#c9a8d4; font-size:0.72rem; margin-top:0.8rem;'>🔒 Pembayaran aman via Midtrans</p>", unsafe_allow_html=True)