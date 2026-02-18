"""
Mobile HTML Builder - iPhone向けモバイル版ダッシュボードHTML生成
デスクトップ版に準拠したSF風テーマ・SWITCH切替・ブート画面・マーキー
"""
import base64
import streamlit as st
from pathlib import Path
from ..config import APP_ROOT
from ..components.stock import fetch_stock, build_svg_chart
from ..components.news import fetch_news_for, fetch_kddi_press_releases, fetch_fujitsu_press_releases
from ..components.images import IMG_MAP
from ..components.intelligence import fetch_bu_intelligence, WAKONX_KEYWORDS, BX_KEYWORDS
from ..analysis.insights import run_insight_matcher
from ..analysis.opportunities import generate_opportunities


def _load_image_b64(filename: str) -> str:
    """アプリルートから画像を読み込みBase64データURIを返す"""
    path = APP_ROOT / filename
    try:
        img_data = path.read_bytes()
        return f"data:image/png;base64,{base64.b64encode(img_data).decode()}"
    except Exception:
        return ""


def _build_bu_panel(bu_name: str, intel: dict, color: str) -> str:
    """BU専用インテリジェンスパネル構築（モバイル向け）"""
    score = intel["opportunity_score"]
    score_color = "#00ff88" if score >= 70 else ("#ffaa00" if score >= 40 else "#ff6699")

    news_items = ""
    for i, article in enumerate(intel["articles"][:4], 1):
        news_items += f"""
        <div class="m-news-item">
            <span class="m-news-idx" style="color:{color};">#{i:02d}</span>
            <a href="{article['link']}" target="_blank">{article['title']}</a>
        </div>"""

    match_items = ""
    for match in intel["matches"]:
        source_title = match['title']
        if len(source_title) > 50:
            source_title = source_title[:50] + "..."
        match_items += f"""
        <div class="m-bu-match">
            <span class="m-bu-keyword" style="color:{color};">{match['keyword']}</span>
            <span class="m-bu-priority priority-{match['priority'].lower()}">{match['priority']}</span>
            <div class="m-bu-action">▸ {match['action']}</div>
            <div class="m-bu-source"><a href="{match['link']}" target="_blank">{source_title}</a></div>
        </div>"""

    if not match_items:
        match_items = '<div class="m-empty">キーワードマッチなし</div>'

    return f"""
    <div class="m-bu-panel" style="border-color:{color};">
        <div class="m-bu-header" style="background:linear-gradient(90deg, {color}22 0%, transparent 100%);">
            <span class="m-bu-title" style="color:{color};">{bu_name}</span>
            <span class="m-bu-score" style="color:{score_color};">{score:.0f}<span style="font-size:0.45rem;color:rgba(255,255,255,0.3);">/100</span></span>
        </div>
        <div class="m-bu-body">
            <div class="m-bu-section-title" style="color:{color};">RECENT ACTIVITY</div>
            {news_items}
            <div class="m-bu-section-title" style="color:{color};margin-top:10px;">UVANCE SYNERGY</div>
            {match_items}
        </div>
    </div>"""


