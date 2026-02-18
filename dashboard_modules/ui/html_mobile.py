"""
Mobile HTML Builder - iPhone向けモバイル版ダッシュボードHTML生成
縦1カラム、アコーディオン形式、SF風テーマ維持
"""
import streamlit as st
from ..components.stock import fetch_stock, build_svg_chart
from ..components.news import fetch_news_for, fetch_kddi_press_releases, fetch_fujitsu_press_releases
from ..analysis.insights import run_insight_matcher
from ..analysis.opportunities import generate_opportunities


def build_mobile_html() -> str:
    """モバイル版ダッシュボードの全HTMLを生成"""

    # ─── NEWS データ取得 ───────────────────────────────────────
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

    # ─── STOCK データ取得 ──────────────────────────────────────
    stocks = [
        ("KDDI", "9433.T", "#00ffcc"),
        ("FUJITSU", "6702.T", "#00aaff"),
        ("SoftBank", "9434.T", "#ffaa00"),
        ("NTT docomo", "9437.T", "#ff6699"),
        ("CTC", "4739.T", "#9966ff"),
    ]
    stock_html = ""
    for name, ticker, color in stocks:
        price, diff, pct, dates, closes = fetch_stock(ticker, 7)
        if price is not None:
            arrow = "▲" if diff > 0 else ("▼" if diff < 0 else "─")
            cls = "up" if diff > 0 else ("down" if diff < 0 else "neutral")
            chart_svg = build_svg_chart(dates, closes, color, width=300, height=70)
            stock_html += f"""
            <div class="m-stock-card">
                <div class="m-stock-header">
                    <span class="m-stock-name" style="color:{color};">{name}</span>
                    <span class="m-stock-ticker">{ticker}</span>
                </div>
                <div class="m-stock-price m-{cls}">&yen;{price:,.1f}</div>
                <div class="m-stock-diff m-{cls}">{arrow} {abs(diff):,.1f} ({abs(pct):.2f}%)</div>
                <div class="m-stock-chart">{chart_svg}</div>
            </div>"""
        else:
            stock_html += f"""
            <div class="m-stock-card">
                <div class="m-stock-header">
                    <span class="m-stock-name" style="color:{color};">{name}</span>
                    <span class="m-stock-ticker">{ticker}</span>
                </div>
                <div class="m-stock-price" style="color:rgba(0,255,204,0.25);font-size:0.8rem;">AWAITING SIGNAL</div>
            </div>"""

    # ─── INSIGHT MATCHER ──────────────────────────────────────
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

    # ─── AI OPPORTUNITIES ─────────────────────────────────────
    reports_ready = st.session_state.get("reports_ready", False)

    if reports_ready and "generated_opportunities" in st.session_state:
        opportunities = st.session_state["generated_opportunities"]
    else:
        # ニュースデータを収集してオポチュニティ生成
        from ..components.intelligence import fetch_bu_intelligence, WAKONX_KEYWORDS, BX_KEYWORDS
        wakonx_intel = fetch_bu_intelligence("WAKONX", WAKONX_KEYWORDS)
        bx_intel = fetch_bu_intelligence("BX", BX_KEYWORDS)
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

    # ─── 全体HTML組み立て ─────────────────────────────────────
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

/* ── Header ── */
.m-header {{
    text-align: center;
    padding: 18px 12px 14px;
    border-bottom: 1px solid rgba(0,255,204,0.15);
    background: linear-gradient(180deg, rgba(0,20,40,0.95) 0%, rgba(0,0,0,0.95) 100%);
    position: sticky;
    top: 0;
    z-index: 100;
}}
.m-header h1 {{
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    letter-spacing: 4px;
    color: rgba(0,255,204,0.9);
    text-shadow: 0 0 12px rgba(0,255,204,0.3);
    font-weight: 700;
}}
.m-header .m-sub {{
    font-size: 0.5rem;
    color: rgba(0,255,204,0.35);
    letter-spacing: 3px;
    margin-top: 4px;
}}

/* ── Accordion (details/summary) ── */
details {{
    border-bottom: 1px solid rgba(0,255,204,0.1);
}}
summary {{
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: rgba(0,255,204,0.85);
    padding: 14px 16px;
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
    top: 56px;
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

/* ── News Items ── */
.m-news-sub {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    letter-spacing: 2px;
    color: rgba(0,255,204,0.5);
    padding: 10px 0 6px;
    border-bottom: 1px solid rgba(0,255,204,0.06);
    margin-bottom: 4px;
}}
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
    z-index: 9999;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px
    );
}}
</style>
</head>
<body>

<div class="m-scanlines"></div>

<div class="m-header">
    <h1>STRATEGIC DASHBOARD</h1>
    <div class="m-sub">FUJITSU // KDDI ACCOUNT INTELLIGENCE</div>
</div>

<!-- NEWS & PRESS -->
<details open>
    <summary>NEWS &amp; PRESS RELEASES</summary>
    <div class="section-body">
        <div class="m-news-sub">KDDI x FUJITSU NEWS</div>
        {news_html}

        <div class="m-news-sub" style="margin-top:14px;">KDDI PRESS RELEASES</div>
        {press_html}

        <div class="m-news-sub" style="margin-top:14px;">FUJITSU PRESS RELEASES</div>
        {fujitsu_press_html}
    </div>
</details>

<!-- STOCK MONITOR -->
<details>
    <summary>STOCK MONITOR</summary>
    <div class="section-body">
        {stock_html}
    </div>
</details>

<!-- INSIGHT MATCHER -->
<details>
    <summary>INSIGHT MATCHER</summary>
    <div class="section-body">
        {insight_html}
    </div>
</details>

<!-- AI OPPORTUNITIES -->
<details>
    <summary>AI STRATEGIC OPPORTUNITIES</summary>
    <div class="section-body">
        {opp_html}
    </div>
</details>

<div class="m-footer">
    FUJITSU // ACCOUNT INTELLIGENCE DIVISION // MOBILE
</div>

</body></html>"""
