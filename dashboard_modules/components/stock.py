"""
Stock data fetching and chart generation
"""
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=300)
def fetch_stock(ticker: str, days: int = 7):
    """株価の直近N日分の日付・終値・前日比を取得"""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period="1mo")
        if hist.empty or len(hist) < 2:
            return None, None, None, [], []
        hist = hist.tail(days)
        latest = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])
        diff = latest - prev
        pct = (diff / prev) * 100
        dates = [d.strftime("%m/%d") for d in hist.index]
        closes = [float(c) for c in hist["Close"].tolist()]
        return latest, diff, pct, dates, closes
    except Exception:
        return None, None, None, [], []


def build_svg_chart(dates: list[str], closes: list[float],
                    color: str = "#00ffcc", width: int = 280, height: int = 80) -> str:
    """SVGチャート生成"""
    if not closes or len(closes) < 2:
        return '<div style="color:rgba(0,255,204,0.2);font-size:0.7rem;">NO DATA</div>'
    mn, mx = min(closes), max(closes)
    rng = mx - mn if mx != mn else 1
    pad = 8
    cw = width - pad * 2
    ch = height - pad * 2
    points = []
    for i, v in enumerate(closes):
        x = pad + (i / (len(closes) - 1)) * cw
        y = pad + ch - ((v - mn) / rng) * ch
        points.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(points)
    # fill area
    fill_points = f"{pad:.1f},{height - pad:.1f} " + polyline + f" {width - pad:.1f},{height - pad:.1f}"
    # date labels
    labels = ""
    for i, d in enumerate(dates):
        if i == 0 or i == len(dates) - 1 or i == len(dates) // 2:
            x = pad + (i / (len(dates) - 1)) * cw
            labels += f'<text x="{x:.1f}" y="{height - 1}" fill="rgba(0,255,204,0.3)" font-size="7" text-anchor="middle">{d}</text>'
    return f"""<svg width="{width}" height="{height}" style="display:block;margin-top:6px;">
        <polygon points="{fill_points}" fill="url(#chartGrad{color.replace('#','')})" />
        <polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round"/>
        <defs><linearGradient id="chartGrad{color.replace('#','')}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="{color}" stop-opacity="0.02"/>
        </linearGradient></defs>
        {labels}
    </svg>"""
