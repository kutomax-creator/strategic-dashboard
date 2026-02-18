"""
Strategic Dashboard
===========================
SF映画風の戦略コックピット・ダッシュボード
富士通アカウントセールスマネージャー向け KDDI動向監視
"""

import streamlit as st
import streamlit.components.v1 as components
import time

# Configuration
from dashboard_modules.config import PAGE_CONFIG

# Components
from dashboard_modules.components.news import fetch_news_for, fetch_kddi_press_releases, fetch_fujitsu_press_releases
from dashboard_modules.components.chat import get_chat_response
from dashboard_modules.components.context import (
    get_context_files, add_context_file, toggle_context_file,
    delete_context_file, get_active_context_data
)

# Analysis
from dashboard_modules.analysis.opportunities import generate_opportunities, generate_detail_report

# UI
from dashboard_modules.ui.html_builder import build_dashboard_html

# ─── Page Config ─────────────────────────────────────────────────────
st.set_page_config(**PAGE_CONFIG)


# ─── Password Gate ───────────────────────────────────────────────────
def check_password() -> bool:
    """パスワード認証。st.secrets に password が設定されていなければスキップ。"""
    try:
        correct_pw = st.secrets["password"]
    except (KeyError, FileNotFoundError):
        return True  # secrets未設定ならスキップ（ローカル開発用）

    if st.session_state.get("authenticated"):
        return True

    st.markdown("""<style>
        html, body, [data-testid="stApp"] { background: #000 !important; }
        .login-box { max-width: 400px; margin: 15vh auto; text-align: center; }
        .login-box h2 { color: rgba(0,255,204,0.9); font-family: monospace; letter-spacing: 4px; }
        .login-box p { color: rgba(0,255,204,0.5); font-size: 0.8rem; }
    </style>""", unsafe_allow_html=True)
    st.markdown('<div class="login-box"><h2>STRATEGIC DASHBOARD</h2><p>Enter access code</p></div>', unsafe_allow_html=True)

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
        iframe { border: none !important; }
    </style>""", unsafe_allow_html=True)

    reports_ready = st.session_state.get("reports_ready", False)

    html = build_dashboard_html()
    components.html(html, height=860 if not reports_ready else 900, scrolling=False)

    # チャット状態初期化（常に実行）
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    # ボタンエリアのスタイル（常に適用）
    st.markdown("""<style>
            /* Remove all default padding/margin */
            .main .block-container {
                padding-left: 0 !important;
                padding-right: 0 !important;
            }
            div[data-testid="stHorizontalBlock"] {
                gap: 0 !important;
            }
            /* Button row container */
            div[data-testid="column"] {
                display: flex !important;
                align-items: center !important;
                padding: 0 !important;
            }
            div[data-testid="column"]:first-child {
                justify-content: center !important;
                padding-left: 1rem !important;
            }
            div[data-testid="column"]:last-child {
                justify-content: flex-end !important;
                padding-right: 1rem !important;
            }
            div[data-testid="column"]:last-child div.stButton {
                margin-right: 0 !important;
                margin-left: auto !important;
            }
            div.stButton {
                margin: 10px 0 !important;
                width: auto !important;
            }
            div.stButton > button {
                background: rgba(0,255,204,0.08) !important;
                border: 1px solid rgba(0,255,204,0.3) !important;
                color: rgba(0,255,204,0.9) !important;
                font-family: 'Orbitron', monospace !important;
                font-size: 0.55rem !important;
                letter-spacing: 3px !important;
                padding: 6px 24px !important;
                width: auto !important;
                min-width: unset !important;
                text-shadow: 0 0 8px rgba(0,255,204,0.3) !important;
            }
            div.stButton > button:hover {
                background: rgba(0,255,204,0.15) !important;
                border-color: rgba(0,255,204,0.6) !important;
                color: rgba(0,255,230,1) !important;
                text-shadow: 0 0 12px rgba(0,255,204,0.5) !important;
            }
            div.stProgress > div > div { background-color: rgba(0,255,204,0.6) !important; }
            div.stProgress { margin: 10px auto !important; max-width: 400px; }
    </style>""", unsafe_allow_html=True)

    # ボタン配置
    if not reports_ready:
        # レポート未生成時：両方のボタン表示
        col1, col2 = st.columns([1, 1])
        with col1:
            generate_button = st.button("▶ GENERATE REPORTS")
        with col2:
            if st.button("▶ STRATEGY CHAT", key="open_chat_dialog"):
                st.session_state.show_chat_dialog = True

        if generate_button:
            # キャッシュクリア（前回のエラー結果が残っている場合に対応）
            generate_detail_report.clear()
            progress_bar = st.progress(0, text="Preparing...")
            # html_builderと同じニュースソースを使用（WAKONX/BX特化 + 一般KDDI）
            from dashboard_modules.components.intelligence import fetch_bu_intelligence, WAKONX_KEYWORDS, BX_KEYWORDS
            wakonx_intel = fetch_bu_intelligence("WAKONX", WAKONX_KEYWORDS)
            bx_intel = fetch_bu_intelligence("BX", BX_KEYWORDS)
            wakonx_articles = wakonx_intel["articles"][:5]
            bx_articles = bx_intel["articles"][:5]
            kddi_general = fetch_news_for("KDDI", 3)
            kddi_combined = wakonx_articles + bx_articles + kddi_general
            fujitsu_news_raw = fetch_news_for("%E5%AF%8C%E5%A3%AB%E9%80%9A+Uvance+OR+%E5%AF%8C%E5%A3%AB%E9%80%9A+DX+OR+%E5%AF%8C%E5%A3%AB%E9%80%9A+%E5%85%B1%E5%89%B5", 8)
            kddi_tuple = tuple(a["title"] for a in kddi_combined)
            fujitsu_tuple = tuple(a["title"] for a in fujitsu_news_raw)
            # プレスリリース取得
            kddi_press_raw = fetch_kddi_press_releases(8)
            fujitsu_press_raw = fetch_fujitsu_press_releases(8)
            kddi_press_tuple = tuple(
                f"{pr['title']} — {pr.get('description', '')}" if pr.get("description") else pr["title"]
                for pr in kddi_press_raw
            )
            fujitsu_press_tuple = tuple(pr["title"] for pr in fujitsu_press_raw)
            progress_bar.progress(10, text="Analyzing opportunities...")
            opportunities = generate_opportunities(kddi_tuple, fujitsu_tuple, kddi_press_tuple, fujitsu_press_tuple)
            # スコア順にソートして上位3件のみレポート生成
            top_opportunities = sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)[:3] if opportunities else []
            report_data_cache = {}
            total = len(top_opportunities) if top_opportunities else 1
            for idx, opp in enumerate(top_opportunities):
                t = opp.get("title", "Unknown")
                pct = 15 + int((idx / total) * 80)
                progress_bar.progress(pct, text=f"Generating report {idx+1}/{total}...")
                print(f"[GEN] Generating report for: {t[:50]}")
                fname, sec_html, rep_title = generate_detail_report(t, kddi_tuple, fujitsu_tuple, kddi_press_tuple, fujitsu_press_tuple)
                print(f"[GEN] Result: fname={fname}, html_len={len(sec_html)}, title={rep_title[:30] if rep_title else 'EMPTY'}")
                report_data_cache[t] = {"filename": fname, "sections_html": sec_html, "title": rep_title}
            progress_bar.progress(100, text="Complete!")
            st.session_state["report_data_cache"] = report_data_cache
            st.session_state["generated_opportunities"] = opportunities
            st.session_state["reports_ready"] = True
            time.sleep(0.5)
            st.rerun()
    else:
        # レポート生成後：チャットボタンのみ表示
        if st.button("▶ STRATEGY CHAT", key="open_chat_dialog_after"):
            st.session_state.show_chat_dialog = True

    # ─── Strategy Chat Dialog ────────────────────────────────────
    if "show_chat_dialog" not in st.session_state:
        st.session_state.show_chat_dialog = False

    @st.dialog("💬 STRATEGY CHAT // AI STRATEGIST", width="large")
    def show_chat():
        # メッセージ履歴表示
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 入力エリア
        if prompt := st.chat_input("KDDIアカウント戦略について質問・議論..."):
            # ユーザーメッセージを追加
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # AIレスポンス生成
            with st.chat_message("assistant"):
                with st.spinner("AI Strategist is thinking..."):
                    response = get_chat_response(prompt, st.session_state.chat_messages[:-1])
                st.markdown(response)

            # AIメッセージを履歴に追加
            st.session_state.chat_messages.append({"role": "assistant", "content": response})

        # クリアボタン
        if st.session_state.chat_messages:
            if st.button("🗑 Clear Chat History"):
                st.session_state.chat_messages = []
                st.rerun()

    if st.session_state.show_chat_dialog:
        show_chat()
        st.session_state.show_chat_dialog = False

    # ─── Context Library UI ──────────────────────────────────────
    if True:
        st.markdown("""<style>
        /* Context Library Container */
        .context-library {
            background: rgba(0,8,18,0.95);
            border: 1px solid rgba(0,255,204,0.15);
            border-radius: 4px;
            padding: 16px 20px;
            margin: 10px auto;
            max-width: 900px;
        }
        .context-title {
            font-family: 'Orbitron', monospace;
            font-size: 0.55rem;
            letter-spacing: 3px;
            color: rgba(0,255,204,0.9);
            margin-bottom: 12px;
            text-align: center;
            text-shadow: 0 0 8px rgba(0,255,204,0.3);
        }
        /* Minimal File Uploader Styling */
        .context-library section[data-testid="stFileUploader"] {
            max-width: 600px !important;
            margin: 0 auto 12px auto !important;
        }
        .context-library section[data-testid="stFileUploader"] button {
            background: rgba(0,255,204,0.08) !important;
            border: 1px solid rgba(0,255,204,0.3) !important;
            color: rgba(0,255,204,0.8) !important;
            font-family: monospace !important;
            font-size: 0.65rem !important;
            padding: 6px 16px !important;
        }
        .context-library section[data-testid="stFileUploader"] button:hover {
            background: rgba(0,255,204,0.15) !important;
            border-color: rgba(0,255,204,0.5) !important;
        }
        .context-library section[data-testid="stFileUploader"] small {
            color: rgba(0,255,204,0.4) !important;
            font-size: 0.55rem !important;
        }
        /* Success Messages */
        .context-library .stSuccess {
            background: rgba(0,255,204,0.05) !important;
            border: 1px solid rgba(0,255,204,0.2) !important;
            color: rgba(0,255,204,0.8) !important;
            font-size: 0.65rem !important;
        }
        /* Hide Info Messages in Context Library */
        .context-library .stInfo {
            display: none !important;
        }
        /* Text Display - Context Library specific */
        .context-library .stMarkdown, .context-library .stText {
            color: rgba(0,255,204,0.7) !important;
            font-size: 0.65rem !important;
        }
        /* Columns - Context Library specific */
        .context-library div[data-testid="column"] {
            color: rgba(0,255,204,0.7) !important;
            font-size: 0.6rem !important;
        }
        /* Checkbox - Context Library specific */
        .context-library .stCheckbox label {
            color: rgba(0,255,204,0.7) !important;
            font-size: 0.6rem !important;
        }
        /* Button - Context Library specific */
        .context-library .stButton button {
            background: rgba(0,255,204,0.08) !important;
            border: 1px solid rgba(0,255,204,0.25) !important;
            color: rgba(0,255,204,0.8) !important;
            font-size: 0.6rem !important;
            padding: 2px 8px !important;
        }
        .context-library .stButton button:hover {
            background: rgba(0,255,204,0.15) !important;
            border-color: rgba(0,255,204,0.5) !important;
        }
        /* Text Area - Context Library specific */
        .context-library .stTextArea label {
            color: rgba(0,255,204,0.7) !important;
            font-size: 0.65rem !important;
        }
        .context-library .stTextArea textarea {
            background: rgba(0,12,24,0.9) !important;
            color: rgba(0,255,204,0.7) !important;
            border: 1px solid rgba(0,255,204,0.2) !important;
            font-family: monospace !important;
            font-size: 0.6rem !important;
        }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="context-library">', unsafe_allow_html=True)

    # ファイルアップロード
    uploaded_file = st.file_uploader(
        "📎 Upload Excel / Text / CSV / MD / PDF",
        type=["xlsx", "xls", "txt", "md", "csv", "pdf"],
        key="context_file_uploader"
    )

    if uploaded_file is not None:
        # 既に追加済みかチェック（無限ループ防止）
        if uploaded_file.name not in get_context_files():
            file_ext = uploaded_file.name.split(".")[-1].lower()
            add_context_file(uploaded_file.name, uploaded_file.read(), file_ext)
            st.success(f"✅ {uploaded_file.name} をアップロードしました")
            st.rerun()

    # アップロード済みファイル一覧
    context_files = get_context_files()
    if context_files:
        st.markdown("**📄 Uploaded Files:**")
        for filename, info in context_files.items():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.text(f"{filename} ({info['type'].upper()})")
            with col2:
                st.text(f"📅 {info['uploaded_at']}")
            with col3:
                is_active = st.checkbox("Active", value=info["active"], key=f"toggle_{filename}")
                if is_active != info["active"]:
                    toggle_context_file(filename)
                    st.rerun()
            with col4:
                if st.button("🗑", key=f"delete_{filename}"):
                    delete_context_file(filename)
                    st.rerun()

        # プレビュー
        if st.checkbox("📊 Preview Context Data", value=False):
            context_data = get_active_context_data()
            if context_data:
                st.text_area("Active Context Data (sent to AI)", context_data, height=300)
            else:
                st.info("アクティブなファイルがありません")
    else:
        st.info("ファイルをアップロードしてください")

    st.markdown('</div>', unsafe_allow_html=True)


# ─── Main ────────────────────────────────────────────────────────
def main():
    if not check_password():
        return
    render()


if __name__ == "__main__":
    main()
