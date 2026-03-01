"""
BU Intelligence - WAKONX/KDDI BX keywords mapping
"""
import streamlit as st
from ..components.news import fetch_news_for

# ─── WAKONX/KDDI BX Intelligence Hub ─────────────────────────────
# WAKONX/KDDI BX 注目キーワード → Uvance マッピング
WAKONX_KEYWORDS = {
    "WAKONX": {"uvance": "Digital Shifts", "action": "WAKONX連携DXソリューション提案", "priority": "HIGH"},
    "DX": {"uvance": "Digital Shifts", "action": "DX推進支援・Kozuchi AI連携提案", "priority": "HIGH"},
    "AI": {"uvance": "Digital Shifts", "action": "Kozuchi AI Platform連携提案", "priority": "HIGH"},
    "生成AI": {"uvance": "Digital Shifts", "action": "生成AI共同開発・PoC提案", "priority": "HIGH"},
    "クラウド": {"uvance": "Hybrid IT", "action": "Hybrid IT基盤構築支援", "priority": "MEDIUM"},
    "IoT": {"uvance": "Digital Shifts", "action": "IoT×AI統合ソリューション提案", "priority": "MEDIUM"},
    "データ活用": {"uvance": "Digital Shifts", "action": "Data e-TRUST活用提案", "priority": "HIGH"},
    "セキュリティ": {"uvance": "Digital Shifts", "action": "ゼロトラスト統合提案", "priority": "MEDIUM"},
    "エッジ": {"uvance": "Hybrid IT", "action": "5Gエッジコンピューティング提案", "priority": "HIGH"},
    "ゼロトラスト": {"uvance": "Hybrid IT", "action": "ゼロトラストセキュリティ提案", "priority": "HIGH"},
    "メタバース": {"uvance": "Trusted Society", "action": "XR×5Gプラットフォーム提案", "priority": "MEDIUM"},
}

BX_KEYWORDS = {
    "BX": {"uvance": "Digital Shifts", "action": "ビジネス変革コンサル提案", "priority": "HIGH"},
    "事業変革": {"uvance": "Digital Shifts", "action": "事業変革支援・PMO提案", "priority": "HIGH"},
    "共創": {"uvance": "Digital Shifts", "action": "Uvance共創プログラム提案", "priority": "HIGH"},
    "イノベーション": {"uvance": "Digital Shifts", "action": "共創ワークショップ提案", "priority": "MEDIUM"},
    "新規事業": {"uvance": "Digital Shifts", "action": "新規事業立上げ支援提案", "priority": "HIGH"},
    "デジタル": {"uvance": "Digital Shifts", "action": "デジタルビジネス構築支援", "priority": "MEDIUM"},
    "パートナー": {"uvance": "Digital Shifts", "action": "パートナーシップ提案", "priority": "MEDIUM"},
    "ヘルスケア": {"uvance": "Healthy Living", "action": "遠隔医療・健康経営DX提案", "priority": "HIGH"},
    "医療": {"uvance": "Healthy Living", "action": "医療DX基盤提案", "priority": "MEDIUM"},
    "スマートシティ": {"uvance": "Trusted Society", "action": "デジタルツイン都市提案", "priority": "HIGH"},
    "防災": {"uvance": "Trusted Society", "action": "防災DX基盤提案", "priority": "MEDIUM"},
    "自治体": {"uvance": "Trusted Society", "action": "行政DX支援提案", "priority": "MEDIUM"},
    "カーボン": {"uvance": "Digital Shifts", "action": "CO2可視化・GX推進提案", "priority": "HIGH"},
    "ESG": {"uvance": "Digital Shifts", "action": "ESGデータ基盤提案", "priority": "HIGH"},
    "SAP": {"uvance": "Digital Shifts", "action": "基幹システム刷新提案", "priority": "HIGH"},
    "ERP": {"uvance": "Digital Shifts", "action": "ERP移行支援提案", "priority": "MEDIUM"},
}


@st.cache_data(ttl=300)
def fetch_bu_intelligence(bu_name: str, keywords: dict) -> dict:
    """WAKONX/KDDI BX専用のインテリジェンス収集"""
    # ニュース取得（BU名でフィルタ）
    query = f"KDDI+{bu_name}"
    articles = fetch_news_for(query, 8)

    # キーワードマッチング
    matches = []
    seen_uvance = set()
    total_priority_score = 0

    for article in articles:
        title = article["title"]
        for keyword, info in keywords.items():
            if keyword in title:
                priority_weight = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(info["priority"], 1)
                total_priority_score += priority_weight

                if info["uvance"] not in seen_uvance:
                    seen_uvance.add(info["uvance"])
                    matches.append({
                        "keyword": keyword,
                        "title": title,
                        "uvance": info["uvance"],
                        "action": info["action"],
                        "priority": info["priority"],
                        "link": article["link"],
                    })

    # 機会スコア算出 (0-100)
    opportunity_score = min(100, (total_priority_score / max(len(articles), 1)) * 25)

    return {
        "articles": articles[:5],  # 最新5件
        "matches": matches[:3],     # トップ3マッチ
        "opportunity_score": round(opportunity_score, 1),
        "keyword_hits": len(matches),
    }


