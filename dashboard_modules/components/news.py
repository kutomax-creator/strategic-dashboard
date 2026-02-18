"""
News fetching from Google News RSS
"""
import streamlit as st
import feedparser


@st.cache_data(ttl=300)
def fetch_news_for(query: str, n: int = 4) -> list[dict]:
    """Google News RSSから指定キーワードのニュースを取得"""
    # 期間フィルターは削除（Google News RSSで正常に動作しないため）
    url = f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"
    articles = []
    try:
        feed = feedparser.parse(url)
        seen = set()
        for entry in feed.entries:
            if entry.title not in seen:
                seen.add(entry.title)
                articles.append({
                    "title": entry.title,
                    "link": entry.get("link", "#"),
                    "published": entry.get("published", ""),
                })
    except Exception:
        pass
    return articles[:n]


@st.cache_data(ttl=600)
def fetch_kddi_press_releases(n: int = 8) -> list[dict]:
    """KDDI公式プレスリリースRSSから取得"""
    url = "https://newsroom.kddi.com/news/newsrelease.xml"
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:n]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", "#"),
                "published": entry.get("published", ""),
                "description": entry.get("description", ""),
            })
    except Exception:
        pass
    return articles


@st.cache_data(ttl=600)
def fetch_fujitsu_press_releases(n: int = 8) -> list[dict]:
    """富士通プレスリリースをPR TIMES RSSから取得"""
    url = "https://prtimes.jp/companyrdf.php?company_id=93942"
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:n]:
            title = entry.get("title", "")
            articles.append({
                "title": title,
                "link": entry.get("link", "#"),
                "published": entry.get("dc_date", entry.get("published", "")),
                "is_uvance": "uvance" in title.lower() or "Uvance" in title,
            })
    except Exception:
        pass
    return articles