def build_mobile_html() -> str:
    """モバイル版ダッシュボードの全HTMLを生成"""

    # ─── 画像読込 ──────────────────────────────────────────
    boot_splash_img = _load_image_b64("opening.png")
    back_logo_img = _load_image_b64("back.png")
    map_img_data = IMG_MAP or ""

    # ─── NEWS データ取得 ───────────────────────────────────
    news_all = fetch_news_for("KDDI+%E5%AF%8C%E5%A3%AB%E9%80%9A+%E9%80%9A%E4%BF%A1", 5)
    news_html = ""
    for i, a in enumerate(news_all, 1):
        news_html += f"""
        <div class="m-news-item">
            <span class="m-news-idx">INTEL-{i:03d}</span>
            <a href="{a['link']}" target="_blank">{a['title']}</a>
            <span class="m-news-date">{a.get('published', '')}</span>
        </div>"""
    if not news_html:
        news_html = '<div class="m-news-item"><span class="m-empty">NO INTEL FEED</span></div>'

    # KDDI Press Releases
    press_releases = fetch_kddi_press_releases(8)
    press_html = ""
    for i, pr in enumerate(press_releases, 1):
        press_html += f"""
        <div class="m-news-item">
            <span class="m-news-idx" style="color:#ff6699;">PR-{i:03d}</span>
            <a href="{pr['link']}" target="_blank">{pr['title']}</a>
            <span class="m-news-date">{pr.get('published', '')}</span>
        </div>"""
    if not press_html:
        press_html = '<div class="m-news-item"><span class="m-empty">NO PRESS RELEASE FEED</span></div>'

    # Fujitsu Press Releases
    fujitsu_releases = fetch_fujitsu_press_releases(8)
    fujitsu_press_html = ""
    for i, pr in enumerate(fujitsu_releases, 1):
        uvance_badge = ' <span class="m-uvance-badge">UVANCE</span>' if pr.get("is_uvance") else ""
        fujitsu_press_html += f"""
        <div class="m-news-item">
            <span class="m-news-idx" style="color:#00aaff;">FJ-{i:03d}</span>
            <a href="{pr['link']}" target="_blank">{pr['title']}</a>{uvance_badge}
            <span class="m-news-date">{pr.get('published', '')}</span>
        </div>"""
    if not fujitsu_press_html:
        fujitsu_press_html = '<div class="m-news-item"><span class="m-empty">NO FUJITSU PRESS FEED</span></div>'

    # ─── WAKONX / BX Intelligence ─────────────────────────
    wakonx_intel = fetch_bu_intelligence("WAKONX", WAKONX_KEYWORDS)
    bx_intel = fetch_bu_intelligence("BX", BX_KEYWORDS)
    wakonx_html = _build_bu_panel("WAKONX INTELLIGENCE", wakonx_intel, "#00ffcc")
    bx_html = _build_bu_panel("KDDI BX INTELLIGENCE", bx_intel, "#ff6699")

    # ─── STOCK データ取得 ──────────────────────────────────
    stocks = [
        ("KDDI", "9433.T", "#00ffcc", "KDDI+%E6%A0%AA%E4%BE%A1"),
        ("FUJITSU", "6702.T", "#00aaff", "%E5%AF%8C%E5%A3%AB%E9%80%9A+%E6%A0%AA%E4%BE%A1"),
        ("SoftBank", "9434.T", "#ffaa00", "%E3%82%BD%E3%83%95%E3%83%88%E3%83%90%E3%83%B3%E3%82%AF+%E6%A0%AA%E4%BE%A1"),
        ("NTT docomo", "9437.T", "#ff6699", "NTT%E3%83%89%E3%82%B3%E3%83%A2+%E6%A0%AA%E4%BE%A1"),
        ("CTC", "4739.T", "#9966ff", "CTC+%E6%A0%AA%E4%BE%A1"),
    ]
    stock_html = ""
    for name, ticker, color, query in stocks:
        price, diff, pct, dates, closes = fetch_stock(ticker, 7)
        # トピック取得（マーキー用）
        topics = fetch_news_for(query, 4)
        topics_html = ""
        for ta in topics:
            topics_html += f'<div class="m-stock-topic"><a href="{ta["link"]}" target="_blank">{ta["title"]}</a></div>'
        if topics_html:
            topics_html = f'<div class="m-stock-topics">{topics_html}</div>'

        if price is not None:
            arrow = "▲" if diff > 0 else ("▼" if diff < 0 else "─")
            cls = "up" if diff > 0 else ("down" if diff < 0 else "neutral")
            # アラート判定
            alert_badge = ""
            if pct is not None and abs(pct) >= 2.0:
                alert_text = "急騰" if pct > 0 else "急落"
                alert_badge = f'<span class="m-stock-alert">{alert_text}</span>'
            chart_svg = build_svg_chart(dates, closes, color, width=300, height=70)
            stock_html += f"""
            <div class="m-stock-card">
                <div class="m-stock-header">
                    <span class="m-stock-name" style="color:{color};">{name}</span>
                    <span class="m-stock-ticker">{ticker} {alert_badge}</span>
                </div>
                <div class="m-stock-price m-{cls}">&yen;{price:,.1f}</div>
                <div class="m-stock-diff m-{cls}">{arrow} {abs(diff):,.1f} ({abs(pct):.2f}%)</div>
                <div class="m-stock-chart">{chart_svg}</div>
                {topics_html}
            </div>"""
        else:
            stock_html += f"""
            <div class="m-stock-card">
                <div class="m-stock-header">
                    <span class="m-stock-name" style="color:{color};">{name}</span>
                    <span class="m-stock-ticker">{ticker}</span>
                </div>
                <div class="m-stock-price" style="color:rgba(0,255,204,0.25);font-size:0.8rem;">AWAITING SIGNAL</div>
                {topics_html}
            </div>"""

    # ─── INSIGHT MATCHER ──────────────────────────────────
    matches, synergy_score = run_insight_matcher()
    if synergy_score >= 70:
        score_color = "#00ff88"
    elif synergy_score >= 40:
        score_color = "#ffaa00"
    else:
        score_color = "#ff3366"

    insight_html = f"""
    <div class="m-synergy">
        <span class="m-synergy-label">SYNERGY SCORE</span>
        <span class="m-synergy-score" style="color:{score_color};">{synergy_score:.1f}</span>
    </div>"""

    for m in matches[:4]:
        has_ai = "confidence" in m
        revenue = m.get("revenue_potential", 0) if has_ai else 0
        reasoning = m.get("reasoning", "")

        insight_html += f"""
        <div class="m-match-card">
            <div class="m-match-kddi">
                <span class="m-match-label">KDDI</span>
                <a href="{m['link']}" target="_blank">{m['kddi']}</a>
            </div>
            <div class="m-match-arrow">MATCH</div>
            <div class="m-match-fujitsu">
                <span class="m-match-label">FUJITSU</span>
                <a href="{m.get('fujitsu_url', '#')}" target="_blank">{m['fujitsu']}</a>
            </div>
            <div class="m-match-action">▶ {m['action']}</div>
            {"<div class='m-match-revenue'>商機 " + str(revenue) + "%</div>" if revenue else ""}
            {"<div class='m-match-reasoning'>" + reasoning[:80] + "</div>" if reasoning else ""}
        </div>"""

    if not matches:
        insight_html += '<div class="m-empty">SCANNING FOR MATCHES...</div>'

    # ─── AI OPPORTUNITIES ─────────────────────────────────
    reports_ready = st.session_state.get("reports_ready", False)

    if reports_ready and "generated_opportunities" in st.session_state:
        opportunities = st.session_state["generated_opportunities"]
    else:
        wakonx_articles = wakonx_intel["articles"][:5]
        bx_articles = bx_intel["articles"][:5]
        kddi_general = fetch_news_for("KDDI", 3)
        kddi_combined = wakonx_articles + bx_articles + kddi_general
        fujitsu_news_raw = fetch_news_for(
            "%E5%AF%8C%E5%A3%AB%E9%80%9A+Uvance+OR+%E5%AF%8C%E5%A3%AB%E9%80%9A+DX+OR+%E5%AF%8C%E5%A3%AB%E9%80%9A+%E5%85%B1%E5%89%B5", 8
        )
        kddi_tuple = tuple(a["title"] for a in kddi_combined)
        fujitsu_tuple = tuple(a["title"] for a in fujitsu_news_raw)
        kddi_press_tuple = tuple(
            f"{pr['title']} — {pr.get('description', '')}" if pr.get("description") else pr["title"]
            for pr in press_releases
        )
        fujitsu_press_tuple = tuple(pr["title"] for pr in fujitsu_releases)
        opportunities = generate_opportunities(kddi_tuple, fujitsu_tuple, kddi_press_tuple, fujitsu_press_tuple)

    opp_html = ""
    if opportunities:
        top_opps = sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)[:3]
        for opp in top_opps:
            score = int(opp.get("score", 0))
            title = opp.get("title", "Unknown")
            uvance = opp.get("uvance_area", "")
            reason = opp.get("score_reason", "")
            if score >= 90:
                s_color = "#00ff88"
            elif score >= 60:
                s_color = "#ffaa00"
            else:
                s_color = "#ff6699"
            opp_html += f"""
            <div class="m-opp-card">
                <div class="m-opp-header">
                    <div class="m-opp-score" style="color:{s_color};">{score}</div>
                    <div class="m-opp-title">{title}</div>
                </div>
                <div class="m-opp-uvance">{uvance}</div>
                <div class="m-opp-reason">{reason}</div>
            </div>"""
    else:
        opp_html = '<div class="m-empty">NO OPPORTUNITIES DETECTED</div>'

    # ─── 全体HTML組み立て ─────────────────────────────────
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
    background: #000;
    color: #00ffcc;
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    -webkit-text-size-adjust: 100%;
    -webkit-font-smoothing: antialiased;
}}

