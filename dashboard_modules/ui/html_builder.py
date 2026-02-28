"""
HTML Dashboard Builder - Generates the main dashboard HTML
"""
import base64
from datetime import datetime
from ..config import APP_ROOT
from ..components.stock import fetch_stock, build_svg_chart
from ..components.news import fetch_news_for, fetch_kddi_press_releases, fetch_fujitsu_press_releases
from ..components.images import IMG_BG, IMG_MAP, img_tag
from ..components.weather import fetch_tokyo_weather
from ..components.context import get_active_context_data
from ..components.intelligence import fetch_bu_intelligence, WAKONX_KEYWORDS, BX_KEYWORDS
from ..analysis.insights import run_insight_matcher, check_alerts


def _load_image_b64(filename: str) -> str:
    """アプリルートから画像を読み込みBase64データURIを返す"""
    path = APP_ROOT / filename
    try:
        img_data = path.read_bytes()
        print(f"[IMG] Loaded {filename} ({len(img_data)} bytes)")
        return f"data:image/png;base64,{base64.b64encode(img_data).decode()}"
    except Exception as e:
        print(f"[IMG] Failed to load {filename}: {e}")
        return ""


def build_dashboard_html(proposal_history: list | None = None) -> str:

    # Load boot splash image as base64
    boot_splash_img = _load_image_b64("opening.png")

    # Load background logo as base64
    back_logo_img = _load_image_b64("back.png")

    # Fetch data
    kddi_price, kddi_diff, kddi_pct, kddi_dates, kddi_closes = fetch_stock("9433.T", 7)
    fujitsu_price, fujitsu_diff, fujitsu_pct, fujitsu_dates, fujitsu_closes = fetch_stock("6702.T", 7)
    docomo_price, docomo_diff, docomo_pct, docomo_dates, docomo_closes = fetch_stock("9437.T", 7)
    softbank_price, softbank_diff, softbank_pct, softbank_dates, softbank_closes = fetch_stock("9434.T", 7)
    ctc_price, ctc_diff, ctc_pct, ctc_dates, ctc_closes = fetch_stock("4739.T", 7)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def build_topic_html(articles: list[dict]) -> str:
        if not articles:
            return ""
        items = ""
        for a in articles:
            items += f'<div class="stock-topic"><a href="{a["link"]}" target="_blank">{a["title"]}</a></div>'
        return f'<div class="stock-topics">{items}</div>'

    def stock_block(name: str, ticker: str, price, diff, pct, dates, closes, color: str, query: str, alert_msg: str = "") -> str:
        topics = build_topic_html(fetch_news_for(query, 4))
        alert_badge = f'<span class="stock-alert-badge">{alert_msg}</span>' if alert_msg else ""
        if price is not None:
            direction = "up" if diff > 0 else ("down" if diff < 0 else "neutral")
            arrow = "▲" if diff > 0 else ("▼" if diff < 0 else "─")
            cls = {"up": "stock-up", "down": "stock-down", "neutral": "stock-neutral"}[direction]
            return f"""
            <div class="stock-section">
                <div class="stock-label">{name} // {ticker} {alert_badge}</div>
                <div class="stock-price {cls}">&yen;{price:,.1f}</div>
                <div class="stock-diff {cls}">{arrow} {abs(diff):,.1f} ({abs(pct):.2f}%)</div>
                {build_svg_chart(dates, closes, color)}
                {topics}
            </div>"""
        else:
            return f"""
            <div class="stock-section">
                <div class="stock-label">{name} // {ticker} {alert_badge}</div>
                <div class="stock-price" style="color:rgba(0,255,204,0.25);font-size:1rem;">AWAITING SIGNAL</div>
                {topics}
            </div>"""

    # 個別銘柄のアラートメッセージ生成
    fujitsu_alert = ""
    kddi_alert = ""
    docomo_alert = ""
    softbank_alert = ""
    ctc_alert = ""
    threshold = 2.0
    if fujitsu_pct is not None and abs(fujitsu_pct) >= threshold:
        fujitsu_alert = "急騰" if fujitsu_pct > 0 else "急落"
    if kddi_pct is not None and abs(kddi_pct) >= threshold:
        kddi_alert = "急騰" if kddi_pct > 0 else "急落"
    if docomo_pct is not None and abs(docomo_pct) >= threshold:
        docomo_alert = "急騰" if docomo_pct > 0 else "急落"
    if softbank_pct is not None and abs(softbank_pct) >= threshold:
        softbank_alert = "急騰" if softbank_pct > 0 else "急落"
    if ctc_pct is not None and abs(ctc_pct) >= threshold:
        ctc_alert = "急騰" if ctc_pct > 0 else "急落"

    # Primary stocks (always visible)
    stock_primary = stock_block("KDDI", "9433.T", kddi_price, kddi_diff, kddi_pct, kddi_dates, kddi_closes, "#00ffcc", "KDDI+%E6%A0%AA%E4%BE%A1", kddi_alert)
    stock_primary += stock_block("FUJITSU", "6702.T", fujitsu_price, fujitsu_diff, fujitsu_pct, fujitsu_dates, fujitsu_closes, "#00aaff", "%E5%AF%8C%E5%A3%AB%E9%80%9A+%E6%A0%AA%E4%BE%A1", fujitsu_alert)
    # Secondary stocks (collapsed by default)
    stock_secondary = stock_block("SoftBank", "9434.T", softbank_price, softbank_diff, softbank_pct, softbank_dates, softbank_closes, "#ffaa00", "%E3%82%BD%E3%83%95%E3%83%88%E3%83%90%E3%83%B3%E3%82%AF+%E6%A0%AA%E4%BE%A1", softbank_alert)
    stock_secondary += stock_block("NTT docomo", "9437.T", docomo_price, docomo_diff, docomo_pct, docomo_dates, docomo_closes, "#ff6699", "NTT%E3%83%89%E3%82%B3%E3%83%A2+%E6%A0%AA%E4%BE%A1", docomo_alert)
    stock_secondary += stock_block("CTC", "4739.T", ctc_price, ctc_diff, ctc_pct, ctc_dates, ctc_closes, "#9966ff", "CTC+%E6%A0%AA%E4%BE%A1", ctc_alert)
    stock_html = f"""{stock_primary}
    <div class="stock-secondary collapsed" id="stockSecondary">{stock_secondary}</div>
    <button class="stock-toggle-btn" id="stockToggleBtn" onclick="toggleStockExpand()">SHOW ALL (5)</button>"""

    # News for right panel
    news_all = fetch_news_for("KDDI+%E5%AF%8C%E5%A3%AB%E9%80%9A+%E9%80%9A%E4%BF%A1", 5)
    news_html = ""
    for i, a in enumerate(news_all, 1):
        news_html += f"""
        <div class="news-item">
            <div class="news-idx">INTEL-{i:03d}</div>
            <div class="news-title"><a href="{a['link']}" target="_blank">{a['title']}</a></div>
            <div class="news-date">{a.get('published', '')}</div>
        </div>"""
    if not news_html:
        news_html = '<div class="news-item"><div class="news-title" style="color:rgba(0,255,204,0.2);">NO INTEL FEED</div></div>'

    # KDDI Press Releases
    press_releases = fetch_kddi_press_releases(8)
    press_html = ""
    for i, pr in enumerate(press_releases, 1):
        press_html += f"""
        <div class="news-item">
            <div class="news-idx" style="color:#ff6699;">PR-{i:03d}</div>
            <div class="news-title"><a href="{pr['link']}" target="_blank">{pr['title']}</a></div>
            <div class="news-date">{pr.get('published', '')}</div>
        </div>"""
    if not press_html:
        press_html = '<div class="news-item"><div class="news-title" style="color:rgba(0,255,204,0.2);">NO PRESS RELEASE FEED</div></div>'

    # Fujitsu Press Releases
    fujitsu_releases = fetch_fujitsu_press_releases(8)
    fujitsu_press_html = ""
    for i, pr in enumerate(fujitsu_releases, 1):
        uvance_badge = ' <span style="background:#00aaff;color:#000;padding:1px 5px;border-radius:3px;font-size:0.45rem;font-weight:700;margin-left:4px;">UVANCE</span>' if pr.get("is_uvance") else ""
        fujitsu_press_html += f"""
        <div class="news-item">
            <div class="news-idx" style="color:#00aaff;">FJ-{i:03d}</div>
            <div class="news-title"><a href="{pr['link']}" target="_blank">{pr['title']}</a>{uvance_badge}</div>
            <div class="news-date">{pr.get('published', '')}</div>
        </div>"""
    if not fujitsu_press_html:
        fujitsu_press_html = '<div class="news-item"><div class="news-title" style="color:rgba(0,255,204,0.2);">NO FUJITSU PRESS FEED</div></div>'

    # ─── WAKONX/KDDI BX Intelligence Hub データ取得 ────────────────────
    wakonx_intel = fetch_bu_intelligence("WAKONX", WAKONX_KEYWORDS)
    bx_intel = fetch_bu_intelligence("BX", BX_KEYWORDS)

    # ─── PROPOSAL GENERATION HISTORY (中央パネル) ─────────────────────
    _proposals = proposal_history or []
    if _proposals:
        opp_rows = ""
        overlay_panels = ""
        for i, entry in enumerate(reversed(_proposals)):
            score = int(entry.get("score", 0))
            title = entry.get("opportunity_title", "Unknown")[:60]
            date_str = entry.get("generated_at", "")[:10]
            approach = entry.get("approach_plan", "")
            gamma_url = entry.get("gamma_url", "")
            if score >= 80:
                score_cls = "opp-score-high"
            elif score >= 50:
                score_cls = "opp-score-mid"
            else:
                score_cls = "opp-score-low"

            # Gamma link badge
            gamma_badge = ""
            if gamma_url:
                gamma_badge = f' <a href="{gamma_url}" target="_blank" style="color:#b478ff;font-size:0.5rem;text-decoration:underline;margin-left:6px;">GAMMA</a>'

            opp_rows += f"""
                <div class="opp-row" onclick="showApproachPlan({i})">
                    <div class="opp-score-wrap">
                        <div class="opp-score-label">SCORE</div>
                        <div class="opp-score {score_cls}">{score}</div>
                    </div>
                    <div class="opp-info">
                        <div class="opp-title">{title}{gamma_badge}</div>
                        <div class="opp-uvance">{date_str}</div>
                    </div>
                    <div class="opp-arrow">&#9654;</div>
                </div>"""

            # Approach plan overlay
            safe_approach = approach.replace('`', '&#96;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
            overlay_panels += f"""
                <div class="report-overlay" id="approachOverlay{i}" style="display:none;">
                    <div class="report-overlay-inner">
                        <div class="report-overlay-header">
                            <button class="report-close-btn-top" onclick="closeApproachPlan({i})">&#10005;</button>
                            <div class="report-overlay-label">HYPOTHESIS PROPOSAL // APPROACH PLAN</div>
                            <div class="report-overlay-title">{title}</div>
                            <div class="overlay-score-box">
                                <span class="overlay-score-num {'overlay-score-high' if score >= 80 else 'overlay-score-mid' if score >= 50 else 'overlay-score-low'}">{score}</span>
                                <span class="overlay-score-label">PROPOSAL QUALITY SCORE</span>
                            </div>
                        </div>
                        <div class="report-overlay-body">
                            <div class="section-body" style="white-space:pre-wrap;">{safe_approach if safe_approach else '<span style="color:rgba(180,120,255,0.3);">NO APPROACH PLAN DATA</span>'}</div>
                        </div>
                        <div class="report-overlay-footer">
                            FUJITSU // ACCOUNT INTELLIGENCE DIVISION // KDDI SECTOR // END OF PLAN
                        </div>
                    </div>
                </div>"""

        ai_html = f"""
        <div class="ai-panel" id="aiPanel">
            <div class="ai-title" onclick="toggleAiPanel()">
                PROPOSAL GENERATION HISTORY
                <span class="ai-toggle" id="aiToggle">&#9654;</span>
            </div>
            <div class="ai-body" id="aiBody">
                {opp_rows}
                <div class="opp-hint">CLICK TO VIEW APPROACH PLAN</div>
            </div>
        </div>
        {overlay_panels}"""
    else:
        ai_html = """
        <div class="ai-panel" id="aiPanel">
            <div class="ai-title" onclick="toggleAiPanel()">
                PROPOSAL GENERATION HISTORY
                <span class="ai-toggle" id="aiToggle">&#9654;</span>
            </div>
            <div class="ai-body" id="aiBody">
                <div class="ai-line" style="color:rgba(180,120,255,0.25);">NO PROPOSALS YET &#8212; USE GENERATE HYPOTHESIS</div>
            </div>
        </div>"""

    # ─── WAKONX/KDDI BX Intelligence Hub HTML ────────────────────
    # wakonx_intel と bx_intel は既に上で取得済み

    def build_bu_panel(bu_name: str, intel: dict, color: str, accent: str) -> str:
        """BU専用インテリジェンスパネル構築"""
        score = intel["opportunity_score"]
        score_color = "#00ff88" if score >= 70 else ("#ffaa00" if score >= 40 else "#ff6699")

        # ニュース表示
        news_items = ""
        for i, article in enumerate(intel["articles"][:4], 1):
            news_items += f"""
            <div class="bu-news-item">
                <span class="bu-news-idx">#{i:02d}</span>
                <a href="{article['link']}" target="_blank" class="bu-news-title">{article['title']}</a>
            </div>"""

        # マッチング表示
        match_items = ""
        for match in intel["matches"]:
            priority_badge = f'<span class="priority-badge priority-{match["priority"].lower()}">{match["priority"]}</span>'
            # ニュースタイトルを短縮表示
            source_title = match['title']
            if len(source_title) > 60:
                source_title = source_title[:60] + "..."
            match_items += f"""
            <div class="bu-match">
                <div class="bu-match-header">
                    <span class="bu-keyword">{match['keyword']}</span>
                    {priority_badge}
                    <span class="bu-uvance">{match['uvance']}</span>
                </div>
                <div class="bu-action">▸ {match['action']}</div>
                <div class="bu-source">
                    <span class="bu-source-label">検知元:</span>
                    <a href="{match['link']}" target="_blank">{source_title}</a>
                </div>
            </div>"""

        if not match_items:
            match_items = '<div style="color:rgba(255,255,255,0.2);font-size:0.7rem;padding:10px 0;">現在、キーワードマッチなし</div>'

        return f"""
        <div class="bu-panel" style="border-color:{color};">
            <div class="bu-header" style="background:linear-gradient(90deg, {color}22 0%, transparent 100%);">
                <div class="bu-title" style="color:{color};">{bu_name} INTELLIGENCE</div>
                <div class="bu-score">
                    <span style="color:{score_color};font-size:1.4rem;font-weight:700;">{score:.0f}</span>
                    <span style="font-size:0.5rem;color:rgba(255,255,255,0.4);">/100</span>
                    <div style="font-size:0.45rem;color:rgba(255,255,255,0.3);letter-spacing:2px;">OPPORTUNITY</div>
                </div>
            </div>
            <div class="bu-body">
                <div class="bu-section">
                    <div class="bu-section-title" style="color:{accent};">RECENT ACTIVITY</div>
                    {news_items}
                </div>
                <div class="bu-section">
                    <div class="bu-section-title" style="color:{accent};">UVANCE SYNERGY</div>
                    {match_items}
                </div>
            </div>
        </div>"""

    wakonx_html = build_bu_panel("WAKONX", wakonx_intel, "#00ffcc", "#00ffcc")
    bx_html = build_bu_panel("KDDI BX", bx_intel, "#ff6699", "#ff6699")

    # Insight Matcher HTML (実ニュースベース)
    matches, synergy_score = run_insight_matcher()
    # スコアに応じた色
    if synergy_score >= 70:
        score_color = "#00ff88"
        score_label = "HIGH"
    elif synergy_score >= 40:
        score_color = "#ffaa00"
        score_label = "MID"
    else:
        score_color = "#ff3366"
        score_label = "LOW"

    matcher_rows = ""

    for i, m in enumerate(matches[:2]):  # 最大2件まで表示
        delay = i * 6

        # AI評価スコア（confidence, strategic_fit等があれば表示）
        has_ai_scores = "confidence" in m
        if has_ai_scores:
            confidence = m.get("confidence", 70)
            strategic = m.get("strategic_fit", 70)
            urgency = m.get("urgency", 50)
            revenue = m.get("revenue_potential", 50)

            # スコアバーの色
            conf_color = "#00ff88" if confidence >= 80 else "#ffaa00" if confidence >= 60 else "#ff6699"
            strat_color = "#00ff88" if strategic >= 80 else "#ffaa00" if strategic >= 60 else "#ff6699"

            reasoning_text = m.get("reasoning", "分析中...")
            timing_text = m.get("timing_insight", "")
            explanation = f"{reasoning_text}"
            if timing_text:
                explanation = f"⏱ {timing_text}<br><br>{reasoning_text}"

            score_display = f"""
            <div class="ai-scores-simple">
                <span class="score-label-inline">商機</span>
                <span class="score-value-inline">{revenue}%</span>
                <div class="score-explain-btn" onclick="toggleExplanation({i})" title="スコア理由を表示">
                    <span class="explain-icon">ℹ</span>
                </div>
            </div>
            <div class="score-explanation" id="explanation{i}" style="display:none;">
                {explanation}
            </div>"""
        else:
            # フォールバック：頻度バー非表示
            score_display = ""

        # 富士通ソリューション名に商機スコアを追加
        fujitsu_display = m['fujitsu']
        if has_ai_scores and revenue:
            fujitsu_display = f"{m['fujitsu']} <span style='color:rgba(0,255,204,0.7);font-size:0.55rem;'>（商機{revenue}%）</span>"

        matcher_rows += f"""
        <div class="match-row" style="animation-delay:{delay}s;">
            <div class="match-kddi"><a href="{m['link']}" target="_blank">{m['kddi']}</a></div>
            <div class="match-center">
                <div class="match-found">MATCH！</div>
            </div>
            <div class="match-fujitsu"><a href="{m['fujitsu_url']}" target="_blank">{fujitsu_display}</a></div>
        </div>
        <div class="match-action" style="animation-delay:{delay + 2}s;">
            ▶ {m['action']}
        </div>
        <div class="match-source" style="animation-delay:{delay + 2}s;">
            {m['source'][:80]}
        </div>"""
    if not matches:
        matcher_rows += '<div style="text-align:center;color:rgba(0,255,204,0.3);font-size:0.6rem;letter-spacing:2px;">SCANNING FOR MATCHES...</div>'

    # アラート判定
    alerts = check_alerts(kddi_pct, fujitsu_pct, docomo_pct, softbank_pct, ctc_pct)
    alert_active = "active" if alerts else ""
    alert_html = ""
    for a in alerts:
        alert_html += f'<div class="alert-item">{a}</div>'

    bg_img = img_tag(IMG_BG, "bg-frame")
    map_img = img_tag(IMG_MAP, "holo-map")
    header_frame = ""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
    background: #000;
    color: #00ffcc;
    width: 100%; height: 100%;
    overflow: hidden;
    font-family: 'Share Tech Mono', monospace;
}}

