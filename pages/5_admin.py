"""
pages/5_admin.py — Panel Admin PhotoBooth
Login dengan JWT-style session (password di secrets.toml)
"""

import streamlit as st
import hashlib
import hmac
from datetime import datetime
from db import get_all_sessions

st.set_page_config(page_title="PhotoBooth · Admin", page_icon="🔐", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&display=swap');
html, body, [class*="css"] { background:#0a0a0a; color:#f0f0f0; font-family:'Space Mono',monospace; }
.stApp { background:#0a0a0a; }
.section-label {
    font-family:'Bebas Neue',cursive; letter-spacing:4px; color:#f5e642;
    font-size:1.3rem; border-left:4px solid #f5e642; padding-left:10px; margin:1rem 0 0.6rem;
}
.stat-card {
    background:#161616; border:1px solid #2a2a2a; border-radius:4px;
    padding:1.2rem; text-align:center;
}
.stat-number { font-family:'Bebas Neue',cursive; font-size:2.5rem; color:#f5e642; letter-spacing:4px; margin:0; }
.stat-label { color:#555; font-size:0.6rem; letter-spacing:3px; text-transform:uppercase; }
.divider { border:none; border-top:1px solid #1e1e1e; margin:1.2rem 0; }
.badge-paid { background:#1b5e20; color:#81c784; padding:2px 8px; border-radius:2px; font-size:0.6rem; letter-spacing:2px; }
.badge-pending { background:#3e2723; color:#ffb74d; padding:2px 8px; border-radius:2px; font-size:0.6rem; letter-spacing:2px; }
.badge-completed { background:#0d47a1; color:#90caf9; padding:2px 8px; border-radius:2px; font-size:0.6rem; letter-spacing:2px; }
.stTextInput input { background:#161616!important; color:#f0f0f0!important; border:1px solid #333!important; border-radius:2px!important; font-family:'Space Mono',monospace!important; }
.stButton > button {
    background:#f5e642!important; color:#0a0a0a!important; border:none!important;
    border-radius:2px!important; font-family:'Bebas Neue',cursive!important;
    letter-spacing:3px!important; font-size:1rem!important; padding:0.7rem 2rem!important;
}
.stDataFrame { border:1px solid #2a2a2a!important; border-radius:4px!important; }
</style>
""", unsafe_allow_html=True)


def check_password(password: str) -> bool:
    correct = st.secrets.get("ADMIN_PASSWORD", "admin123")
    return hmac.compare_digest(
        hashlib.sha256(password.encode()).hexdigest(),
        hashlib.sha256(correct.encode()).hexdigest(),
    )


# ── Login gate ─────────────────────────────────────────────────────────────────
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.markdown("<h1 style='text-align:center; font-family:Bebas Neue,cursive; font-size:3rem; color:#f5e642; letter-spacing:8px;'>🔐 ADMIN PANEL</h1>", unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<p style='color:#888; font-size:0.7rem; letter-spacing:3px; text-align:center;'>MASUKKAN PASSWORD ADMIN</p>", unsafe_allow_html=True)
        pw = st.text_input("Password", type="password", label_visibility="collapsed")
        if st.button("MASUK"):
            if check_password(pw):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Password salah.")
    st.stop()

# ── Dashboard ──────────────────────────────────────────────────────────────────
st.markdown("<h1 style='font-family:Bebas Neue,cursive; font-size:2.5rem; color:#f5e642; letter-spacing:8px;'>ADMIN PANEL</h1>", unsafe_allow_html=True)

col_logout, _ = st.columns([1, 5])
with col_logout:
    if st.button("LOGOUT"):
        st.session_state.admin_logged_in = False
        st.rerun()

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
with st.spinner("Memuat data..."):
    sessions = get_all_sessions(limit=200)

# ── Stats ──────────────────────────────────────────────────────────────────────
total = len(sessions)
paid = sum(1 for s in sessions if s.get("status") in ("paid", "completed"))
completed = sum(1 for s in sessions if s.get("status") == "completed")
revenue = paid * 10000

today_str = datetime.utcnow().strftime("%Y-%m-%d")
today_sessions = [s for s in sessions if s.get("created_at", "").startswith(today_str)]
today_paid = sum(1 for s in today_sessions if s.get("status") in ("paid", "completed"))

col1, col2, col3, col4, col5 = st.columns(5)
stats = [
    (str(total), "TOTAL SESI"),
    (str(paid), "SUDAH BAYAR"),
    (str(completed), "SELESAI"),
    (f"Rp {revenue:,}".replace(",", "."), "TOTAL REVENUE"),
    (str(today_paid), "HARI INI"),
]
for col, (num, label) in zip([col1, col2, col3, col4, col5], stats):
    with col:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{num}</div>
            <div class='stat-label'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Filters ────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-label'>HISTORY SESI</div>", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
with col_f1:
    date_filter = st.date_input("Filter tanggal", value=None, label_visibility="visible")
with col_f2:
    status_filter = st.selectbox("Filter status", ["Semua", "pending", "paid", "completed"], label_visibility="visible")
with col_f3:
    if st.button("🔄 REFRESH"):
        st.rerun()

# Apply filters
filtered = sessions
if date_filter:
    date_str = str(date_filter)
    filtered = [s for s in filtered if s.get("created_at", "").startswith(date_str)]
if status_filter != "Semua":
    filtered = [s for s in filtered if s.get("status") == status_filter]

# ── Table ──────────────────────────────────────────────────────────────────────
if not filtered:
    st.markdown("<p style='color:#444; font-size:0.7rem; letter-spacing:2px;'>Tidak ada data.</p>", unsafe_allow_html=True)
else:
    for s in filtered:
        status = s.get("status", "pending")
        badge_class = {"paid": "badge-paid", "completed": "badge-completed"}.get(status, "badge-pending")

        created = s.get("created_at", "")[:16].replace("T", " ")
        order_id = s.get("midtrans_order_id", "-")
        frame = s.get("frame_choice", "-")
        fil = s.get("filter_choice", "-")
        n_photos = len(s.get("photo_urls") or [])
        strip_url = s.get("strip_url", "")

        with st.expander(f"📸 {created} — {order_id} — {status.upper()}", expanded=False):
            col_a, col_b, col_c = st.columns([2, 2, 2])
            with col_a:
                st.markdown(f"""
                <p style='font-size:0.65rem; color:#888; letter-spacing:2px; margin:0;'>SESSION ID</p>
                <p style='font-size:0.7rem; color:#f0f0f0; word-break:break-all;'>{s.get("id","")}</p>
                <p style='font-size:0.65rem; color:#888; letter-spacing:2px; margin-top:0.5rem;'>STATUS</p>
                <span class='{badge_class}'>{status.upper()}</span>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <p style='font-size:0.65rem; color:#888; letter-spacing:2px; margin:0;'>FRAME</p>
                <p style='font-size:0.8rem; color:#f0f0f0;'>{frame}</p>
                <p style='font-size:0.65rem; color:#888; letter-spacing:2px; margin-top:0.5rem;'>FILTER</p>
                <p style='font-size:0.8rem; color:#f0f0f0;'>{fil}</p>
                <p style='font-size:0.65rem; color:#888; letter-spacing:2px; margin-top:0.5rem;'>JUMLAH FOTO</p>
                <p style='font-size:0.8rem; color:#f0f0f0;'>{n_photos}</p>
                """, unsafe_allow_html=True)
            with col_c:
                if strip_url:
                    st.markdown(f"<p style='font-size:0.65rem; color:#888; letter-spacing:2px;'>STRIP</p>", unsafe_allow_html=True)
                    st.image(strip_url, width=150)
                    st.markdown(f"<a href='{strip_url}' target='_blank' style='color:#f5e642; font-size:0.6rem;'>Buka full size</a>", unsafe_allow_html=True)
                else:
                    st.markdown("<p style='color:#444; font-size:0.65rem;'>Strip belum tersedia.</p>", unsafe_allow_html=True)

            # Individual photos
            photo_urls = s.get("photo_urls") or []
            if photo_urls:
                st.markdown("<p style='font-size:0.65rem; color:#888; letter-spacing:2px; margin-top:0.5rem;'>FOTO INDIVIDUAL</p>", unsafe_allow_html=True)
                pcols = st.columns(min(len(photo_urls), 4))
                for pi, purl in enumerate(photo_urls[:4]):
                    if purl:
                        with pcols[pi]:
                            st.image(purl, use_container_width=True, caption=f"Foto {pi+1}")