/* ── Background Image ── */
.m-bg-image {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    max-width: 80vw;
    max-height: 80vh;
    opacity: 0.6;
    pointer-events: none;
    z-index: 0;
}}
.m-map-image {{
    position: fixed;
    bottom: 5vh;
    left: 50%;
    transform: translateX(-50%);
    width: 70vw;
    max-width: 400px;
    opacity: 0.15;
    pointer-events: none;
    z-index: 0;
    animation: breathe 10s ease-in-out infinite;
}}
@keyframes breathe {{
    0%, 100% {{ opacity: 0.15; transform: translateX(-50%) scale(1); }}
    50%      {{ opacity: 0.25; transform: translateX(-50%) scale(1.02); }}
}}

/* ── Boot Splash Screen ── */
.boot-splash {{
    position: fixed;
    inset: 0;
    z-index: 99999;
    background: #000;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding-top: 3vh;
    opacity: 1;
    transition: opacity 0.8s ease-out;
    cursor: pointer;
}}
.boot-splash.hide {{
    opacity: 0;
    pointer-events: none;
}}
.boot-splash img {{
    max-width: 95%;
    max-height: 85%;
    object-fit: contain;
    animation: bootFadeIn 0.8s ease-out;
}}
.boot-system {{
    position: fixed;
    top: 5vh;
    left: 4vw;
    z-index: 999999;
    font-family: 'Share Tech Mono', monospace;
    color: rgba(0,255,204,0.9);
}}
.boot-messages {{
    margin-bottom: 12px;
    min-height: 70px;
}}
.boot-message {{
    font-size: 0.6rem;
    line-height: 1.6;
    color: rgba(0,255,204,0.85);
    text-shadow: 0 0 8px rgba(0,255,204,0.3);
    margin-bottom: 3px;
    animation: bootTextAppear 0.3s ease-out;
}}
.boot-message .status-ok {{
    color: rgba(0,255,100,1);
    font-weight: 700;
}}
@keyframes bootTextAppear {{
    from {{ opacity: 0; transform: translateX(-10px); }}
    to {{ opacity: 1; transform: translateX(0); }}
}}
.boot-progress {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.progress-bar-container {{
    width: 200px;
    height: 10px;
    background: rgba(0,20,30,0.8);
    border: 1px solid rgba(0,255,204,0.3);
    border-radius: 2px;
    overflow: hidden;
}}
.progress-bar-fill {{
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg,
        rgba(0,255,204,0.6) 0%,
        rgba(0,255,204,0.9) 50%,
        rgba(0,255,204,0.6) 100%);
    box-shadow: 0 0 10px rgba(0,255,204,0.5);
    transition: width 0.3s ease-out;
}}
.progress-percent {{
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    color: rgba(0,255,204,1);
    text-shadow: 0 0 10px rgba(0,255,204,0.5);
    min-width: 35px;
}}
.boot-hint {{
    position: fixed;
    bottom: 18vh;
    left: 50%;
    transform: translateX(-50%);
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 4px;
    color: rgba(0,255,204,0.9);
    text-shadow: 0 0 15px rgba(0,255,204,0.5);
    animation: pulseHint 2s ease-in-out infinite;
    z-index: 999999;
}}
@keyframes bootFadeIn {{
    from {{ opacity: 0; transform: scale(0.95); }}
    to {{ opacity: 1; transform: scale(1); }}
}}
@keyframes pulseHint {{
    0%, 100% {{ opacity: 0.5; }}
    50% {{ opacity: 1; }}
}}