.viewport {{
    position: relative;
    width: 100vw; height: 100vh;
    overflow: hidden;
    background: #000;
}}

/* BG frame - behind everything */
.bg-frame {{
    position: absolute; inset: 0;
    width: 100%; height: 100%;
    object-fit: fill;
    z-index: 1; pointer-events: none;
    opacity: 0.7;
}}
.bg-frame.placeholder {{ display: none; }}

/* Scanlines */
.scanlines {{
    position: absolute; inset: 0; z-index: 50;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.05) 2px, rgba(0,0,0,0.05) 4px);
    pointer-events: none;
}}

/* Vignette */
.vignette {{
    position: absolute; inset: 0; z-index: 50;
    pointer-events: none;
    background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.7) 100%);
}}

/* Background Logo - centered */
.bg-logo {{
    position: absolute;
    top: 25%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 2;
    pointer-events: none;
    opacity: 0.6;
    max-width: 30vw;
    max-height: 30vh;
}}

/* Loading Overlay - Streamlit実行中に表示 */
.stApp.streamlit-running::before {{
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: #000 url('{boot_splash_img}') center center no-repeat;
    background-size: 25vw auto;
    z-index: 9999;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.2s ease-in;
}}
.stApp.streamlit-running::after {{
    content: 'PROCESSING AI ANALYSIS...';
    position: fixed;
    top: 60%;
    left: 50%;
    transform: translateX(-50%);
    z-index: 10000;
    color: rgba(0,255,204,0.8);
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem;
    letter-spacing: 3px;
    opacity: 0;
    transition: opacity 0.2s ease-in;
    animation: pulse-text 1.5s ease-in-out infinite;
}}
.stApp.streamlit-running::before,
.stApp.streamlit-running::after {{
    opacity: 1;
}}
@keyframes pulse-text {{
    0%, 100% {{ opacity: 0.6; }}
    50% {{ opacity: 1; }}
}}

/* Hologram map - static, centered */
.holo-map {{
    width: 100%;
    display: block;
    animation: breathe 10s ease-in-out infinite;
    filter: drop-shadow(0 0 20px rgba(0,180,255,0.15));
}}
.holo-map.placeholder {{
    width: 100%; height: 34vw; max-height: 480px;
    border: 1px solid rgba(0,180,255,0.15); border-radius: 12px;
}}
@keyframes breathe {{
    0%, 100% {{ opacity: 0.75; transform: scale(1); }}
    50%      {{ opacity: 0.95; transform: scale(1.02); }}
}}

