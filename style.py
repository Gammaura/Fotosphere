"""
style.py — Shared styles untuk semua halaman PhotoBooth
Pastel soft aesthetic: pink, lavender, cream
"""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

:root {
    --bg:       #fdf6fb;
    --bg2:      #f7eef5;
    --card:     #ffffff;
    --pink:     #f06292;
    --pink-l:   #f8bbd0;
    --pink-d:   #e91e8c;
    --lavender: #9c7bb5;
    --lav-l:    #e8def8;
    --lav-d:    #7b5ea7;
    --cream:    #fff8e1;
    --gold:     #f9a825;
    --green:    #66bb6a;
    --text:     #3d2c3e;
    --muted:    #a68ab0;
    --border:   #ebd5f0;
    --white:    #ffffff;
    --shadow:   0 4px 20px rgba(240,98,146,0.12);
    --shadow-l: 0 2px 10px rgba(156,123,181,0.10);
}

*, html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Nunito', sans-serif !important;
}

.stApp {
    background: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 80% 40% at 0% 0%, #f8bbd040, transparent),
        radial-gradient(ellipse 60% 40% at 100% 100%, #e8def840, transparent) !important;
    min-height: 100vh;
}

#MainMenu, footer, header, .stDeployButton,
section[data-testid="stSidebar"] { display: none !important; }

.block-container {
    padding: 2rem 1.5rem !important;
    max-width: 900px !important;
    margin: 0 auto !important;
}

/* ── Card ── */
.card {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: var(--shadow-l);
    margin-bottom: 1rem;
}

/* ── Page title ── */
.page-title {
    text-align: center;
    margin-bottom: 1.5rem;
}
.page-title .emoji { font-size: 2.5rem; display: block; margin-bottom: 0.3rem; }
.page-title h1 {
    font-size: 2rem !important;
    font-weight: 900 !important;
    color: var(--pink-d) !important;
    margin: 0 !important;
    letter-spacing: 1px;
}
.page-title p {
    color: var(--muted) !important;
    font-size: 0.85rem !important;
    margin: 0.3rem 0 0 !important;
}

/* ── Step badge ── */
.step-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 1.5rem;
}
.step-dot {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 800;
    background: var(--border);
    color: var(--muted);
}
.step-dot.active {
    background: var(--pink);
    color: white;
    box-shadow: 0 0 0 4px var(--pink-l);
}
.step-dot.done {
    background: var(--green);
    color: white;
}

/* ── Section label ── */
.sec-label {
    font-size: 0.75rem;
    font-weight: 800;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    display: block;
}

/* ── Primary button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--pink) 0%, var(--pink-d) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.5px !important;
    padding: 0.75rem 1.5rem !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(240,98,146,0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(240,98,146,0.5) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* ── Secondary button ── */
.btn-sec > button {
    background: white !important;
    color: var(--pink) !important;
    border: 2px solid var(--pink-l) !important;
    box-shadow: none !important;
}
.btn-sec > button:hover {
    background: var(--bg2) !important;
    border-color: var(--pink) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Ghost button ── */
.btn-ghost > button {
    background: transparent !important;
    color: var(--muted) !important;
    border: 1.5px solid var(--border) !important;
    box-shadow: none !important;
    font-size: 0.85rem !important;
    padding: 0.5rem !important;
}
.btn-ghost > button:hover {
    border-color: var(--pink-l) !important;
    color: var(--pink) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Lavender button ── */
.btn-lav > button {
    background: linear-gradient(135deg, var(--lavender), var(--lav-d)) !important;
    box-shadow: 0 4px 15px rgba(156,123,181,0.35) !important;
}
.btn-lav > button:hover {
    box-shadow: 0 8px 25px rgba(156,123,181,0.5) !important;
}

/* ── Active select button ── */
.btn-selected > button {
    background: var(--lav-l) !important;
    color: var(--lav-d) !important;
    border: 2px solid var(--lavender) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Divider ── */
.divider { border: none; border-top: 1.5px solid var(--border); margin: 1.5rem 0; }

/* ── Info row ── */
.info-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
}
.info-row:last-child { border-bottom: none; }
.info-key { font-size: 0.75rem; color: var(--muted); font-weight: 600; }
.info-val { font-size: 0.85rem; font-weight: 800; color: var(--text); }

/* Streamlit camera & image styling */
div[data-testid="stCameraInput"] > div {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 2px solid var(--border) !important;
}
div[data-testid="stImage"] img { border-radius: 12px !important; }
div[data-testid="stSelectbox"] > div > div {
    background: white !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
}
</style>
"""


def step_indicator(current: int):
    """Render step indicator. current = 1-based step number."""
    labels = ["💳", "🎨", "📸", "✨", "⬇️"]
    dots = ""
    for i, label in enumerate(labels):
        n = i + 1
        cls = "active" if n == current else ("done" if n < current else "")
        dots += f'<div class="step-dot {cls}">{label if n >= current else "✓"}</div>'
    return f'<div class="step-row">{dots}</div>'