/* ── Header ── */
.m-header {{
    text-align: center;
    padding: 14px 12px 10px;
    border-bottom: 1px solid rgba(0,255,204,0.15);
    background: linear-gradient(180deg, rgba(0,20,40,0.95) 0%, rgba(0,0,0,0.95) 100%);
    position: sticky;
    top: 0;
    z-index: 100;
}}
.m-header-top {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-bottom: 4px;
}}
.m-header h1 {{
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    letter-spacing: 3px;
    color: rgba(0,255,204,0.9);
    text-shadow: 0 0 12px rgba(0,255,204,0.3);
    font-weight: 700;
}}
.m-header .m-sub {{
    font-size: 0.45rem;
    color: rgba(0,255,204,0.35);
    letter-spacing: 2px;
}}

/* ── SYSTEM ONLINE pulse ── */
.hud-status {{
    display: flex;
    align-items: center;
    gap: 5px;
    font-family: 'Orbitron', monospace;
    font-size: 0.4rem;
    letter-spacing: 2px;
    color: rgba(0,255,204,0.7);
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
}}
.pulse-dot {{
    width: 5px; height: 5px;
    background: #00ffcc;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s ease-in-out infinite;
    box-shadow: 0 0 5px #00ffcc;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.2; }}
}}

/* ── Accordion (details/summary) ── */
details {{
    border-bottom: 1px solid rgba(0,255,204,0.1);
    position: relative;
    z-index: 1;
}}
summary {{
    font-family: 'Orbitron', monospace;
    font-size: 0.6rem;
    letter-spacing: 2px;
    color: rgba(0,255,204,0.85);
    padding: 12px 14px;
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,12,24,0.9);
    border-bottom: 1px solid rgba(0,255,204,0.08);
    text-shadow: 0 0 8px rgba(0,255,204,0.2);
    position: sticky;
    top: 48px;
    z-index: 50;
}}
summary::-webkit-details-marker {{
    color: rgba(0,255,204,0.5);
}}
details[open] > summary {{
    background: rgba(0,255,204,0.05);
    border-bottom: 1px solid rgba(0,255,204,0.2);
}}
.section-body {{
    padding: 10px 12px 16px;
    background: rgba(0,4,10,0.95);
}}