/* Map container for overlays */
.map-container {{
    position: absolute;
    top: 62%; left: 50%;
    transform: translate(-50%, -50%);
    width: 50vw; max-width: 700px;
    z-index: 3;
}}

/* Arrows converging to target */
.map-arrow {{
    position: absolute;
    z-index: 4;
    pointer-events: none;
}}
.map-arrow::before, .map-arrow::after {{
    content: "";
    position: absolute;
    background: rgba(0,180,255,0.6);
    border-radius: 1px;
}}

/* Top arrow - drops down */
.arrow-top {{
    top: 5%; left: 58%;
    width: 2px; height: 20%;
}}
.arrow-top::before {{
    width: 2px; height: 8px;
    animation: arrowDown 3s ease-in-out infinite;
    box-shadow: 0 0 6px rgba(0,180,255,0.8);
}}
/* Bottom arrow - moves up */
.arrow-bottom {{
    bottom: 15%; left: 45%;
    width: 2px; height: 20%;
}}
.arrow-bottom::before {{
    width: 2px; height: 8px;
    bottom: 0;
    animation: arrowUp 3s ease-in-out infinite;
    animation-delay: 0.8s;
    box-shadow: 0 0 6px rgba(0,180,255,0.8);
}}
/* Left arrow - moves right */
.arrow-left {{
    top: 42%; left: 10%;
    height: 2px; width: 25%;
}}
.arrow-left::before {{
    height: 2px; width: 10px;
    animation: arrowRight2 3.5s ease-in-out infinite;
    animation-delay: 0.4s;
    box-shadow: 0 0 6px rgba(0,180,255,0.8);
}}
/* Right arrow - moves left */
.arrow-right {{
    top: 36%; right: 15%;
    height: 2px; width: 25%;
}}
.arrow-right::before {{
    height: 2px; width: 10px;
    right: 0;
    animation: arrowLeft2 3.5s ease-in-out infinite;
    animation-delay: 1.2s;
    box-shadow: 0 0 6px rgba(0,180,255,0.8);
}}

/* Target ping pulse - red (KDDI TARGET LOCKED) */
.map-ping-red {{
    position: absolute;
    top: 48%; left: 48%;
    width: 20px; height: 20px;
    z-index: 5;
    pointer-events: none;
    border: 2px solid rgba(255,60,60,0.8);
    border-radius: 50%;
    animation: pingPulseRed 3s ease-out infinite;
}}
.map-ping-red::after {{
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 4px; height: 4px;
    background: rgba(255,60,60,0.9);
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(255,60,60,0.6);
}}

/* Fujitsu ping pulse - green (FUJITSU KAWASAKI) */
.map-ping-green {{
    position: absolute;
    top: 73%; left: 16%;
    width: 14px; height: 14px;
    z-index: 5;
    pointer-events: none;
    border: 2px solid rgba(0,255,100,0.8);
    border-radius: 50%;
    animation: pingPulseGreen 3s ease-out infinite;
    animation-delay: 1.5s;
}}
.map-ping-green::after {{
    content: "";
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 4px; height: 4px;
    background: rgba(0,255,100,0.9);
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(0,255,100,0.6);
}}

@keyframes arrowDown {{
    0%   {{ transform: translateY(0); opacity: 0; }}
    20%  {{ opacity: 1; }}
    80%  {{ opacity: 1; }}
    100% {{ transform: translateY(calc(20vh * 0.5)); opacity: 0; }}
}}
@keyframes arrowUp {{
    0%   {{ transform: translateY(0); opacity: 0; }}
    20%  {{ opacity: 1; }}
    80%  {{ opacity: 1; }}
    100% {{ transform: translateY(calc(-20vh * 0.5)); opacity: 0; }}
}}
@keyframes arrowRight2 {{
    0%   {{ transform: translateX(0); opacity: 0; }}
    20%  {{ opacity: 1; }}
    80%  {{ opacity: 1; }}
    100% {{ transform: translateX(calc(25vw * 0.4)); opacity: 0; }}
}}
@keyframes arrowLeft2 {{
    0%   {{ transform: translateX(0); opacity: 0; }}
    20%  {{ opacity: 1; }}
    80%  {{ opacity: 1; }}
    100% {{ transform: translateX(calc(-25vw * 0.4)); opacity: 0; }}
}}
@keyframes pingPulseRed {{
    0%   {{ transform: scale(1); opacity: 0.8; box-shadow: 0 0 4px rgba(255,60,60,0.5); }}
    70%  {{ transform: scale(3.5); opacity: 0; box-shadow: 0 0 20px rgba(255,60,60,0); }}
    100% {{ transform: scale(3.5); opacity: 0; }}
}}
@keyframes pingPulseGreen {{
    0%   {{ transform: scale(1); opacity: 0.8; box-shadow: 0 0 4px rgba(0,255,100,0.5); }}
    70%  {{ transform: scale(3.5); opacity: 0; box-shadow: 0 0 20px rgba(0,255,100,0); }}
    100% {{ transform: scale(3.5); opacity: 0; }}
}}

/* ── Header ── */
.hud-header {{
    position: absolute; top: 0; left: 0; right: 0;
    height: 50px; z-index: 20;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(180deg, rgba(0,8,18,0.95) 0%, transparent 100%);
}}
.hud-header-frame {{
    position: absolute; top: -4px; left: 50%; transform: translateX(-50%);
    width: 50vw; max-width: 680px; opacity: 0.4;
    pointer-events: none;
}}
.hud-header-frame.placeholder {{ display: none; }}
.hud-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem; font-weight: 900;
    letter-spacing: 8px; color: rgba(0,255,204,0.95);
    text-shadow: 0 0 16px rgba(0,255,204,0.4);
}}
.hud-clock {{
    position: absolute; right: 2%;
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: #00ffcc;
    letter-spacing: 2px;
    text-shadow: 0 0 12px rgba(0,255,204,0.5), 0 0 25px rgba(0,255,204,0.15);
}}
.hud-status {{
    position: absolute; left: 2%;
    font-size: 0.65rem;
    color: #00ffee;
    letter-spacing: 2px;
    font-weight: 600;
    text-shadow: 0 0 15px rgba(0,255,204,0.8), 0 0 30px rgba(0,255,204,0.4), 0 0 45px rgba(0,255,204,0.2);
}}

/* ── Panels ── */
.panel {{
    position: absolute;
    top: 60px; bottom: 40px;
    width: 22vw; min-width: 260px; max-width: 360px;
    z-index: 10;
    border: 1px solid rgba(0,255,204,0.12);
    border-radius: 6px;
    background: rgba(0,12,24,0.85);
    box-shadow: inset 0 0 60px rgba(0,255,204,0.02), 0 0 20px rgba(0,255,204,0.04);
    overflow-y: auto; scrollbar-width: none;
}}
.panel::-webkit-scrollbar {{ display: none; }}
.panel.left  {{ left: 1.5%; }}
.panel.right {{ right: 1.5%; }}
.panel-inner {{
    padding: 18px 16px;
}}
.panel-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.6rem; font-weight: 700;
    letter-spacing: 4px; color: rgba(0,255,204,0.9);
    text-shadow: 0 0 10px rgba(0,255,204,0.4);
    margin-bottom: 14px; padding-bottom: 8px;
    border-bottom: 1px solid rgba(0,255,204,0.12);
}}
.panel-title-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(0,255,204,0.12);
}}
.panel-title-row .panel-title {{
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
}}
.bu-toggle-btn {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    letter-spacing: 2px;
    padding: 4px 10px;
    background: rgba(0,255,204,0.08);
    border: 1px solid rgba(0,255,204,0.3);
    border-radius: 3px;
    color: #00ffcc;
    cursor: pointer;
    transition: all 0.3s;
    text-shadow: 0 0 6px rgba(0,255,204,0.3);
}}
.bu-toggle-btn:hover {{
    background: rgba(0,255,204,0.15);
    border-color: rgba(0,255,204,0.6);
    text-shadow: 0 0 12px rgba(0,255,204,0.6);
    transform: scale(1.05);
}}
.bu-content {{
    display: none;
}}
.bu-content.active {{
    display: block;
}}

/* Corner brackets */
.panel::before, .panel::after {{
    content: ""; position: absolute;
    width: 16px; height: 16px;
    border-color: rgba(0,255,204,0.25); border-style: solid;
}}
.panel::before {{ top: -1px; left: -1px; border-width: 2px 0 0 2px; }}
.panel::after  {{ bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }}

/* ── Insight Matcher (center) ── */
.insight-matcher {{
    position: absolute;
    top: 55px; left: 50%;
    transform: translateX(-50%);
    width: 52vw; max-width: 680px;
    z-index: 10;
    padding: 8px 16px;
    border: 1px solid rgba(0,255,204,0.12);
    border-radius: 6px;
    background: rgba(0,12,24,0.85);
    box-shadow: inset 0 0 60px rgba(0,255,204,0.02), 0 0 20px rgba(0,255,204,0.04);
    max-height: 320px;
    overflow-y: auto;
    scrollbar-width: none;
}}
/* INSIGHT MATCHER トグル関連 */
.matcher-body {{
    transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
    max-height: 2000px;
    opacity: 1;
    overflow: hidden;
}}
.matcher-body.collapsed {{
    max-height: 0;
    opacity: 0;
}}
.matcher-toggle {{
    margin-left: 10px;
    font-size: 0.8rem;
    transition: transform 0.3s;
    display: inline-block;
}}
/* Synergy score display */
.synergy-score {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-bottom: 6px;
    padding: 4px 0;
    border: 1px solid rgba(0,255,204,0.08);
    border-radius: 4px;
    background: rgba(0,0,0,0.3);
}}
.score-label {{
    font-family: 'Orbitron', monospace;
    font-size: 0.45rem;
    color: rgba(0,255,204,0.4);
    letter-spacing: 3px;
}}
.score-value {{
    font-family: 'Orbitron', monospace;
    font-size: 1.4rem;
    font-weight: 900;
    text-shadow: 0 0 20px currentColor;
}}
.score-rank {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-shadow: 0 0 10px currentColor;
}}
.score-formula {{
    font-size: 0.4rem;
    color: rgba(0,255,204,0.2);
    font-style: italic;
}}
.freq-bar {{
    font-size: 0.5rem;
    color: rgba(0,255,204,0.3);
    letter-spacing: 1px;
}}

/* Alert overlay */
.alert-overlay {{
    position: absolute;
    inset: 0;
    z-index: 100;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.3s;
}}
.alert-overlay.active {{
    opacity: 1;
    animation: alertFlash 4s ease-in-out infinite;
}}
.alert-overlay.active::before {{
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,0,0,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,0,0,0.03) 1px, transparent 1px);
    background-size: 24px 24px;
    animation: alertGrid 2s linear infinite;
}}
.alert-overlay.active::after {{
    content: "";
    position: absolute;
    inset: 0;
    border: 2px solid rgba(255,0,0,0.15);
    box-shadow: inset 0 0 80px rgba(255,0,0,0.05);
}}
@keyframes alertFlash {{
    0%, 100% {{ opacity: 0.5; }}
    50% {{ opacity: 1; }}
}}
@keyframes alertGrid {{
    0% {{ transform: translateY(0); }}
    100% {{ transform: translateY(24px); }}
}}

