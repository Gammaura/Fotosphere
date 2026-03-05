"""pages/3_shoot.py — Self photo studio, light theme"""

import streamlit as st
import streamlit.components.v1 as components
import base64
import json
from io import BytesIO
from PIL import Image
from utils import mirror_image, pil_to_bytes, FRAMES, build_strip
from db import upload_photo, update_session
from style import GLOBAL_CSS, step_bar

st.set_page_config(page_title="Fotosphere · Foto", page_icon="📸",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Guard ─────────────────────────────────────────────────────────────────────
if not st.session_state.get("session_id"):
    st.warning("Sesi tidak valid.")
    st.stop()

frame_choice = st.session_state.get("frame_choice", list(FRAMES.keys())[0])
frame        = FRAMES[frame_choice]
N            = frame["n_photos"]
mirror       = st.session_state.get("mirror", False)

if "photos" not in st.session_state or len(st.session_state.get("photos", [])) != N:
    st.session_state.photos = [None] * N
if "shoot_phase" not in st.session_state:
    st.session_state.shoot_phase = "shooting"

photos = st.session_state.photos

# ── Shared CSS ────────────────────────────────────────────────────────────────
SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@400;500;700;900&display=swap');

html, body {
    overflow: hidden !important;
    overscroll-behavior: none !important;
    height: 100% !important;
    margin: 0 !important;
}
.stApp {
    height: 100vh !important;
    overflow: hidden !important;
    background: #f8f8fc !important;
}
.stApp > .main,
section[data-testid="stAppViewContainer"],
section[data-testid="stAppViewContainer"] > div,
.block-container {
    height: 100vh !important;
    overflow: hidden !important;
    padding: 0 !important;
    max-width: 100% !important;
}
#MainMenu, footer, header { visibility: hidden; }
button[title="View fullscreen"],
div[data-testid="stImage"] > div { display: none !important; }
div[data-testid="stImage"] img { border-radius: 12px !important; }
</style>
"""

# ══════════════════════════════════════════════════════════════════════════════
# PHASE: REVIEW
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.shoot_phase == "review":
    st.markdown(SHARED_CSS, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .block-container { padding: 1.2rem 2rem !important; }

    div[data-testid="stButton"] > button {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.72rem !important; font-weight: 700 !important;
        letter-spacing: 1px !important;
        padding: 0.4rem 0 !important;
        border-radius: 30px !important;
        border: 1.5px solid #eeeef5 !important;
        background: white !important; color: #555570 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        width: 100% !important; margin-top: 6px !important;
        transition: all 0.15s !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #ff4d8d !important; color: #ff4d8d !important;
    }
    div[data-testid="stButton"] > button p { color: inherit !important; font-size: 0.72rem !important; }

    .btn-next div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #ff4d8d, #e0005a) !important;
        border-color: transparent !important; color: white !important;
        font-size: 0.8rem !important; padding: 0.6rem 0 !important;
        box-shadow: 0 6px 20px rgba(255,77,141,0.35) !important;
    }
    .btn-next div[data-testid="stButton"] > button p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

    # Step bar
    st.markdown(step_bar(3), unsafe_allow_html=True)

    # Header
    frame_display = frame_choice.split(" ", 1)[-1] if not frame_choice[0].isalpha() else frame_choice
    mode_label = "🪞 Mirror" if mirror else "📷 Normal"
    filled = sum(1 for p in photos if p is not None)

    col_back, col_title, col_info = st.columns([1, 4, 1])
    with col_back:
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("← BACK"):
            st.session_state.shoot_phase = "shooting"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.markdown(f'<h2 style="text-align:center;font-size:1.2rem;font-weight:900;letter-spacing:2px;margin:0;color:#2a2a3a;font-family:DM Sans,sans-serif;">Review Foto</h2>', unsafe_allow_html=True)
    with col_info:
        st.markdown(f'<p style="text-align:right;font-size:0.78rem;font-weight:700;color:#ff4d8d;margin:0;font-family:Space Mono,monospace;">{filled}/{N} Foto</p>', unsafe_allow_html=True)

    st.markdown('<p style="text-align:center;font-size:0.75rem;color:#9a9aaa;font-family:DM Sans,sans-serif;margin:0.3rem 0 1rem;">Mau retake foto mana? Atau langsung lanjut ke filter.</p>', unsafe_allow_html=True)

    cols = st.columns(N, gap="small")
    for i, col in enumerate(cols):
        with col:
            if photos[i] is not None:
                st.image(photos[i], use_container_width=True)
            st.markdown(f'<p style="text-align:center;color:#9a9aaa;font-size:0.58rem;font-family:Space Mono,monospace;margin:3px 0 0;">FOTO {i+1}</p>', unsafe_allow_html=True)
            if st.button(f"↺ Retake {i+1}", key=f"rt_{i}", use_container_width=True):
                photos[i] = None
                st.session_state.photos = photos
                st.session_state.shoot_phase = "shooting"
                st.rerun()

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.markdown('<div class="btn-next">', unsafe_allow_html=True)
        if st.button("✨  LANJUT KE FILTER  →", use_container_width=True):
            with st.spinner(""):
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

# ══════════════════════════════════════════════════════════════════════════════
# PHASE: SHOOTING
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown(SHARED_CSS, unsafe_allow_html=True)

    mirror_js  = "true" if mirror else "false"
    frame_name = frame_choice.split(" ", 1)[-1] if not frame_choice[0].isalpha() else frame_choice
    mode_txt   = "MIRROR" if mirror else "NORMAL"

    # Step bar di atas component
    st.markdown(step_bar(3), unsafe_allow_html=True)

    component_result = components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@400;600;700;900&display=swap');

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
    width: 100%; height: 100%;
    background: #f8f8fc;
    font-family: 'DM Sans', sans-serif;
    overflow: hidden;
    display: flex; flex-direction: column;
}}

/* ── Header ── */
.header {{
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0.55rem 1.4rem;
    background: white;
    border-bottom: 1.5px solid #f0f0f5;
    flex-shrink: 0;
}}
.back-btn {{
    display: flex; align-items: center; gap: 6px;
    font-size: 0.68rem; font-weight: 700; color: #555570;
    background: white; border: 1.5px solid #eeeef5;
    border-radius: 30px; padding: 0.3rem 0.9rem;
    cursor: pointer; transition: all 0.15s;
    letter-spacing: 0.5px;
}}
.back-btn:hover {{ border-color: #ff4d8d; color: #ff4d8d; }}
.header-title {{
    font-size: 0.72rem; font-weight: 700;
    color: #2a2a3a; letter-spacing: 0.5px;
    display: flex; align-items: center; gap: 8px;
}}
.header-title .frame-badge {{
    background: #fff0f5; color: #ff4d8d;
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.6rem; font-weight: 700;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
}}
.header-title .mode-badge {{
    background: #f5f5fa; color: #888899;
    border-radius: 20px; padding: 2px 8px;
    font-size: 0.58rem; font-weight: 700;
    font-family: 'Space Mono', monospace;
}}
.header-right {{
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem; font-weight: 700; color: #ff4d8d;
}}

/* ── Slot dots ── */
.slots {{
    display: flex; justify-content: center; gap: 8px;
    padding: 0.55rem 0; background: white;
    border-bottom: 1.5px solid #f0f0f5;
    flex-shrink: 0;
}}
.dot {{
    width: 34px; height: 34px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700;
    border: 2px solid #eeeef5; color: #bbbbcc;
    background: white; transition: all 0.25s;
}}
.dot.done {{
    background: #ff4d8d; border-color: #ff4d8d; color: white;
}}
.dot.active {{
    border-color: #ff4d8d; color: #ff4d8d;
    box-shadow: 0 0 0 4px rgba(255,77,141,0.15);
    animation: pulse-dot 1.2s ease-in-out infinite;
}}
@keyframes pulse-dot {{
    0%,100% {{ box-shadow: 0 0 0 4px rgba(255,77,141,0.15); }}
    50% {{ box-shadow: 0 0 0 8px rgba(255,77,141,0.06); }}
}}

/* ── Body ── */
.body {{
    flex: 1; display: flex; gap: 0.9rem;
    padding: 0.8rem 1.2rem; min-height: 0;
}}

/* ── Camera col ── */
.cam-col {{
    flex: 3; display: flex; flex-direction: column;
    gap: 0.5rem; min-height: 0;
}}
.cam-card {{
    flex: 1; position: relative;
    border-radius: 22px; overflow: hidden;
    background: #eeeef5; min-height: 0;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}}
#video {{
    width: 100%; height: 100%;
    object-fit: cover; display: block;
    transform: {('scaleX(-1)' if mirror else 'none')};
}}
canvas {{ display: none; }}

/* Countdown overlay */
.cd-overlay {{
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(2px);
    z-index: 10; pointer-events: none;
}}
.cd-overlay.hidden {{ display: none; }}
.cd-ring {{
    width: 160px; height: 160px;
    border-radius: 50%;
    background: rgba(255,255,255,0.92);
    box-shadow: 0 8px 40px rgba(255,77,141,0.3), 0 0 0 6px rgba(255,77,141,0.15);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 4px;
}}
.cd-num {{
    font-size: 5rem; font-weight: 900; line-height: 1;
    color: #ff4d8d;
    font-family: 'DM Sans', sans-serif;
    animation: pop 0.3s cubic-bezier(0.175,0.885,0.32,1.275);
}}
@keyframes pop {{
    0% {{ transform: scale(1.4); opacity: 0; }}
    100% {{ transform: scale(1); opacity: 1; }}
}}
.cd-label {{
    font-size: 0.6rem; font-weight: 700;
    color: #9a9aaa; letter-spacing: 3px;
    font-family: 'Space Mono', monospace;
}}

/* Flash */
.flash {{
    position: absolute; inset: 0;
    background: white; opacity: 0;
    pointer-events: none; z-index: 20;
    border-radius: 22px; transition: opacity 0.04s;
}}
.flash.go {{ opacity: 1; }}

/* Status bar bawah kamera */
.status-bar {{
    display: flex; align-items: center;
    justify-content: center; gap: 8px;
    padding: 0.4rem;
    background: white; border-radius: 14px;
    border: 1.5px solid #f0f0f5;
    flex-shrink: 0;
}}
.status-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: #eeeef5; flex-shrink: 0;
    transition: background 0.2s;
}}
.status-dot.active {{ background: #ff4d8d; animation: blink 1s ease-in-out infinite; }}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
.status-txt {{
    font-size: 0.62rem; font-weight: 700;
    color: #9a9aaa; letter-spacing: 2px;
    font-family: 'Space Mono', monospace;
    transition: color 0.2s;
}}
.status-txt.pink {{ color: #ff4d8d; }}

/* ── Strip col ── */
.strip-col {{
    flex: 1; display: flex; flex-direction: column;
    gap: 0.4rem; min-height: 0;
}}
.strip-header {{
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0 0.2rem; flex-shrink: 0;
}}
.strip-title {{
    font-size: 0.58rem; font-weight: 700;
    color: #9a9aaa; letter-spacing: 3px;
    font-family: 'Space Mono', monospace;
}}
.strip-count {{
    font-size: 0.58rem; font-weight: 700;
    color: #ff4d8d; letter-spacing: 1px;
    font-family: 'Space Mono', monospace;
}}
.strip-slots {{
    flex: 1; display: flex; flex-direction: column;
    gap: 0.4rem; overflow: hidden; min-height: 0;
}}
.strip-slot {{
    flex: 1; border-radius: 14px; overflow: hidden;
    background: white;
    border: 1.5px solid #f0f0f5;
    display: flex; align-items: center; justify-content: center;
    position: relative; min-height: 0;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.strip-slot.filled {{
    border-color: #ffcce0;
    box-shadow: 0 2px 12px rgba(255,77,141,0.1);
}}
.strip-slot img {{
    width: 100%; height: 100%; object-fit: cover; display: block;
    {('transform: scaleX(-1);' if mirror else '')}
}}
.empty-icon {{ font-size: 1.2rem; opacity: 0.2; }}
.slot-label {{
    position: absolute; bottom: 5px; right: 7px;
    font-size: 0.45rem; font-weight: 700;
    color: rgba(0,0,0,0.2);
    font-family: 'Space Mono', monospace;
}}
.strip-slot.active-slot {{
    border-color: #ff4d8d;
    box-shadow: 0 0 0 3px rgba(255,77,141,0.12);
}}
</style>
</head>
<body>

<!-- Header -->
<div class="header">
    <button class="back-btn" onclick="goBack()">← BACK</button>
    <div class="header-title">
        <span>{frame_name}</span>
        <span class="frame-badge">{N} FOTO</span>
        <span class="mode-badge">{mode_txt}</span>
    </div>
    <div class="header-right" id="progress-txt">0/{N}</div>
</div>

<!-- Slot dots -->
<div class="slots" id="slots"></div>

<!-- Body -->
<div class="body">
    <!-- Kamera -->
    <div class="cam-col">
        <div class="cam-card">
            <video id="video" autoplay playsinline muted></video>
            <canvas id="canvas"></canvas>
            <div class="cd-overlay hidden" id="overlay">
                <div class="cd-ring">
                    <div class="cd-num" id="cd-num">5</div>
                    <div class="cd-label" id="cd-label">BERSIAP</div>
                </div>
            </div>
            <div class="flash" id="flash"></div>
        </div>
        <div class="status-bar">
            <div class="status-dot" id="status-dot"></div>
            <span class="status-txt" id="status-txt">MEMULAI KAMERA...</span>
        </div>
    </div>

    <!-- Strip preview -->
    <div class="strip-col">
        <div class="strip-header">
            <span class="strip-title">STRIP PREVIEW</span>
            <span class="strip-count" id="strip-count">0/{N}</span>
        </div>
        <div class="strip-slots" id="strip-slots"></div>
    </div>
</div>

<script>
const N = {N};
const MIRROR = {mirror_js};
const DELAY = 5;

let photos = new Array(N).fill(null);
let currentIdx = 0;
let done = false;

const video   = document.getElementById('video');
const canvas  = document.getElementById('canvas');
const overlay = document.getElementById('overlay');
const cdNum   = document.getElementById('cd-num');
const cdLabel = document.getElementById('cd-label');
const flash   = document.getElementById('flash');

function setStatus(txt, active) {{
    document.getElementById('status-txt').textContent = txt;
    document.getElementById('status-txt').className = 'status-txt' + (active ? ' pink' : '');
    document.getElementById('status-dot').className = 'status-dot' + (active ? ' active' : '');
}}

function buildStrip() {{
    const container = document.getElementById('strip-slots');
    container.innerHTML = '';
    for (let i = 0; i < N; i++) {{
        const div = document.createElement('div');
        div.className = 'strip-slot' + (photos[i] ? ' filled' : '') + (i === currentIdx && !photos[i] ? ' active-slot' : '');
        div.id = 'slot-' + i;
        if (photos[i]) {{
            const img = document.createElement('img');
            img.src = photos[i];
            div.appendChild(img);
        }} else {{
            div.innerHTML = '<span class="empty-icon">📷</span>';
        }}
        div.innerHTML += `<span class="slot-label">${{String(i+1).padStart(2,'0')}}</span>`;
        container.appendChild(div);
    }}
    const filled = photos.filter(p=>p).length;
    document.getElementById('strip-count').textContent = filled + '/' + N;
    document.getElementById('progress-txt').textContent = filled + '/' + N;
}}

function updateSlots() {{
    const row = document.getElementById('slots');
    row.innerHTML = '';
    for (let i = 0; i < N; i++) {{
        const d = document.createElement('div');
        d.className = 'dot';
        if (photos[i]) {{ d.classList.add('done'); d.textContent = '✓'; }}
        else if (i === currentIdx) {{ d.classList.add('active'); d.textContent = i+1; }}
        else {{ d.textContent = i+1; }}
        row.appendChild(d);
    }}
}}

async function startCamera() {{
    try {{
        const stream = await navigator.mediaDevices.getUserMedia({{
            video: {{ facingMode: 'user', width:{{ideal:1280}}, height:{{ideal:720}} }},
            audio: false
        }});
        video.srcObject = stream;
        await video.play();
        setStatus('KAMERA SIAP', true);
        setTimeout(startNextShot, 900);
    }} catch(e) {{
        setStatus('IZINKAN AKSES KAMERA ↑', false);
    }}
}}

function startNextShot() {{
    if (done) return;
    currentIdx = photos.findIndex(p => p === null);
    if (currentIdx === -1) {{ allDone(); return; }}
    updateSlots();
    buildStrip();
    setStatus('FOTO ' + (currentIdx+1) + ' DARI ' + N, true);

    let count = DELAY;
    overlay.classList.remove('hidden');

    function tick() {{
        cdNum.style.animation = 'none';
        void cdNum.offsetWidth;
        cdNum.style.animation = 'pop 0.3s cubic-bezier(0.175,0.885,0.32,1.275)';
        if (count > 0) {{
            cdNum.textContent = count;
            cdLabel.textContent = 'FOTO ' + (currentIdx+1) + ' DARI ' + N;
            count--;
            setTimeout(tick, 1000);
        }} else {{
            cdNum.textContent = '📸';
            cdLabel.textContent = '';
            setTimeout(capture, 180);
        }}
    }}
    tick();
}}

function capture() {{
    overlay.classList.add('hidden');
    canvas.width  = video.videoWidth  || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (MIRROR) {{ ctx.translate(canvas.width,0); ctx.scale(-1,1); }}
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    flash.classList.add('go');
    setTimeout(() => flash.classList.remove('go'), 160);

    const full = canvas.toDataURL('image/jpeg', 0.88);
    photos[currentIdx] = full;

    const slot = document.getElementById('slot-' + currentIdx);
    if (slot) {{
        slot.innerHTML = '';
        slot.className = 'strip-slot filled';
        const img = document.createElement('img');
        img.src = full;
        slot.appendChild(img);
        slot.innerHTML += `<span class="slot-label">${{String(currentIdx+1).padStart(2,'0')}}</span>`;
    }}
    updateSlots();

    const filled = photos.filter(p=>p).length;
    document.getElementById('strip-count').textContent = filled + '/' + N;
    document.getElementById('progress-txt').textContent = filled + '/' + N;

    const next = photos.findIndex(p => p === null);
    if (next !== -1) {{
        setStatus('FOTO ' + (currentIdx+2) + ' SIAP...', true);
        setTimeout(startNextShot, 1200);
    }} else {{
        setTimeout(allDone, 800);
    }}
}}

function allDone() {{
    if (done) return;
    done = true;
    setStatus('SEMUA FOTO SELESAI!', true);
    overlay.classList.remove('hidden');
    cdNum.textContent = '✓';
    cdNum.style.color = '#ff4d8d';
    cdLabel.textContent = 'SELESAI!';

    // Kirim ke Python
    const out = photos.map(p => {{
        if (!p) return null;
        const c2 = document.createElement('canvas');
        const img = new Image();
        img.src = p;
        c2.width = 960;
        c2.height = Math.round((img.naturalHeight || 720) * 960 / (img.naturalWidth || 1280));
        const ctx2 = c2.getContext('2d');
        ctx2.drawImage(img, 0, 0, c2.width, c2.height);
        return c2.toDataURL('image/jpeg', 0.82);
    }});

    setTimeout(() => {{
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: JSON.stringify(out)
        }}, '*');
    }}, 700);
}}

function goBack() {{
    window.parent.postMessage({{
        type: 'streamlit:setComponentValue',
        value: JSON.stringify({{action:'back'}})
    }}, '*');
}}

buildStrip();
updateSlots();
startCamera();
</script>
</body>
</html>
""", height=620, scrolling=False)

    # ── Handle response ───────────────────────────────────────────────────────
    if component_result is not None:
        try:
            data = json.loads(component_result)
            if isinstance(data, dict) and data.get("action") == "back":
                st.session_state.shoot_phase = "shooting"
                st.session_state.photos = [None] * N
                st.switch_page("pages/2_frame.py")
            elif isinstance(data, list):
                for i, b64 in enumerate(data):
                    if b64 and i < N:
                        img_bytes = base64.b64decode(b64.split(",")[1])
                        photos[i] = Image.open(BytesIO(img_bytes)).convert("RGB")
                st.session_state.photos = photos
                st.session_state.shoot_phase = "review"
                st.rerun()
        except:
            pass