/* ── News SWITCH Section ── */
.m-news-switch-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}}
.m-panel-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    letter-spacing: 2px;
    transition: color 0.3s;
}}
.m-switch-btn {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    letter-spacing: 2px;
    padding: 5px 12px;
    background: rgba(0,255,204,0.08);
    border: 1px solid rgba(0,255,204,0.3);
    border-radius: 3px;
    color: #00ffcc;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
    text-shadow: 0 0 6px rgba(0,255,204,0.3);
    transition: all 0.3s;
}}
.m-switch-btn:active {{
    background: rgba(0,255,204,0.2);
    border-color: rgba(0,255,204,0.6);
    transform: scale(0.95);
}}
.bu-content {{
    display: none;
}}
.bu-content.active {{
    display: block;
}}

/* ── Quick Links ── */
.quick-links {{
    display: flex;
    gap: 6px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}}
.quick-link {{
    font-family: 'Orbitron', monospace;
    font-size: 0.45rem;
    letter-spacing: 1px;
    padding: 4px 10px;
    border: 1px solid rgba(0,255,204,0.35);
    border-radius: 3px;
    color: #00ffcc;
    text-decoration: none;
    -webkit-tap-highlight-color: transparent;
    text-shadow: 0 0 6px rgba(0,255,204,0.2);
}}
.quick-link:active {{
    background: rgba(0,255,204,0.15);
    border-color: rgba(0,255,204,0.7);
}}

/* ── News Items ── */
.m-news-item {{
    padding: 8px 0;
    border-bottom: 1px solid rgba(0,255,204,0.04);
    line-height: 1.5;
}}
.m-news-idx {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    color: rgba(0,255,204,0.45);
    margin-right: 6px;
    letter-spacing: 1px;
}}
.m-news-item a {{
    color: rgba(0,255,204,0.8);
    text-decoration: none;
    font-size: 0.8rem;
    line-height: 1.6;
}}
.m-news-item a:active {{
    color: #00ffee;
}}
.m-news-date {{
    display: block;
    font-size: 0.6rem;
    color: rgba(0,255,204,0.25);
    margin-top: 2px;
}}
.m-uvance-badge {{
    background: #00aaff;
    color: #000;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 0.45rem;
    font-weight: 700;
    margin-left: 4px;
    vertical-align: middle;
}}
.m-empty {{
    text-align: center;
    color: rgba(0,255,204,0.2);
    font-size: 0.7rem;
    padding: 20px 0;
    letter-spacing: 2px;
}}