/* ── Pip-Boy Weather Terminal ── */
.pipboy-weather {{
    position: absolute;
    top: 400px;
    left: 50%;
    transform: translateX(-50%);
    width: 50vw;
    max-width: 650px;
    z-index: 10;
    background: rgba(0,0,0,0.95);
    border: 2px solid rgba(0,255,204,0.2);
    border-radius: 3px;
    padding: 12px 16px;
    box-shadow: inset 0 0 30px rgba(0,255,204,0.05), 0 0 20px rgba(0,255,204,0.1);
    overflow: hidden;
}}
.pipboy-weather::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        rgba(0,255,204,0.02) 0px,
        rgba(0,255,204,0.02) 2px,
        transparent 2px,
        transparent 4px
    );
    pointer-events: none;
    z-index: 1;
}}
.pipboy-header {{
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    font-weight: bold;
    letter-spacing: 2px;
    color: rgba(0,255,204,0.6);
    text-align: center;
    border-bottom: 1px solid rgba(0,255,204,0.2);
    padding-bottom: 6px;
    margin-bottom: 12px;
    text-shadow: 0 0 5px rgba(0,255,204,0.3);
    position: relative;
    z-index: 2;
}}
.pipboy-body {{
    display: flex;
    gap: 20px;
    align-items: center;
    position: relative;
    z-index: 2;
}}
.pipboy-character {{
    flex-shrink: 0;
    width: 100px;
}}
.vault-boy {{
    width: 100%;
    height: auto;
    filter: drop-shadow(0 0 5px rgba(0,255,204,0.3));
}}
.pipboy-data {{
    flex: 1;
    display: flex;
    gap: 20px;
    align-items: center;
}}
.pipboy-temp-display {{
    text-align: center;
    border-right: 2px solid rgba(0,255,204,0.2);
    padding-right: 20px;
}}
.pipboy-temp-value {{
    font-family: 'Courier New', monospace;
    font-size: 3rem;
    font-weight: bold;
    color: rgba(0,255,204,0.9);
    line-height: 1;
    text-shadow: 0 0 10px rgba(0,255,204,0.4);
}}
.pipboy-temp-label {{
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    color: rgba(0,255,204,0.5);
    margin-top: 4px;
    letter-spacing: 2px;
}}
.pipboy-stats {{
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
.pipboy-stat {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 8px;
    background: rgba(0,255,204,0.03);
    border-left: 2px solid rgba(0,255,204,0.2);
}}
.pipboy-stat-label {{
    font-family: 'Courier New', monospace;
    font-size: 0.65rem;
    color: rgba(0,255,204,0.5);
    letter-spacing: 1px;
}}
.pipboy-stat-value {{
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    font-weight: bold;
    color: rgba(0,255,204,0.8);
    text-shadow: 0 0 5px rgba(0,255,204,0.3);
}}

/* Alert banner */
.alert-banner {{
    position: absolute;
    top: 52px; left: 50%;
    transform: translateX(-50%);
    z-index: 101;
    display: flex;
    gap: 12px;
    pointer-events: none;
}}
.alert-item {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    font-weight: 700;
    color: #ff3366;
    letter-spacing: 2px;
    padding: 3px 12px;
    border: 1px solid rgba(255,51,102,0.3);
    border-radius: 3px;
    background: rgba(255,0,0,0.08);
    animation: alertBlink 1.5s ease-in-out infinite;
    text-shadow: 0 0 8px rgba(255,51,102,0.4);
}}
@keyframes alertBlink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.4; }}
}}

/* AI Strategic Insight panel */
.ai-panel {{
    position: absolute;
    top: 42%; left: 50%;
    transform: translate(-50%, 0);
    width: 52vw; max-width: 680px;
    z-index: 10;
    padding: 10px 14px;
    border: 1px solid rgba(180,120,255,0.12);
    border-radius: 6px;
    background: rgba(10,5,20,0.45);
    box-shadow: 0 0 20px rgba(180,120,255,0.04);
    backdrop-filter: blur(3px);
}}
.ai-line {{
    font-size: 0.75rem;
    color: rgba(200,170,255,0.75);
    line-height: 1.7;
    margin-bottom: 1px;
}}
.ai-line.ai-section-head {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    font-weight: 700;
    color: rgba(180,120,255,0.8);
    letter-spacing: 2px;
    margin-top: 8px;
    margin-bottom: 2px;
    text-shadow: 0 0 6px rgba(180,120,255,0.3);
}}

