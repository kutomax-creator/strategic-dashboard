"""
Strategic Dashboard — Mobile Version
=====================================
iPhone向けモバイル版ダッシュボード
縦1カラム・アコーディオン形式
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from pathlib import Path

# Configuration
from dashboard_modules.config import PAGE_CONFIG

# UI
from dashboard_modules.ui.html_mobile import build_mobile_html

# ─── Report Persistence ──────────────────────────────────────────────
_REPORT_CACHE_FILE = Path(__file__).resolve().parent / "static" / "_report_cache.json"


def _load_reports():
    """保存済みレポートを復元"""
    try:
        if _REPORT_CACHE_FILE.exists():
            data = json.loads(_REPORT_CACHE_FILE.read_text(encoding="utf-8"))
            return data.get("report_data_cache", {}), data.get("generated_opportunities", [])
    except Exception:
        pass
    return None, None


# リロード時にsession_stateが空なら保存済みを復元
if "reports_ready" not in st.session_state:
    cached_reports, cached_opps = _load_reports()
    if cached_reports:
        st.session_state["report_data_cache"] = cached_reports
        st.session_state["generated_opportunities"] = cached_opps
        st.session_state["reports_ready"] = True

# ─── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Strategic Dashboard Mobile",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ─── Password Gate ───────────────────────────────────────────────────
def check_password() -> bool:
    """パスワード認証。st.secrets に password が設定されていなければスキップ。"""
    try:
        correct_pw = st.secrets["password"]
    except (KeyError, FileNotFoundError):
        return True

    if st.session_state.get("authenticated"):
        return True

    st.markdown("""<style>
        html, body, [data-testid="stApp"] { background: #000 !important; }
        .login-box { max-width: 320px; margin: 20vh auto; text-align: center; padding: 0 16px; }
        .login-box h2 { color: rgba(0,255,204,0.9); font-family: monospace; letter-spacing: 4px; font-size: 1rem; }
        .login-box p { color: rgba(0,255,204,0.5); font-size: 0.7rem; }
    </style>""", unsafe_allow_html=True)
    st.markdown(
        '<div class="login-box"><h2>STRATEGIC DASHBOARD</h2><p>Enter access code</p></div>',
        unsafe_allow_html=True,
    )

    pw = st.text_input("Password", type="password", label_visibility="collapsed")
    if pw:
        if pw == correct_pw:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Access denied")
    return False


# ─── Render ──────────────────────────────────────────────────────────
def render():
    # Hide Streamlit UI chrome
    st.markdown("""<style>
        header[data-testid="stHeader"], footer, #MainMenu,
        [data-testid="stToolbar"], [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] { display: none !important; }
        [data-testid="stApp"] > div:first-child { padding: 0 !important; }
        section[data-testid="stMain"] > div { padding: 0 !important; max-width: 100% !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        html, body, [data-testid="stApp"] { background: #000 !important; }
        iframe { border: none !important; width: 100% !important; }
    </style>""", unsafe_allow_html=True)

    html = build_mobile_html()
    components.html(html, height=2400, scrolling=True)


# ─── Main ────────────────────────────────────────────────────────────
def main():
    if not check_password():
        return
    render()


if __name__ == "__main__":
    main()