/* ── BU Intelligence Panel ── */
.m-bu-panel {{
    border: 1px solid rgba(0,255,204,0.15);
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 10px;
}}
.m-bu-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 12px;
}}
.m-bu-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    letter-spacing: 2px;
    font-weight: 700;
}}
.m-bu-score {{
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    font-weight: 900;
}}
.m-bu-body {{
    padding: 8px 12px 12px;
}}
.m-bu-section-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.45rem;
    letter-spacing: 2px;
    margin-bottom: 6px;
}}
.m-bu-match {{
    background: rgba(0,255,204,0.03);
    border: 1px solid rgba(0,255,204,0.06);
    border-radius: 4px;
    padding: 8px;
    margin-bottom: 6px;
}}
.m-bu-keyword {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    font-weight: 700;
    margin-right: 6px;
}}
.m-bu-priority {{
    font-family: 'Orbitron', monospace;
    font-size: 0.4rem;
    padding: 1px 5px;
    border-radius: 2px;
    letter-spacing: 1px;
}}
.priority-high {{ background: rgba(255,51,102,0.2); color: #ff3366; border: 1px solid rgba(255,51,102,0.3); }}
.priority-medium {{ background: rgba(255,170,0,0.15); color: #ffaa00; border: 1px solid rgba(255,170,0,0.3); }}
.priority-low {{ background: rgba(0,255,204,0.1); color: #00ffcc; border: 1px solid rgba(0,255,204,0.2); }}
.m-bu-action {{
    font-size: 0.7rem;
    color: rgba(0,255,204,0.7);
    margin-top: 4px;
}}
.m-bu-source {{
    margin-top: 3px;
}}
.m-bu-source a {{
    font-size: 0.6rem;
    color: rgba(0,255,204,0.4);
    text-decoration: none;
}}

/* ── Stock Cards ── */
.m-stock-card {{
    background: rgba(0,255,204,0.03);
    border: 1px solid rgba(0,255,204,0.08);
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 10px;
}}
.m-stock-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}}
.m-stock-name {{
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
}}
.m-stock-ticker {{
    font-size: 0.55rem;
    color: rgba(0,255,204,0.3);
    display: flex;
    align-items: center;
    gap: 6px;
}}
.m-stock-alert {{
    font-family: 'Orbitron', monospace;
    font-size: 0.45rem;
    font-weight: 700;
    color: #ff3366;
    padding: 1px 6px;
    border: 1px solid rgba(255,51,102,0.5);
    border-radius: 3px;
    background: rgba(255,0,0,0.12);
    animation: alertBlink 1.5s ease-in-out infinite;
}}
@keyframes alertBlink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.3; }}
}}
.m-stock-price {{
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 1px;
}}
.m-stock-diff {{
    font-size: 0.75rem;
    margin-top: 2px;
    margin-bottom: 4px;
}}
.m-up {{ color: #00ff88; }}
.m-down {{ color: #ff3366; }}
.m-neutral {{ color: rgba(0,255,204,0.5); }}
.m-stock-chart {{
    display: flex;
    justify-content: center;
    margin-top: 4px;
}}
.m-stock-chart svg {{
    max-width: 100%;
    height: auto;
}}

/* ── Stock Marquee Topics ── */
.m-stock-topics {{
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1px dashed rgba(0,255,204,0.08);
}}
.m-stock-topic {{
    font-size: 0.6rem;
    line-height: 1.8;
    color: rgba(0,255,204,0.5);
    white-space: nowrap;
    overflow: hidden;
}}
.m-stock-topic a {{
    color: rgba(0,255,204,0.5);
    text-decoration: none;
    display: inline-block;
    animation: marquee 25s linear infinite;
    padding-left: 100%;
}}
.m-stock-topic:nth-child(2) a {{ animation-delay: -3s; }}
.m-stock-topic:nth-child(3) a {{ animation-delay: -6s; }}
.m-stock-topic:nth-child(4) a {{ animation-delay: -9s; }}
.m-stock-topic a:active {{
    color: #00ffcc;
}}
.m-stock-topics.paused .m-stock-topic a {{
    animation-play-state: paused;
}}
@keyframes marquee {{
    0%   {{ transform: translateX(0); }}
    100% {{ transform: translateX(-200%); }}
}}

/* ── Insight Matcher ── */
.m-synergy {{
    text-align: center;
    padding: 12px 0;
    margin-bottom: 10px;
    border-bottom: 1px solid rgba(0,255,204,0.08);
}}
.m-synergy-label {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    letter-spacing: 2px;
    color: rgba(0,255,204,0.4);
    display: block;
    margin-bottom: 4px;
}}
.m-synergy-score {{
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    font-weight: 900;
}}
.m-match-card {{
    background: rgba(0,255,204,0.03);
    border: 1px solid rgba(0,255,204,0.08);
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 10px;
}}
.m-match-label {{
    font-family: 'Orbitron', monospace;
    font-size: 0.45rem;
    letter-spacing: 2px;
    color: rgba(0,255,204,0.4);
    display: block;
    margin-bottom: 2px;
}}
.m-match-kddi a, .m-match-fujitsu a {{
    color: rgba(0,255,204,0.85);
    text-decoration: none;
    font-size: 0.8rem;
    line-height: 1.5;
}}
.m-match-kddi a:active, .m-match-fujitsu a:active {{
    color: #00ffee;
}}
.m-match-arrow {{
    text-align: center;
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    color: rgba(0,255,204,0.5);
    padding: 6px 0;
    letter-spacing: 4px;
}}
.m-match-action {{
    font-size: 0.75rem;
    color: rgba(0,255,204,0.7);
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid rgba(0,255,204,0.06);
}}
.m-match-revenue {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    color: rgba(0,255,204,0.6);
    margin-top: 4px;
}}
.m-match-reasoning {{
    font-size: 0.65rem;
    color: rgba(0,255,204,0.35);
    margin-top: 4px;
    line-height: 1.5;
}}

/* ── Opportunities ── */
.m-opp-card {{
    background: rgba(180,120,255,0.04);
    border: 1px solid rgba(180,120,255,0.12);
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 10px;
}}
.m-opp-header {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
}}
.m-opp-score {{
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem;
    font-weight: 900;
    min-width: 48px;
    text-align: center;
    line-height: 1;
    padding-top: 2px;
}}
.m-opp-title {{
    font-size: 0.8rem;
    color: rgba(180,120,255,0.9);
    line-height: 1.5;
    flex: 1;
}}
.m-opp-uvance {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    color: rgba(180,120,255,0.5);
    letter-spacing: 2px;
    margin-top: 6px;
}}
.m-opp-reason {{
    font-size: 0.7rem;
    color: rgba(180,120,255,0.4);
    margin-top: 6px;
    line-height: 1.5;
}}