/* Opportunity rows */
.opp-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 10px;
    margin-bottom: 4px;
    border: 1px solid rgba(180,120,255,0.06);
    border-radius: 4px;
    background: rgba(20,10,40,0.4);
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
}}
.opp-row:hover {{
    background: rgba(180,120,255,0.08);
    border-color: rgba(180,120,255,0.25);
    box-shadow: 0 0 12px rgba(180,120,255,0.08);
}}
.opp-row-pending {{
    cursor: default;
    opacity: 0.6;
}}
.opp-score-wrap {{
    flex-shrink: 0;
    text-align: center;
    min-width: 38px;
}}
.opp-score-label {{
    font-family: 'Orbitron', monospace;
    font-size: 0.35rem;
    color: rgba(0,255,204,0.7);
    letter-spacing: 2px;
    margin-bottom: 2px;
}}
.opp-score {{
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 900;
    letter-spacing: 1px;
    text-shadow: 0 0 10px currentColor;
}}
.opp-score-high {{ color: #00ff88; }}
.opp-score-mid {{ color: #ffaa00; }}
.opp-score-low {{ color: rgba(180,120,255,0.4); }}
.opp-info {{
    flex: 1;
    min-width: 0;
}}
.opp-title {{
    font-size: 0.65rem;
    color: rgba(200,170,255,0.85);
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.opp-uvance {{
    font-size: 0.55rem;
    color: rgba(200,170,255,0.8);
    letter-spacing: 1px;
    margin-top: 2px;
}}
.opp-arrow {{
    color: rgba(180,120,255,0.25);
    font-size: 0.6rem;
    flex-shrink: 0;
    transition: all 0.3s;
}}
.opp-row:hover .opp-arrow {{
    color: rgba(180,120,255,0.7);
    transform: translateX(3px);
}}
.opp-hint {{
    font-family: 'Orbitron', monospace;
    font-size: 0.35rem;
    color: rgba(180,120,255,0.2);
    letter-spacing: 3px;
    text-align: center;
    margin-top: 8px;
}}
.generate-btn {{
    background: rgba(180,120,255,0.1);
    border: 1px solid rgba(180,120,255,0.3);
    color: rgba(200,170,255,0.8);
    font-family: 'Orbitron', monospace;
    font-size: 0.4rem;
    letter-spacing: 2px;
    padding: 4px 16px;
    cursor: pointer;
    border-radius: 3px;
    transition: all 0.3s;
}}
.generate-btn:hover {{
    background: rgba(180,120,255,0.25);
    color: rgba(220,200,255,1);
    box-shadow: 0 0 10px rgba(180,120,255,0.15);
}}
/* Report overlay */
.report-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: rgba(0,0,0,0.92);
    justify-content: center;
    align-items: flex-start;
    overflow-y: auto;
    padding: 20px;
}}
.report-overlay-inner {{
    max-width: 860px;
    width: 100%;
    margin: 0 auto;
    padding: 30px;
    position: relative;
}}
.report-overlay-header {{
    position: relative;
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(180,120,255,0.15);
}}
.report-overlay-label {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    letter-spacing: 6px;
    color: rgba(180,120,255,0.4);
    margin-bottom: 10px;
}}
.report-overlay-title {{
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 900;
    color: rgba(200,160,255,1);
    letter-spacing: 2px;
    text-shadow: 0 0 25px rgba(180,120,255,0.4);
    line-height: 1.6;
    margin-bottom: 14px;
}}
.overlay-score-box {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 12px 0 16px 0;
    padding: 10px 16px;
    border: 1px solid rgba(180,120,255,0.12);
    border-radius: 6px;
    background: rgba(15,8,30,0.7);
    flex-wrap: wrap;
}}
.overlay-score-num {{
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    font-weight: 900;
    letter-spacing: 2px;
    line-height: 1;
}}
.overlay-score-high {{ color: #0fc; text-shadow: 0 0 15px rgba(0,255,204,0.5); }}
.overlay-score-mid {{ color: #fc0; text-shadow: 0 0 15px rgba(255,204,0,0.4); }}
.overlay-score-low {{ color: rgba(180,120,255,0.5); }}
.overlay-score-label {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    color: rgba(180,120,255,0.5);
    letter-spacing: 3px;
}}
.overlay-score-reason {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: rgba(240,230,255,0.8);
    flex-basis: 100%;
    margin-top: 4px;
    line-height: 1.6;
}}
.report-close-btn {{
    background: rgba(180,120,255,0.1);
    border: 1px solid rgba(180,120,255,0.3);
    color: rgba(180,120,255,0.8);
    font-family: 'Orbitron', monospace;
    font-size: 0.6rem;
    letter-spacing: 3px;
    padding: 6px 20px;
    cursor: pointer;
    border-radius: 3px;
    transition: all 0.3s;
}}
.report-close-btn:hover {{
    background: rgba(180,120,255,0.25);
    color: rgba(180,120,255,1);
    box-shadow: 0 0 15px rgba(180,120,255,0.2);
}}
.report-close-btn-top {{
    position: absolute;
    top: 20px;
    right: 20px;
    background: rgba(255,100,100,0.15);
    border: 1px solid rgba(255,100,100,0.4);
    color: rgba(255,150,150,0.9);
    font-family: 'Orbitron', monospace;
    font-size: 1.2rem;
    width: 40px;
    height: 40px;
    cursor: pointer;
    border-radius: 50%;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}}
.report-close-btn-top:hover {{
    background: rgba(255,100,100,0.3);
    border-color: rgba(255,100,100,0.7);
    color: rgba(255,200,200,1);
    box-shadow: 0 0 20px rgba(255,100,100,0.3);
    transform: rotate(90deg);
}}
.report-overlay-body {{
    font-family: 'Share Tech Mono', monospace;
    color: rgba(220,200,255,0.85);
}}
.report-overlay-body .report-section {{
    margin-bottom: 22px;
    padding: 18px 22px;
    border: 1px solid rgba(180,120,255,0.15);
    border-radius: 6px;
    background: rgba(15,8,30,0.8);
    box-shadow: 0 0 12px rgba(180,120,255,0.03);
}}
.report-overlay-body .section-header {{
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: rgba(200,160,255,1);
    letter-spacing: 3px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(180,120,255,0.25);
    text-shadow: 0 0 10px rgba(180,120,255,0.4);
}}
.report-overlay-body .section-body {{
    font-size: 0.95rem;
    line-height: 2.2;
    color: rgba(240,230,255,0.95);
}}
.report-overlay-body .section-uvance {{
    border-color: rgba(0,180,255,0.2);
    background: rgba(0,20,40,0.6);
}}
.report-overlay-body .section-uvance .section-header {{
    color: rgba(0,200,255,0.9);
    border-bottom-color: rgba(0,180,255,0.2);
    text-shadow: 0 0 10px rgba(0,180,255,0.4);
}}
.sub-heading {{
    display: inline-block;
    color: rgba(0,255,204,1);
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 2px;
    margin-top: 8px;
    text-shadow: 0 0 8px rgba(0,255,204,0.4);
}}
.report-overlay-actions {{
    text-align: center;
    margin: 24px 0;
    padding: 16px 0;
    border-top: 1px solid rgba(180,120,255,0.1);
}}
.asana-btn {{
    background: rgba(180,120,255,0.12);
    border: 1px solid rgba(180,120,255,0.35);
    color: rgba(200,170,255,0.9);
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    padding: 10px 30px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.3s;
}}
.asana-btn:hover {{
    background: rgba(180,120,255,0.25);
    border-color: rgba(180,120,255,0.6);
    box-shadow: 0 0 15px rgba(180,120,255,0.15);
    color: rgba(220,200,255,1);
}}
.proposal-btn {{
    background: rgba(0,255,204,0.12);
    border: 1px solid rgba(0,255,204,0.35);
    color: rgba(0,255,204,0.9);
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    padding: 10px 30px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.3s;
    margin-left: 10px;
}}
.proposal-btn:hover {{
    background: rgba(0,255,204,0.25);
    border-color: rgba(0,255,204,0.6);
    box-shadow: 0 0 15px rgba(0,255,204,0.15);
    color: rgba(0,255,230,1);
}}
.gemini-btn {{
    background: rgba(255,170,0,0.12);
    border: 1px solid rgba(255,170,0,0.35);
    color: rgba(255,170,0,0.9);
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    padding: 10px 30px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.3s;
    margin-left: 10px;
}}
.gemini-btn:hover {{
    background: rgba(255,170,0,0.25);
    border-color: rgba(255,170,0,0.6);
    box-shadow: 0 0 15px rgba(255,170,0,0.15);
    color: rgba(255,200,50,1);
}}
.save-btn {{
    background: rgba(0,180,255,0.12);
    border: 1px solid rgba(0,180,255,0.35);
    color: rgba(0,180,255,0.9);
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    padding: 10px 30px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.3s;
    margin-left: 10px;
}}
.save-btn:hover {{
    background: rgba(0,180,255,0.25);
    border-color: rgba(0,180,255,0.6);
    box-shadow: 0 0 15px rgba(0,180,255,0.15);
    color: rgba(100,220,255,1);
}}
.report-overlay-actions {{
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}}
.report-overlay-footer {{
    text-align: center;
    margin-top: 30px;
    padding-top: 16px;
    border-top: 1px solid rgba(180,120,255,0.08);
    font-family: 'Orbitron', monospace;
    font-size: 0.4rem;
    color: rgba(180,120,255,0.2);
    letter-spacing: 4px;
}}
.ai-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 4px;
    color: rgba(210,170,255,1);
    text-shadow: 0 0 12px rgba(180,120,255,0.5);
    text-align: center;
    margin-bottom: 8px;
    padding-bottom: 5px;
    border-bottom: 1px solid rgba(180,120,255,0.15);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    user-select: none;
}}
.ai-toggle {{
    font-size: 0.5rem;
    color: rgba(180,120,255,0.4);
    transition: transform 0.3s;
}}
.ai-panel.collapsed .ai-toggle {{
    transform: rotate(-90deg);
}}
.ai-body {{
    max-height: 500px;
    overflow: hidden;
    transition: max-height 0.4s ease, opacity 0.3s ease;
    opacity: 1;
}}
.ai-body.collapsed {{
    max-height: 0;
    opacity: 0;
}}

/* ── BU Intelligence Hub ── */
.bu-panel {{
    background: rgba(0,8,18,0.5);
    border: 1px solid;
    border-radius: 4px;
    margin-bottom: 0;
    backdrop-filter: blur(4px);
    box-shadow: 0 0 12px rgba(0,255,204,0.05);
}}
.bu-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}}
.bu-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-shadow: 0 0 10px currentColor;
}}
.bu-score {{
    text-align: center;
}}
.bu-body {{
    padding: 10px 12px;
}}
.bu-section {{
    margin-bottom: 10px;
}}
.bu-section-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    letter-spacing: 3px;
    opacity: 0.7;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.bu-news-item {{
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    display: flex;
    gap: 8px;
    align-items: flex-start;
}}
.bu-news-idx {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    color: rgba(0,255,204,0.4);
    min-width: 24px;
}}
.bu-news-title {{
    font-size: 0.7rem;
    color: rgba(255,255,255,0.75);
    text-decoration: none;
    line-height: 1.4;
    transition: all 0.3s;
}}
.bu-news-title:hover {{
    color: #00ffcc;
    text-shadow: 0 0 8px rgba(0,255,204,0.4);
}}
.bu-match {{
    background: rgba(255,255,255,0.02);
    border-left: 2px solid rgba(0,255,204,0.3);
    padding: 8px 10px;
    margin-bottom: 6px;
    border-radius: 3px;
}}
.bu-match-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    flex-wrap: wrap;
}}
.bu-keyword {{
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    color: #ffaa00;
    font-weight: 600;
    letter-spacing: 1px;
}}
.bu-uvance {{
    font-size: 0.6rem;
    color: rgba(180,120,255,0.8);
    letter-spacing: 1px;
}}
.bu-action {{
    font-size: 0.65rem;
    color: rgba(0,255,204,0.8);
    line-height: 1.5;
    padding-left: 8px;
    margin-bottom: 4px;
}}
.bu-source {{
    font-size: 0.6rem;
    line-height: 1.4;
    padding-left: 8px;
    margin-top: 4px;
    font-style: italic;
}}
.bu-source-label {{
    color: rgba(100,100,100,0.5);
    margin-right: 4px;
}}
.bu-source a {{
    color: rgba(100,100,100,0.5);
    text-decoration: none;
    transition: all 0.3s;
}}
.bu-source a:hover {{
    color: rgba(150,150,150,0.7);
    text-decoration: underline;
}}
.priority-badge {{
    font-family: 'Orbitron', monospace;
    font-size: 0.45rem;
    padding: 2px 6px;
    border-radius: 3px;
    font-weight: 600;
    letter-spacing: 1px;
}}
.priority-high {{
    background: rgba(255,0,0,0.15);
    color: #ff4444;
    border: 1px solid rgba(255,0,0,0.3);
}}
.priority-medium {{
    background: rgba(255,170,0,0.15);
    color: #ffaa00;
    border: 1px solid rgba(255,170,0,0.3);
}}
.priority-low {{
    background: rgba(100,100,100,0.15);
    color: #888;
    border: 1px solid rgba(100,100,100,0.3);
}}

