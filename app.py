"""app.py — Landing page Fotosphere"""

import streamlit as st
import uuid
import base64
import os
from payment import create_payment, generate_order_id
from db import create_session
from style import GLOBAL_CSS

st.set_page_config(page_title="Fotosphere", page_icon="assets/icon.png",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
html, body {
    overflow: hidden !important;
    overscroll-behavior: none !important;
    height: 100% !important;
    margin: 0 !important;
}
.stApp {
    background: linear-gradient(145deg, #f0f0f5 0%, #fafafa 50%, #f5f0f8 100%) !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    overflow: hidden !important;
    overscroll-behavior: none !important;
}
.stApp > .main {
    display: flex !important;
    flex-direction: column !important;
    flex: 1 !important;
    justify-content: center !important;
    overflow: hidden !important;
}
section[data-testid="stAppViewContainer"] { overflow: hidden !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    min-height: 100vh !important;
    flex: 1 !important;
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
.stButton > button {
    background: linear-gradient(135deg, #ff4d8d, #e0005a) !important;
    font-size: 1.5rem !important;
    font-weight: 900 !important;
    letter-spacing: 3px !important;
    padding: 1.2rem 3rem !important;
    border-radius: 60px !important;
    box-shadow: none !important;
    width: 100% !important;
    cursor: pointer !important;
}
.stButton > button:hover { opacity: 0.9 !important; box-shadow: none !important; transform: none !important; }
.stButton > button p, .stButton > button span, .stButton > button div {
    color: white !important; background: transparent !important;
    border: none !important; padding: 0 !important; margin: 0 !important;
}

/* Loading hint */
.loading-hint {
    margin-top: 1rem;
    text-align: center;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 3px;
    color: #c0a0b0;
    animation: fadeInUp 0.3s ease both;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes dots {
    0%   { content: ''; }
    25%  { content: '.'; }
    50%  { content: '..'; }
    75%  { content: '...'; }
}
.loading-hint::after {
    content: '';
    animation: dots 1.2s steps(4, end) infinite;
}

/* Loading overlay */
#loading-overlay {
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(8px);
    z-index: 9999;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
}
#loading-overlay.show { display: flex; }
.loading-eye { width: 80px; height: 80px; animation: pulse 1.2s ease-in-out infinite; }
.loading-text { font-size: 0.85rem; font-weight: 900; letter-spacing: 4px; color: #2a2a3a; animation: fade 1.2s ease-in-out infinite; }
.loading-dots::after { content: ''; animation: dots 1.5s steps(4, end) infinite; }
@keyframes pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.15); opacity: 0.7; } }
@keyframes fade { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
""", unsafe_allow_html=True)

for k in ["session_id","order_id","payment_url","photos","final_photos",
          "frame_choice","mirror","selected_filter","strip_ready",
          "strip_url","strip_bytes_fallback","start_time","active_slot",
          "n_photos","countdown_active","current_shot","shot_photos","loading"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ── TAHAP 2: proses payment setelah loading text sudah kerender ────────────────
if st.session_state.loading == "processing":
    try:
        session_id = str(uuid.uuid4())
        order_id = generate_order_id()
        payment = create_payment(order_id, amount=10000)
        create_session(session_id, order_id)
        st.session_state.session_id = session_id
        st.session_state.order_id = order_id
        st.session_state.payment_url = payment["redirect_url"]
        st.session_state.loading = None
        st.switch_page("pages/1_payment.py")
    except Exception as e:
        st.session_state.loading = None
        st.error(f"Error: {e}")

# ── Helper ─────────────────────────────────────────────────────────────────────
def img_to_b64(filename):
    path = os.path.join("assets", filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        ext = filename.split(".")[-1].lower()
        mime = "image/png" if ext == "png" else f"image/{ext}"
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

# ── Layout ─────────────────────────────────────────────────────────────────────
_, center, _ = st.columns([1, 2, 1])
with center:
    icon_b64 = img_to_b64("icon.png")
    icon_html = f"<img src='{icon_b64}' style='width:100%;height:100%;object-fit:cover;'/>" if icon_b64 else "📷"
    st.markdown(
        "<div style='width:100%;display:flex;flex-direction:column;align-items:center;text-align:center;margin-bottom:2rem;'>"
        "<div style='width:90px;height:90px;margin-bottom:1rem;overflow:hidden;'>"
        f"{icon_html}"
        "</div>"
        "<div style='font-size:2.2rem;font-weight:900;color:#2a2a3a;letter-spacing:2px;margin:0;'>FOTOSPHERE</div>"
        "<div style='font-size:0.85rem;color:#9a9aaa;margin:0.3rem 0 0;letter-spacing:2px;'>✦ Self Photo Studio ✦</div>"
        "</div>",
        unsafe_allow_html=True
    )

_, btn_col, _ = st.columns([2, 3, 2])
with btn_col:
    icon_b64_loading = img_to_b64("icon.png")
    st.markdown(
        f"""
        <div id="loading-overlay">
            <img src="{icon_b64_loading}" class="loading-eye" style="border-radius:20px;"/>
            <div class="loading-text">LOADING<span class="loading-dots"></span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sembunyiin button saat loading, tampilkan saat idle
    if not st.session_state.loading:
        if st.button("TAP TO START", use_container_width=True):
            # TAHAP 1: set loading → rerun → render teks dulu
            st.session_state.loading = "show"
            st.rerun()

    # TAHAP 1 render: teks loading muncul, lalu langsung rerun ke tahap 2
    if st.session_state.loading == "show":
        st.markdown(
            "<div class='loading-hint'>MEMPERSIAPKAN SESI</div>",
            unsafe_allow_html=True
        )
        st.session_state.loading = "processing"
        st.rerun()

    # TAHAP 2 render: teks tetap ada saat proses berlangsung
    if st.session_state.loading == "processing":
        st.markdown(
            "<div class='loading-hint'>MEMPERSIAPKAN SESI</div>",
            unsafe_allow_html=True
        )

_, center2, _ = st.columns([2, 3, 2])
with center2:
    logos = [
        ("gopay.png","GoPay"),("dana.png","DANA"),("ovo.png","OVO"),
        ("linkaja.png","LinkAja"),("shopeepay.png","ShopeePay"),
        ("bca.png","BCA"),("mandiri.png","Mandiri"),("bri.png","BRI"),
        ("bni.png","BNI"),("qris.png","QRIS"),
    ]
    imgs_html = ""
    for fname, label in logos:
        b64 = img_to_b64(fname)
        if b64:
            imgs_html += f'<img src="{b64}" height="24" style="object-fit:contain;max-height:24px;">'
        else:
            imgs_html += f'<span style="font-size:0.65rem;font-weight:800;color:#666;">{label}</span>'

    st.markdown(
        "<p style='text-align:center;color:#c0c0cc;font-size:0.72rem;margin-top:0.8rem;letter-spacing:1px;'>Your Epic Shots are on the Way!</p>"
        "<div style='height:2rem;'></div>"
        "<div style='background:white;border-radius:20px;padding:0.8rem 1rem;box-shadow:0 4px 20px rgba(0,0,0,0.06);border:1.5px solid #f0f0f0;'>"
        "<p style='text-align:center;font-size:0.6rem;font-weight:700;color:#9a9aaa;letter-spacing:3px;margin:0 0 0.8rem;'>METODE PEMBAYARAN</p>"
        f"<div style='display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;justify-content:center;'>{imgs_html}</div>"
        "</div>",
        unsafe_allow_html=True
    )