/* ── Footer ── */
.m-footer {{
    text-align: center;
    padding: 20px 12px;
    font-family: 'Orbitron', monospace;
    font-size: 0.4rem;
    color: rgba(0,255,204,0.15);
    letter-spacing: 3px;
    border-top: 1px solid rgba(0,255,204,0.05);
}}

/* ── Scanlines overlay ── */
.m-scanlines {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 9998;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px
    );
}}
</style>
</head>
<body>

<!-- ── Boot Splash Screen ── -->
<div class="boot-splash" id="bootSplash">
    {"<img src='" + boot_splash_img + "' alt='Loading...'>" if boot_splash_img else ""}
    <div class="boot-system">
        <div class="boot-messages" id="bootMessages"></div>
        <div class="boot-progress">
            <div class="progress-bar-container">
                <div class="progress-bar-fill" id="progressBarFill"></div>
            </div>
            <div class="progress-percent" id="progressPercent">0%</div>
        </div>
    </div>
    <div class="boot-hint" id="bootHint" style="display:none;">TAP TO START</div>
</div>

<!-- ── Background Images ── -->
{"<img src='" + back_logo_img + "' class='m-bg-image' alt=''>" if back_logo_img else ""}
{"<img src='" + map_img_data + "' class='m-map-image' alt=''>" if map_img_data else ""}

<div class="m-scanlines"></div>

<!-- ── Header ── -->
<div class="m-header">
    <div class="hud-status" onclick="returnToBootScreen()">
        <span class="pulse-dot"></span>SYSTEM ONLINE
    </div>
    <div class="m-header-top">
        <h1>STRATEGIC DASHBOARD</h1>
    </div>
    <div class="m-sub">FUJITSU // KDDI ACCOUNT INTELLIGENCE</div>
</div>

<!-- ── NEWS & PRESS (SWITCH切替) ── -->
<details open>
    <summary>NEWS &amp; INTELLIGENCE</summary>
    <div class="section-body">
        <div class="m-news-switch-header">
            <div class="m-panel-title" id="buPanelTitle" style="color:#ffaa00;">TRENDING TOPICS</div>
            <button class="m-switch-btn" onclick="toggleBU()">⇄ SWITCH</button>
        </div>

        <!-- Panel 1: Trending Topics -->
        <div id="newsPanel" class="bu-content active">
            <div class="quick-links">
                <a href="https://www.nikkei.com/" target="_blank" class="quick-link">NIKKEI</a>
                <a href="https://newspicks.com/search/?q=KDDI&t=top" target="_blank" class="quick-link">NEWSPICKS</a>
            </div>
            {news_html}
        </div>

        <!-- Panel 2: KDDI Press -->
        <div id="pressPanel" class="bu-content">
            <div class="quick-links">
                <a href="https://newsroom.kddi.com/" target="_blank" class="quick-link">KDDI NEWSROOM</a>
            </div>
            {press_html}
        </div>

        <!-- Panel 3: Fujitsu Press -->
        <div id="fujitsuPressPanel" class="bu-content">
            <div class="quick-links">
                <a href="https://global.fujitsu/ja-jp/pr" target="_blank" class="quick-link">FUJITSU PR</a>
                <a href="https://global.fujitsu/ja-jp/uvance" target="_blank" class="quick-link">UVANCE</a>
            </div>
            {fujitsu_press_html}
        </div>

        <!-- Panel 4: WAKONX -->
        <div id="wakonxPanel" class="bu-content">
            {wakonx_html}
        </div>

        <!-- Panel 5: KDDI BX -->
        <div id="bxPanel" class="bu-content">
            {bx_html}
        </div>
    </div>
</details>

<!-- ── STOCK MONITOR ── -->
<details>
    <summary>STOCK MONITOR</summary>
    <div class="section-body">
        {stock_html}
    </div>
</details>