.matcher-title {{
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem; font-weight: 700;
    letter-spacing: 4px; color: rgba(0,255,204,0.9);
    text-shadow: 0 0 10px rgba(0,255,204,0.4);
    text-align: center;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(0,255,204,0.12);
}}
.match-row {{
    display: flex; align-items: center;
    justify-content: space-between;
    margin-bottom: 2px;
    opacity: 0;
    animation: matchAppear 24s ease-in-out infinite;
}}
.match-kddi {{
    font-size: 0.7rem; color: #ff6644;
    text-align: right; flex: 1;
    opacity: 0;
    animation: slideFromLeft 24s ease-out infinite;
    text-shadow: 0 0 8px rgba(255,102,68,0.3);
}}
.match-center {{
    width: 100px; text-align: center;
    flex-shrink: 0;
    position: relative;
}}
/* Animated arrows flowing toward center */
.match-center::before, .match-center::after {{
    content: "";
    position: absolute;
    top: 50%; height: 1px;
    width: 30px;
}}
.match-center::before {{
    right: 55px;
    background: linear-gradient(90deg, transparent, #ff6644);
    animation: arrowLeft 2s ease-in-out infinite;
}}
.match-center::after {{
    left: 55px;
    background: linear-gradient(270deg, transparent, #00aaff);
    animation: arrowRight 2s ease-in-out infinite;
}}
@keyframes arrowLeft {{
    0%   {{ opacity: 0; transform: translateX(-15px); }}
    50%  {{ opacity: 1; transform: translateX(10px); }}
    100% {{ opacity: 0; transform: translateX(10px); }}
}}
@keyframes arrowRight {{
    0%   {{ opacity: 0; transform: translateX(15px); }}
    50%  {{ opacity: 1; transform: translateX(-10px); }}
    100% {{ opacity: 0; transform: translateX(-10px); }}
}}
.match-found {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem; font-weight: 900;
    color: #00ff88;
    letter-spacing: 2px;
    opacity: 0;
    animation: matchFlash 24s ease-in-out infinite;
    text-shadow: 0 0 12px rgba(0,255,136,0.5);
}}
.match-fujitsu {{
    font-size: 0.7rem; color: #00aaff;
    text-align: left; flex: 1;
    opacity: 0;
    animation: slideFromRight 24s ease-out infinite;
    text-shadow: 0 0 8px rgba(0,170,255,0.3);
}}
.match-action {{
    font-size: 0.6rem;
    color: rgba(0,255,204,0.7);
    text-align: center;
    margin-bottom: 4px;
    padding: 3px 0;
    opacity: 0;
    animation: actionAppear 24s ease-in-out infinite;
    letter-spacing: 1px;
}}
.ai-scores {{
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
    margin: 6px 0;
    padding: 8px;
    background: rgba(0,12,24,0.6);
    border: 1px solid rgba(0,255,204,0.1);
    border-radius: 3px;
}}
.score-item {{
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 2px 4px;
}}
.score-label {{
    font-size: 0.45rem;
    color: rgba(0,255,204,0.5);
    letter-spacing: 1px;
    font-family: 'Orbitron', monospace;
}}
.score-value {{
    font-size: 0.65rem;
    font-weight: 700;
    color: rgba(0,255,204,0.9);
    font-family: 'Orbitron', monospace;
    text-shadow: 0 0 8px rgba(0,255,204,0.3);
}}
.ai-scores-simple {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 4px 0;
    padding: 4px 8px;
    background: rgba(0,12,24,0.4);
    border: 1px solid rgba(0,255,204,0.1);
    border-radius: 3px;
}}
.score-label-inline {{
    font-size: 0.5rem;
    color: rgba(0,255,204,0.6);
    letter-spacing: 1px;
    font-family: 'Orbitron', monospace;
}}
.score-value-inline {{
    font-size: 0.7rem;
    font-weight: 700;
    color: rgba(0,255,204,0.95);
    font-family: 'Orbitron', monospace;
    text-shadow: 0 0 10px rgba(0,255,204,0.4);
}}
.score-explain-btn {{
    cursor: pointer;
    padding: 4px 8px;
    font-size: 0.45rem;
    color: rgba(180,120,255,0.7);
    background: rgba(180,120,255,0.05);
    border: 1px solid rgba(180,120,255,0.2);
    border-radius: 3px;
    font-family: 'Orbitron', monospace;
    letter-spacing: 1px;
    transition: all 0.2s;
    margin-left: auto;
}}
.score-explain-btn:hover {{
    color: rgba(180,120,255,1);
    background: rgba(180,120,255,0.15);
    border-color: rgba(180,120,255,0.4);
}}
.explain-icon {{
    font-size: 0.6rem;
    margin-right: 2px;
}}
.score-explanation {{
    margin: 8px 0;
    padding: 8px 10px;
    background: rgba(10,5,20,0.6);
    border-left: 3px solid rgba(180,120,255,0.5);
    border-radius: 3px;
    font-size: 0.55rem;
    line-height: 1.5;
    color: rgba(200,170,255,0.85);
    font-family: 'Share Tech Mono', monospace;
}}
.match-source {{
    font-size: 0.48rem;
    color: rgba(0,255,204,0.25);
    text-align: center;
    margin-bottom: 14px;
    padding-bottom: 6px;
    border-bottom: 1px dashed rgba(0,255,204,0.06);
    opacity: 0;
    animation: actionAppear 24s ease-in-out infinite;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.match-kddi a {{
    color: #ff6644;
    text-decoration: none;
}}
.match-kddi a:hover {{
    color: #ff8866;
    text-shadow: 0 0 12px rgba(255,102,68,0.5);
}}
.match-fujitsu a {{
    color: #00aaff;
    text-decoration: none;
}}
.match-fujitsu a:hover {{
    color: #44ccff;
    text-shadow: 0 0 12px rgba(0,170,255,0.5);
}}

@keyframes slideFromLeft {{
    0%, 4% {{ opacity: 0; transform: translateX(-40px); }}
    8%, 80% {{ opacity: 1; transform: translateX(0); }}
    90%, 100% {{ opacity: 0; transform: translateX(0); }}
}}
@keyframes slideFromRight {{
    0%, 8% {{ opacity: 0; transform: translateX(40px); }}
    12%, 80% {{ opacity: 1; transform: translateX(0); }}
    90%, 100% {{ opacity: 0; transform: translateX(0); }}
}}
@keyframes matchFlash {{
    0%, 14% {{ opacity: 0; }}
    16% {{ opacity: 1; }}
    20% {{ opacity: 0.3; }}
    24%, 80% {{ opacity: 1; }}
    90%, 100% {{ opacity: 0; }}
}}
@keyframes matchAppear {{
    0%, 2% {{ opacity: 0; }}
    6%, 85% {{ opacity: 1; }}
    95%, 100% {{ opacity: 0; }}
}}
@keyframes actionAppear {{
    0%, 16% {{ opacity: 0; transform: translateY(-5px); }}
    20%, 80% {{ opacity: 1; transform: translateY(0); }}
    90%, 100% {{ opacity: 0; }}
}}

/* ── Stock ── */
.stock-section {{
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(0,255,204,0.06);
}}
.stock-section:last-child {{ border-bottom: none; }}
.stock-secondary {{
    overflow: hidden;
    transition: max-height 0.3s ease, opacity 0.3s ease;
    max-height: 2000px;
    opacity: 1;
}}
.stock-secondary.collapsed {{
    max-height: 0;
    opacity: 0;
}}
.stock-toggle-btn {{
    display: block;
    width: 100%;
    padding: 4px 0;
    margin: 4px 0 8px;
    background: rgba(0,255,204,0.06);
    border: 1px solid rgba(0,255,204,0.15);
    border-radius: 3px;
    color: rgba(0,255,204,0.6);
    font-family: 'Orbitron', monospace;
    font-size: 0.45rem;
    letter-spacing: 2px;
    cursor: pointer;
    text-align: center;
}}
.stock-toggle-btn:hover {{
    background: rgba(0,255,204,0.12);
    color: rgba(0,255,204,0.9);
}}
.hypothesis-btn {{
    display: block;
    width: 100%;
    padding: 8px 0;
    margin: 12px 0 4px;
    background: rgba(180,120,255,0.08);
    border: 1px solid rgba(180,120,255,0.3);
    border-radius: 4px;
    color: rgba(180,120,255,0.9);
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem;
    letter-spacing: 3px;
    cursor: pointer;
    text-align: center;
    text-shadow: 0 0 8px rgba(180,120,255,0.3);
    transition: all 0.2s;
}}
.hypothesis-btn:hover {{
    background: rgba(180,120,255,0.18);
    border-color: rgba(180,120,255,0.6);
    color: rgba(200,160,255,1);
    text-shadow: 0 0 12px rgba(180,120,255,0.5);
}}
.stock-label {{
    font-size: 0.75rem; color: #00ffcc;
    letter-spacing: 2px; margin-bottom: 2px;
    text-shadow: 0 0 8px rgba(0,255,204,0.3);
    display: flex; align-items: center; gap: 8px;
}}
.stock-alert-badge {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem; font-weight: 700;
    color: #ff3366;
    letter-spacing: 1px;
    padding: 1px 8px;
    border: 1px solid rgba(255,51,102,0.5);
    border-radius: 3px;
    background: rgba(255,0,0,0.12);
    animation: alertBlink 1.5s ease-in-out infinite;
    text-shadow: 0 0 8px rgba(255,51,102,0.5);
}}
.stock-price {{
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem; font-weight: 900;
    line-height: 1.2; margin: 4px 0 2px;
    text-shadow: 0 0 20px currentColor;
}}
.stock-diff {{
    font-size: 0.8rem; margin-bottom: 4px;
}}
.stock-up   {{ color: #00ff88; }}
.stock-down {{ color: #ff3366; }}
.stock-neutral {{ color: #00ffcc; }}

/* Stock related topics */
.stock-topics {{
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1px dashed rgba(0,255,204,0.08);
}}
.stock-topic {{
    font-size: 0.65rem;
    line-height: 1.8;
    color: rgba(0,255,204,0.6);
    white-space: nowrap;
    overflow: hidden;
}}
.stock-topic a {{
    color: rgba(0,255,204,0.6);
    text-decoration: none;
    transition: color 0.3s;
    display: inline-block;
    animation: marquee 25s linear infinite;
    padding-left: 100%;
}}
.stock-topic:nth-child(2) a {{ animation-delay: -3s; }}
.stock-topic:nth-child(3) a {{ animation-delay: -6s; }}
.stock-topic:nth-child(4) a {{ animation-delay: -9s; }}
.stock-topic a:hover {{
    color: #00ffcc;
    animation-play-state: paused;
}}
@keyframes marquee {{
    0%   {{ transform: translateX(0); }}
    100% {{ transform: translateX(-200%); }}
}}

/* ── Quick links ── */
.quick-links {{
    display: flex; gap: 6px; margin-bottom: 14px;
}}
.quick-link {{
    font-family: 'Orbitron', monospace;
    font-size: 0.5rem; letter-spacing: 2px;
    padding: 5px 12px;
    border: 1px solid rgba(0,255,204,0.35);
    border-radius: 3px;
    color: #00ffcc;
    text-decoration: none;
    transition: all 0.3s;
    text-shadow: 0 0 6px rgba(0,255,204,0.2);
}}
.quick-link:hover {{
    color: #fff;
    border-color: rgba(0,255,204,0.7);
    background: rgba(0,255,204,0.1);
    text-shadow: 0 0 12px rgba(0,255,204,0.5);
}}

/* ── Weather Widget ── */
.weather-widget {{
    margin-top: 20px;
    padding: 16px;
    background: rgba(0,12,24,0.6);
    border: 1px solid rgba(0,255,204,0.2);
    border-radius: 4px;
    box-shadow: 0 0 15px rgba(0,255,204,0.05);
}}
.weather-header {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-bottom: 12px;
}}
.weather-icon {{
    font-size: 2rem;
    filter: drop-shadow(0 0 8px rgba(0,255,204,0.3));
}}
.weather-location {{
    font-family: 'Orbitron', monospace;
    font-size: 0.6rem;
    letter-spacing: 3px;
    color: rgba(0,255,204,0.9);
    text-shadow: 0 0 8px rgba(0,255,204,0.3);
}}
.weather-temp {{
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: rgba(0,255,204,1);
    text-align: center;
    text-shadow: 0 0 15px rgba(0,255,204,0.5);
    margin-bottom: 12px;
}}
.weather-details {{
    border-top: 1px solid rgba(0,255,204,0.15);
    padding-top: 10px;
}}
.weather-detail {{
    font-family: monospace;
    font-size: 0.55rem;
    color: rgba(0,255,204,0.7);
    margin-bottom: 4px;
    letter-spacing: 1px;
}}
.weather-condition {{
    font-family: monospace;
    font-size: 0.6rem;
    color: rgba(0,255,204,0.5);
    text-align: center;
    margin-top: 8px;
    font-style: italic;
}}

/* ── News items ── */
.news-item {{
    padding: 10px 0;
    border-bottom: 1px solid rgba(0,255,204,0.05);
}}
.news-idx {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem; color: rgba(0,255,204,0.35);
    letter-spacing: 2px; margin-bottom: 3px;
}}
.news-title {{
    font-size: 0.8rem; color: #00ffcc;
    line-height: 1.6;
    text-shadow: 0 0 8px rgba(0,255,204,0.2);
}}
.news-title a {{ color: #00ffcc; text-decoration: none; transition: all 0.3s; }}
.news-title a:hover {{ color: #fff; text-shadow: 0 0 15px rgba(0,255,204,0.6); }}
.news-date {{
    font-size: 0.5rem; color: rgba(0,255,204,0.3);
    margin-top: 3px;
}}

/* ── Bottom bar ── */
.hud-bottom {{
    position: absolute; bottom: 0; left: 0; right: 0;
    height: 32px; z-index: 20;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(0deg, rgba(0,8,18,0.95) 0%, transparent 100%);
}}
.hud-bottom-text {{
    font-size: 0.45rem; letter-spacing: 4px;
    color: rgba(0,255,204,0.18);
}}

/* Pulse dot */
.pulse-dot {{
    width: 5px; height: 5px;
    background: #00ffcc; border-radius: 50%;
    display: inline-block; margin-right: 5px;
    vertical-align: middle;
    animation: pulse 2s ease-in-out infinite;
    box-shadow: 0 0 5px #00ffcc;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.2; }}
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
}}
.boot-splash.hide {{
    opacity: 0;
    pointer-events: none;
}}
.boot-splash img {{
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
    animation: bootFadeIn 0.8s ease-out;
}}
.boot-hint {{
    position: fixed;
    bottom: 22vh;
    left: 50%;
    transform: translateX(calc(-50% + 0.5em));
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 4px;
    color: rgba(0,255,204,0.9);
    text-shadow: 0 0 15px rgba(0,255,204,0.5);
    animation: pulseHint 2s ease-in-out infinite;
    z-index: 999999;
}}
/* システムブート表示 */
.boot-system {{
    position: fixed;
    top: 5vh;
    left: 5vw;
    z-index: 999999;
    font-family: 'Share Tech Mono', monospace;
    color: rgba(0,255,204,0.9);
}}
.boot-messages {{
    margin-bottom: 15px;
    min-height: 80px;
}}
.boot-message {{
    font-size: 0.7rem;
    line-height: 1.6;
    color: rgba(0,255,204,0.85);
    text-shadow: 0 0 8px rgba(0,255,204,0.3);
    margin-bottom: 4px;
    animation: bootTextAppear 0.3s ease-out;
}}
.boot-message.success {{
    color: rgba(0,255,204,1);
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
    gap: 12px;
}}
.progress-bar-container {{
    width: 250px;
    height: 12px;
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
    font-size: 0.75rem;
    font-weight: 700;
    color: rgba(0,255,204,1);
    text-shadow: 0 0 10px rgba(0,255,204,0.5);
    min-width: 40px;
}}
@keyframes bootFadeIn {{
    from {{ opacity: 0; transform: scale(0.95); }}
    to {{ opacity: 1; transform: scale(1); }}
}}
@keyframes pulseHint {{
    0%, 100% {{ opacity: 0.5; }}
    50% {{ opacity: 1; }}
}}
</style>
</head>
<body>
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
    <div class="boot-hint" id="bootHint" style="display:none;">CLICK TO START</div>
</div>

<div class="viewport">
    <div class="alert-overlay {alert_active}"></div>
    {"<img src='" + back_logo_img + "' class='bg-logo' alt='Background Logo'>" if back_logo_img else ""}
    <div class="map-container">
        {map_img}
        <div class="map-arrow arrow-top"></div>
        <div class="map-arrow arrow-bottom"></div>
        <div class="map-arrow arrow-left"></div>
        <div class="map-arrow arrow-right"></div>
        <div class="map-ping-red"></div>
        <div class="map-ping-green"></div>
    </div>

    <div class="hud-header">
        {header_frame}
        <div class="hud-status" onclick="returnToBootScreen()" style="cursor:pointer;"><span class="pulse-dot"></span>SYSTEM ONLINE</div>
        <div class="hud-clock" id="liveClock">{now}</div>
    </div>

    {ai_html}

    <div class="insight-matcher" id="insightMatcher">
        <div class="matcher-title" onclick="toggleMatcher()" style="cursor:pointer;">
            INSIGHT MATCHER // KDDI x FUJITSU
            <span class="matcher-toggle" id="matcherToggle">▶</span>
        </div>
        <div class="matcher-body collapsed" id="matcherBody">
            {matcher_rows}
        </div>
    </div>

    <div class="panel left">
        <div class="panel-inner">
            <div class="panel-title">STOCK MONITOR</div>
            {stock_html}
            <div style="margin-top:12px;font-size:0.6rem;color:rgba(0,255,204,0.55);letter-spacing:2px;">
                <span class="pulse-dot"></span>LIVE FEED // TYO-JPX
            </div>
            <button class="hypothesis-btn" onclick="triggerHypothesisGeneration()">&#9654; GENERATE HYPOTHESIS</button>
        </div>
    </div>

    <div class="panel right">
        <div class="panel-inner">
            <div class="panel-title-row">
                <div class="panel-title" id="buPanelTitle" style="color:#ffaa00;">TRENDING TOPICS</div>
                <button class="bu-toggle-btn" onclick="toggleBU()">⇄ SWITCH</button>
            </div>
            <div id="newsPanel" class="bu-content active">
                <div class="quick-links" style="margin-bottom:14px;">
                    <a href="https://www.nikkei.com/" target="_blank" class="quick-link">NIKKEI</a>
                    <a href="https://newspicks.com/search/?membership=member&nameVerified=false&q=KDDI&subscriptionPlan=paid&t=top&pick=none&articleType=all&published=none&from=&to=&sortOrder=recommended" target="_blank" class="quick-link">NEWSPICKS</a>
                </div>
                {news_html}
            </div>
            <div id="pressPanel" class="bu-content">
                <div class="quick-links" style="margin-bottom:14px;">
                    <a href="https://newsroom.kddi.com/" target="_blank" class="quick-link">KDDI NEWSROOM</a>
                </div>
                {press_html}
            </div>
            <div id="fujitsuPressPanel" class="bu-content">
                <div class="quick-links" style="margin-bottom:14px;">
                    <a href="https://global.fujitsu/ja-jp/pr" target="_blank" class="quick-link">FUJITSU PR</a>
                    <a href="https://global.fujitsu/ja-jp/uvance" target="_blank" class="quick-link">UVANCE</a>
                </div>
                {fujitsu_press_html}
            </div>
            <div id="wakonxPanel" class="bu-content">
                {wakonx_html}
            </div>
            <div id="bxPanel" class="bu-content">
                {bx_html}
            </div>
        </div>
    </div>

    <div class="hud-bottom">
        <div class="hud-bottom-text">FUJITSU // ACCOUNT INTELLIGENCE DIVISION // KDDI SECTOR WATCH // CLASSIFIED</div>
    </div>
</div>

<script>
// Context Library Data
var CONTEXT_DATA = `{get_active_context_data()}`;

setInterval(function(){{
    var d=new Date();
    var days=['SUN','MON','TUE','WED','THU','FRI','SAT'];
    var s=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')+' ('+days[d.getDay()]+') '+String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0')+':'+String(d.getSeconds()).padStart(2,'0');
    document.getElementById('liveClock').textContent=s;
}},1000);
function triggerHypothesisGeneration(){{
    try {{
        var url = new URL(window.parent.location.href);
        url.searchParams.set('hypothesis_trigger', 'auto');
        window.parent.location.href = url.toString();
    }} catch(e) {{
        alert('ダッシュボード外からは実行できません。Streamlitページで操作してください。');
    }}
}}
function toggleStockExpand(){{
    var sec = document.getElementById('stockSecondary');
    var btn = document.getElementById('stockToggleBtn');
    if (sec && btn) {{
        sec.classList.toggle('collapsed');
        btn.textContent = sec.classList.contains('collapsed') ? 'SHOW ALL (5)' : 'SHOW LESS (2)';
    }}
}}
function toggleAiPanel(){{
    var body = document.getElementById('aiBody');
    var toggle = document.getElementById('aiToggle');
    if (body && toggle) {{
        body.classList.toggle('collapsed');
        toggle.innerHTML = body.classList.contains('collapsed') ? '&#9654;' : '&#9660;';
    }}
}}
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
function showReport(idx){{
    document.getElementById('reportOverlay'+idx).style.display='flex';
}}
function closeReport(idx){{
    document.getElementById('reportOverlay'+idx).style.display='none';
}}
function showApproachPlan(idx){{
    document.getElementById('approachOverlay'+idx).style.display='flex';
}}
function closeApproachPlan(idx){{
    document.getElementById('approachOverlay'+idx).style.display='none';
}}
function addToAsana(idx, title, uvance, score){{
    // 上下両方のボタンを更新
    var btnTop = document.getElementById('asanaBtnTop'+idx);
    var btnBottom = document.getElementById('asanaBtn'+idx);
    var btns = [btnTop, btnBottom].filter(function(b){{ return b; }});
    btns.forEach(function(b){{
        b.textContent = 'SENDING...';
        b.disabled = true;
        b.style.opacity = '0.5';
    }});
    var overlay = document.getElementById('reportOverlay'+idx);
    var bodyEl = overlay.querySelector('.report-overlay-body');
    var reportText = bodyEl ? bodyEl.innerText : '';
    var scoreReason = '';
    var reasonEl = overlay.querySelector('.overlay-score-reason');
    if(reasonEl) scoreReason = reasonEl.innerText;
    var payload = {{
        title: '[KDDI Strategy] ' + title,
        score: score,
        score_reason: scoreReason,
        uvance_area: uvance,
        report_body: reportText,
        source: 'Strategic Dashboard',
        timestamp: new Date().toISOString()
    }};
    fetch('https://hooks.zapier.com/hooks/catch/23986512/uejj8dt/', {{
        method: 'POST',
        body: JSON.stringify(payload),
        mode: 'no-cors'
    }}).then(function(){{
        btns.forEach(function(b){{
            b.textContent = '\\u2705 ADDED TO ASANA';
            b.style.background = 'rgba(0,255,100,0.15)';
            b.style.borderColor = 'rgba(0,255,100,0.4)';
            b.style.color = 'rgba(0,255,100,0.9)';
        }});
    }}).catch(function(){{
        btns.forEach(function(b){{
            b.textContent = '\\u26A0 FAILED - RETRY';
            b.disabled = false;
            b.style.opacity = '1';
        }});
    }});
}}
function saveReport(idx, title){{
    var overlay = document.getElementById('reportOverlay'+idx);
    var inner = overlay.querySelector('.report-overlay-inner');
    var now = new Date();
    var dateStr = now.getFullYear() + String(now.getMonth()+1).padStart(2,'0') + String(now.getDate()).padStart(2,'0');
    var timeStr = String(now.getHours()).padStart(2,'0') + String(now.getMinutes()).padStart(2,'0');
    var html = '<!DOCTYPE html><html><head><meta charset="utf-8">'
        + '<title>Strategic Report - ' + title + '</title>'
        + '<style>'
        + "@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');"
        + '* {{ margin:0; padding:0; box-sizing:border-box; }}'
        + 'html,body {{ background:#000; color:#c8aaff; font-family:"Share Tech Mono",monospace; min-height:100vh; }}'
        + '.report-overlay-inner {{ max-width:900px; margin:0 auto; padding:30px; }}'
        + '.report-overlay-header {{ text-align:center; margin-bottom:30px; padding-bottom:16px; border-bottom:1px solid rgba(180,120,255,0.15); }}'
        + '.report-overlay-label {{ font-family:"Orbitron",monospace; font-size:0.55rem; letter-spacing:6px; color:rgba(180,120,255,0.4); margin-bottom:10px; }}'
        + '.report-overlay-title {{ font-family:"Orbitron",monospace; font-size:1.3rem; font-weight:900; color:rgba(180,120,255,0.9); letter-spacing:2px; text-shadow:0 0 20px rgba(180,120,255,0.3); line-height:1.6; }}'
        + '.overlay-score-box {{ margin:16px 0; }}'
        + '.overlay-score-num {{ font-family:"Orbitron",monospace; font-size:2rem; font-weight:900; }}'
        + '.overlay-score-high {{ color:#00ff88; text-shadow:0 0 20px rgba(0,255,136,0.4); }}'
        + '.overlay-score-mid {{ color:#ffaa00; text-shadow:0 0 20px rgba(255,170,0,0.4); }}'
        + '.overlay-score-low {{ color:rgba(180,120,255,0.4); }}'
        + '.overlay-score-label {{ display:block; font-family:"Orbitron",monospace; font-size:0.4rem; letter-spacing:4px; color:rgba(180,120,255,0.4); margin-top:4px; }}'
        + '.overlay-score-reason {{ display:block; font-size:0.7rem; color:rgba(200,170,255,0.6); margin-top:6px; }}'
        + '.report-overlay-actions {{ display:none; }}'
        + '.report-close-btn-top {{ display:none; }}'
        + '.report-section {{ margin-bottom:28px; padding:16px 20px; border:1px solid rgba(180,120,255,0.08); border-radius:6px; background:rgba(10,5,20,0.6); }}'
        + '.section-header {{ font-family:"Orbitron",monospace; font-size:0.85rem; font-weight:700; color:rgba(180,120,255,0.9); letter-spacing:3px; margin-bottom:14px; padding-bottom:10px; border-bottom:1px solid rgba(180,120,255,0.15); }}'
        + '.section-body {{ font-size:0.95rem; line-height:2.2; color:rgba(220,200,255,0.85); }}'
        + '.section-uvance {{ border-color:rgba(0,180,255,0.2); background:rgba(0,20,40,0.6); }}'
        + '.section-uvance .section-header {{ color:rgba(0,200,255,0.9); border-bottom-color:rgba(0,180,255,0.2); }}'
        + '.sub-heading {{ color:rgba(0,200,255,0.9); font-weight:700; }}'
        + '.report-overlay-footer {{ text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid rgba(180,120,255,0.08); font-family:"Orbitron",monospace; font-size:0.4rem; color:rgba(180,120,255,0.2); letter-spacing:4px; }}'
        + '</style></head><body>'
        + inner.innerHTML
        + '</body></html>';
    var blob = new Blob([html], {{type: 'text/html;charset=utf-8'}});
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    var safeTitle = title.replace(/[^a-zA-Z0-9\\u3000-\\u9FFF]/g, '_').substring(0, 40);
    a.download = 'Report_' + dateStr + '_' + timeStr + '_' + safeTitle + '.html';
    a.click();
    URL.revokeObjectURL(a.href);
}}
function generateProposal(idx, title){{
    var btn = document.getElementById('proposalBtn'+idx);
    var btnTop = document.getElementById('proposalBtnTop'+idx);
    [btn, btnTop].forEach(function(b) {{
        if (b) {{ b.textContent = 'GENERATING...'; b.disabled = true; b.style.opacity = '0.5'; }}
    }});
    var overlay = document.getElementById('reportOverlay'+idx);
    var bodyEl = overlay.querySelector('.report-overlay-body');
    var reportText = bodyEl ? bodyEl.innerText.substring(0, 5000) : '';

    // Streamlit query param方式でトリガー
    // セッションストレージに保存し、親Streamlitに通知
    try {{
        var proposalData = JSON.stringify({{
            action: 'generate_hypothesis',
            opportunity_title: title,
            report_content: reportText,
            timestamp: Date.now()
        }});
        // Streamlit parent window に通知
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            data: proposalData
        }}, '*');

        // URLパラメータ方式でもフォールバック
        var url = new URL(window.parent.location.href);
        url.searchParams.set('hypothesis_trigger', encodeURIComponent(title));
        window.parent.location.href = url.toString();
    }} catch(e) {{
        // フォールバック: クリップボードにコピーして手動指示
        var proposalPrompt = '# 仮説提案書生成リクエスト\\n\\n'
            + '## オポチュニティ: ' + title + '\\n\\n'
            + '## レポート内容:\\n' + reportText + '\\n\\n'
            + 'ダッシュボードの「GENERATE HYPOTHESIS」ボタンをクリックしてください。';
        navigator.clipboard.writeText(proposalPrompt).then(function() {{
            alert('提案情報をクリップボードにコピーしました。\\n\\nダッシュボード下部の「▶ GENERATE HYPOTHESIS」ボタンをクリックして提案書を生成してください。');
        }}).catch(function() {{
            alert('ダッシュボード下部の「▶ GENERATE HYPOTHESIS」ボタンをクリックして提案書を生成してください。');
        }});
    }}

    setTimeout(function() {{
        [btn, btnTop].forEach(function(b) {{
            if (b) {{ b.textContent = '📝 CREATE PROPOSAL'; b.disabled = false; b.style.opacity = '1'; }}
        }});
    }}, 3000);
}}
function sendToGemini(idx){{
    var overlay = document.getElementById('reportOverlay'+idx);
    var titleEl = overlay.querySelector('.report-title');
    var bodyEl = overlay.querySelector('.report-overlay-body');
    var title = titleEl ? titleEl.innerText : '';
    var reportText = bodyEl ? bodyEl.innerText : '';

    var contextSection = CONTEXT_DATA ? `\\n# 追加コンテキスト情報（決算データ・統合レポート等）\\n${{CONTEXT_DATA}}\\n` : '';

    var geminiPrompt = `# 企業調査レポート
${{title}}

${{reportText}}

# 自社ソリューション情報
富士通Uvance（Digital Shifts, Hybrid IT, Healthy Living等）
- Kozuchi AI Platform（生成AI・機械学習）
- Data e-TRUST / Palantir連携（データ利活用）
- プライベート5Gソリューション
- ゼロトラストセキュリティ
- Hybrid IT基盤構築
- DX推進コンサルティング
- 共創プログラム
${{contextSection}}
上記の情報をもとに、KDDI（WAKONX/KDDI BX）向けの提案書骨子を作成してください。`;

    // Copy to clipboard
    navigator.clipboard.writeText(geminiPrompt).then(function(){{
        var btn = document.getElementById('geminiBtn'+idx);
        btn.textContent = '✅ COPIED!';
        setTimeout(function(){{
            btn.textContent = '🎙 SEND TO GEMINI';
        }}, 2000);

        // Open Gemini Gem directly
        window.open('https://gemini.google.com/gem/23bec0ec97ef', '_blank');

        alert('レポート内容をクリップボードにコピーしました！\\n\\n新しいタブでGemini が開きます。\\nGemsにペーストしてご利用ください。');
    }}).catch(function(err){{
        alert('クリップボードへのコピーに失敗しました: ' + err);
    }});
}}

// ── Boot Splash Screen Control (Click to Continue) ──
(function() {{
    console.log('[BOOT] Initializing boot splash...');
    var splash = document.getElementById('bootSplash');
    if (!splash) {{
        console.log('[BOOT] ERROR: Splash element not found');
        return;
    }}
    console.log('[BOOT] Splash element found');

    // セッションストレージで1セッションに1回のみ表示
    var hasShown = sessionStorage.getItem('boot_splash_shown');
    if (hasShown) {{
        console.log('[BOOT] Already shown in this session, skipping');
        splash.remove();
        return;
    }}
    console.log('[BOOT] First time in session, showing splash (click to continue)');

    // クリックで非表示にする
    function hideSplash() {{
        console.log('[BOOT] Hiding splash...');
        splash.classList.add('hide');
        setTimeout(function() {{
            console.log('[BOOT] Removing splash element');
            splash.remove();
        }}, 800); // フェードアウト時間
        sessionStorage.setItem('boot_splash_shown', 'true');
    }}

    // システムブートシーケンス
    var bootMessages = [
        {{ text: '> INITIALIZING ACCOUNT INTELLIGENCE MONITOR...', delay: 0 }},
        {{ text: '> LOADING AI MODULES.................. <span class="status-ok">[OK]</span>', delay: 600 }},
        {{ text: '> CONNECTING TO DATA SOURCES.......... <span class="status-ok">[OK]</span>', delay: 1200 }},
        {{ text: '> ESTABLISHING SECURE CONNECTION...... <span class="status-ok">[OK]</span>', delay: 1800 }},
        {{ text: '> SYSTEM READY', delay: 2400 }}
    ];

    var messagesContainer = document.getElementById('bootMessages');
    var progressFill = document.getElementById('progressBarFill');
    var progressPercent = document.getElementById('progressPercent');
    var bootHint = document.getElementById('bootHint');

    // メッセージを順次表示
    bootMessages.forEach(function(msg) {{
        setTimeout(function() {{
            var msgDiv = document.createElement('div');
            msgDiv.className = 'boot-message';
            msgDiv.innerHTML = msg.text;
            messagesContainer.appendChild(msgDiv);
        }}, msg.delay);
    }});

    // プログレスバーアニメーション
    var progress = 0;
    var progressInterval = setInterval(function() {{
        progress += 3;
        if (progress > 100) {{
            progress = 100;
            clearInterval(progressInterval);
            // 完了後に「CLICK TO START」表示
            setTimeout(function() {{
                bootHint.style.display = 'block';
            }}, 300);
        }}
        progressFill.style.width = progress + '%';
        progressPercent.textContent = progress + '%';
    }}, 80);

    // スプラッシュ画面のどこかをクリックしたら非表示
    splash.addEventListener('click', function() {{
        console.log('[BOOT] Splash clicked, hiding...');
        hideSplash();
    }});

    // マウスカーソルをポインターに変更してクリック可能であることを示す
    splash.style.cursor = 'pointer';
}})();

// スリープボタン機能：オープニング画面に戻る
function returnToBootScreen() {{
    sessionStorage.removeItem('boot_splash_shown');
    location.reload();
}}

// INSIGHT MATCHER トグル機能
function toggleMatcher() {{
    var body = document.getElementById('matcherBody');
    var toggle = document.getElementById('matcherToggle');
    if (body && toggle) {{
        body.classList.toggle('collapsed');
        toggle.textContent = body.classList.contains('collapsed') ? '▶' : '▼';
    }}
}}

// AIスコア理由説明の表示/非表示
function toggleExplanation(index) {{
    var explanation = document.getElementById('explanation' + index);
    if (explanation) {{
        if (explanation.style.display === 'none' || explanation.style.display === '') {{
            explanation.style.display = 'block';
        }} else {{
            explanation.style.display = 'none';
        }}
    }}
}}

// Streamlit実行中検知 - ローディングオーバーレイ表示
(function() {{
    var observer = new MutationObserver(function(mutations) {{
        var stApp = document.querySelector('.stApp');
        var statusLabel = document.querySelector('[data-testid="stStatusWidget"]');

        if (stApp) {{
            // Streamlitが実行中かチェック（"Running..."が表示されているか）
            if (statusLabel && statusLabel.textContent.includes('Running')) {{
                stApp.classList.add('streamlit-running');
            }} else {{
                stApp.classList.remove('streamlit-running');
            }}
        }}
    }});

    // DOM全体を監視
    observer.observe(document.body, {{
        childList: true,
        subtree: true,
        attributes: true,
        characterData: true
    }});
}})();
</script>
</body></html>"""