<!-- ── INSIGHT MATCHER ── -->
<details>
    <summary>INSIGHT MATCHER</summary>
    <div class="section-body">
        {insight_html}
    </div>
</details>

<!-- ── AI OPPORTUNITIES ── -->
<details>
    <summary>AI STRATEGIC OPPORTUNITIES</summary>
    <div class="section-body">
        {opp_html}
    </div>
</details>

<div class="m-footer">
    FUJITSU // ACCOUNT INTELLIGENCE DIVISION // MOBILE
</div>

<script>
// ── News SWITCH toggle ──
function toggleBU(){{
    var wakonx = document.getElementById('wakonxPanel');
    var bx = document.getElementById('bxPanel');
    var news = document.getElementById('newsPanel');
    var press = document.getElementById('pressPanel');
    var fjPress = document.getElementById('fujitsuPressPanel');
    var title = document.getElementById('buPanelTitle');

    if(news.classList.contains('active')){{
        news.classList.remove('active');
        press.classList.add('active');
        title.textContent = 'KDDI PRESS RELEASE';
        title.style.color = '#00aaff';
    }} else if(press.classList.contains('active')){{
        press.classList.remove('active');
        fjPress.classList.add('active');
        title.textContent = 'FUJITSU PRESS RELEASE';
        title.style.color = '#00aaff';
    }} else if(fjPress.classList.contains('active')){{
        fjPress.classList.remove('active');
        wakonx.classList.add('active');
        title.textContent = 'WAKONX INTELLIGENCE';
        title.style.color = '#00ffcc';
    }} else if(wakonx.classList.contains('active')){{
        wakonx.classList.remove('active');
        bx.classList.add('active');
        title.textContent = 'KDDI BX INTELLIGENCE';
        title.style.color = '#ff6699';
    }} else {{
        bx.classList.remove('active');
        news.classList.add('active');
        title.textContent = 'TRENDING TOPICS';
        title.style.color = '#ffaa00';
    }}
}}

// ── Stock marquee tap-to-pause ──
document.querySelectorAll('.m-stock-topics').forEach(function(el){{
    el.addEventListener('click', function(){{
        el.classList.toggle('paused');
    }});
}});

// ── Boot Splash Screen ──
(function() {{
    var splash = document.getElementById('bootSplash');
    if (!splash) return;

    // セッションストレージで1セッションに1回のみ表示
    var hasShown = sessionStorage.getItem('boot_splash_shown');
    if (hasShown) {{
        splash.remove();
        return;
    }}

    function hideSplash() {{
        splash.classList.add('hide');
        setTimeout(function() {{
            splash.remove();
        }}, 800);
        sessionStorage.setItem('boot_splash_shown', 'true');
    }}

    // ブートメッセージ順次表示
    var bootMessages = [
        {{ text: '> INITIALIZING ACCOUNT INTELLIGENCE...', delay: 0 }},
        {{ text: '> LOADING AI MODULES.............. <span class="status-ok">[OK]</span>', delay: 600 }},
        {{ text: '> CONNECTING TO DATA SOURCES...... <span class="status-ok">[OK]</span>', delay: 1200 }},
        {{ text: '> ESTABLISHING SECURE CONNECTION.. <span class="status-ok">[OK]</span>', delay: 1800 }},
        {{ text: '> SYSTEM READY', delay: 2400 }}
    ];

    var messagesContainer = document.getElementById('bootMessages');
    var progressFill = document.getElementById('progressBarFill');
    var progressPercent = document.getElementById('progressPercent');
    var bootHint = document.getElementById('bootHint');

    bootMessages.forEach(function(msg) {{
        setTimeout(function() {{
            var msgDiv = document.createElement('div');
            msgDiv.className = 'boot-message';
            msgDiv.innerHTML = msg.text;
            messagesContainer.appendChild(msgDiv);
        }}, msg.delay);
    }});

    // プログレスバー（80msごとに3%進行）
    var progress = 0;
    var progressInterval = setInterval(function() {{
        progress += 3;
        if (progress > 100) {{
            progress = 100;
            clearInterval(progressInterval);
            setTimeout(function() {{
                bootHint.style.display = 'block';
            }}, 300);
        }}
        progressFill.style.width = progress + '%';
        progressPercent.textContent = progress + '%';
    }}, 80);

    // タップで非表示
    splash.addEventListener('click', function() {{
        hideSplash();
    }});
}})();

// ── SYSTEM ONLINE → ブート画面に戻る ──
function returnToBootScreen() {{
    sessionStorage.removeItem('boot_splash_shown');
    location.reload();
}}
</script>
</body></html>"""
