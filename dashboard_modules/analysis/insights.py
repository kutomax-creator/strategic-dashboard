"""
Insight Matcher - AI-powered news analysis and solution mapping
"""
from __future__ import annotations

import re
import streamlit as st
from ..config import HAS_AI
from ..ai_client import chat_completion
from ..components.news import fetch_news_for

# ─── Insight Matcher ──────────────────────────────────────────────
# キーワード → 富士通ソリューション マッピング
SOLUTION_MAP = {
    # AI / データ
    "AI": {"solution": "Kozuchi AI Platform", "action": "AI業務適用PoCを提案", "url": "https://www.fujitsu.com/jp/services/kozuchi/"},
    "生成AI": {"solution": "Kozuchi AI Platform", "action": "生成AI業務適用PoCを提案", "url": "https://www.fujitsu.com/jp/services/kozuchi/"},
    "LLM": {"solution": "Kozuchi AI Platform", "action": "LLM導入支援を提案", "url": "https://www.fujitsu.com/jp/services/kozuchi/"},
    "機械学習": {"solution": "Kozuchi AI Platform", "action": "ML基盤構築を提案", "url": "https://www.fujitsu.com/jp/services/kozuchi/"},
    "データ": {"solution": "Data e-TRUST / Palantir連携", "action": "データ利活用基盤を提案", "url": "https://www.fujitsu.com/jp/uvance/"},
    "DX": {"solution": "Uvance: Digital Shifts", "action": "DX推進コンサルを提案", "url": "https://www.fujitsu.com/jp/uvance/digital-shifts/"},
    "デジタル": {"solution": "Uvance: Digital Shifts", "action": "デジタル変革支援を提案", "url": "https://www.fujitsu.com/jp/uvance/digital-shifts/"},
    # インフラ / ネットワーク
    "5G": {"solution": "プライベート5Gソリューション", "action": "ローカル5G共同実証を提案", "url": "https://www.fujitsu.com/jp/solutions/network/"},
    "ネットワーク": {"solution": "Uvance: Digital Shifts", "action": "ネットワーク最適化を提案", "url": "https://www.fujitsu.com/jp/uvance/digital-shifts/"},
    "クラウド": {"solution": "Fujitsu Hybrid IT", "action": "マルチクラウド基盤を提案", "url": "https://www.fujitsu.com/jp/solutions/cloud/"},
    "通信": {"solution": "ネットワークソリューション", "action": "通信インフラ高度化を提案", "url": "https://www.fujitsu.com/jp/solutions/network/"},
    "IoT": {"solution": "Uvance: Business Applications", "action": "IoTプラットフォーム提案", "url": "https://www.fujitsu.com/jp/uvance/business-applications/"},
    # セキュリティ
    "セキュリティ": {"solution": "Uvance: Digital Shifts / ゼロトラスト", "action": "ゼロトラスト提案書を準備", "url": "https://www.fujitsu.com/jp/solutions/cyber-security/"},
    "サイバー": {"solution": "セキュリティオペレーション", "action": "SOC/CSIRT支援を提案", "url": "https://www.fujitsu.com/jp/solutions/cyber-security/"},
    "ランサム": {"solution": "セキュリティオペレーション", "action": "ランサムウェア対策を提案", "url": "https://www.fujitsu.com/jp/solutions/cyber-security/"},
    # まちづくり / 社会
    "スマートシティ": {"solution": "Uvance: Trusted Society", "action": "スマートシティ基盤提案書を持参", "url": "https://www.fujitsu.com/jp/uvance/trusted-society/"},
    "まちづくり": {"solution": "Uvance: Trusted Society", "action": "地域DX提案を準備", "url": "https://www.fujitsu.com/jp/uvance/trusted-society/"},
    "自治体": {"solution": "Uvance: Trusted Society", "action": "自治体DXソリューションを提案", "url": "https://www.fujitsu.com/jp/uvance/trusted-society/"},
    "MaaS": {"solution": "Uvance: Trusted Society", "action": "モビリティ基盤を提案", "url": "https://www.fujitsu.com/jp/uvance/trusted-society/"},
    "ドローン": {"solution": "Uvance: Business Applications", "action": "IoTプラットフォーム提案", "url": "https://www.fujitsu.com/jp/uvance/business-applications/"},
    "モビリティ": {"solution": "Uvance: Trusted Society", "action": "モビリティ基盤を提案", "url": "https://www.fujitsu.com/jp/uvance/trusted-society/"},
    # サステナビリティ
    "サステナ": {"solution": "Uvance: Healthy Living", "action": "カーボンニュートラル提案", "url": "https://www.fujitsu.com/jp/uvance/healthy-living/"},
    "カーボン": {"solution": "Uvance: Healthy Living", "action": "GX推進提案を準備", "url": "https://www.fujitsu.com/jp/uvance/healthy-living/"},
    "脱炭素": {"solution": "Uvance: Healthy Living", "action": "脱炭素ソリューション提案", "url": "https://www.fujitsu.com/jp/uvance/healthy-living/"},
    "ESG": {"solution": "Uvance: Healthy Living", "action": "ESG経営支援を提案", "url": "https://www.fujitsu.com/jp/uvance/healthy-living/"},
    "GX": {"solution": "Uvance: Healthy Living", "action": "GX推進提案を準備", "url": "https://www.fujitsu.com/jp/uvance/healthy-living/"},
    # 働き方 / 人材
    "人的資本": {"solution": "Work Life Shift 事例集", "action": "人的資本×DX事例を提案", "url": "https://www.fujitsu.com/jp/about/csr/worklifeshift/"},
    "働き方": {"solution": "Work Life Shift", "action": "働き方改革ソリューション提案", "url": "https://www.fujitsu.com/jp/about/csr/worklifeshift/"},
    "リスキリング": {"solution": "Uvance: Business Applications", "action": "人材育成DXを提案", "url": "https://www.fujitsu.com/jp/uvance/business-applications/"},
    "人材": {"solution": "Work Life Shift", "action": "HRテック提案を準備", "url": "https://www.fujitsu.com/jp/about/csr/worklifeshift/"},
    # 量子 / 先端技術
    "量子": {"solution": "量子シミュレータ CMOS", "action": "量子PoC共同提案を検討", "url": "https://www.fujitsu.com/jp/about/research/technology/quantum/"},
    "ブロックチェーン": {"solution": "Fujitsu Track and Trust", "action": "トレーサビリティ提案", "url": "https://www.fujitsu.com/jp/solutions/blockchain/"},
    "メタバース": {"solution": "Uvance: Business Applications", "action": "メタバース活用PoCを提案", "url": "https://www.fujitsu.com/jp/uvance/business-applications/"},
    "XR": {"solution": "Uvance: Business Applications", "action": "XR業務活用を提案", "url": "https://www.fujitsu.com/jp/uvance/business-applications/"},
    # 金融 / 決済
    "決済": {"solution": "Uvance: Digital Shifts", "action": "決済プラットフォーム提案", "url": "https://www.fujitsu.com/jp/uvance/digital-shifts/"},
    "フィンテック": {"solution": "Uvance: Digital Shifts", "action": "金融DXソリューション提案", "url": "https://www.fujitsu.com/jp/uvance/digital-shifts/"},
    "金融": {"solution": "金融ソリューション", "action": "金融DX提案を準備", "url": "https://www.fujitsu.com/jp/solutions/industry/financial-services/"},
    # その他ビジネス
    "共創": {"solution": "Uvance 共創プログラム", "action": "共創ビジネスワークショップを提案", "url": "https://www.fujitsu.com/jp/uvance/"},
    "共創ビジネス": {"solution": "Uvance 共創プログラム", "action": "KDDI共創テーマに合わせた提案を準備", "url": "https://www.fujitsu.com/jp/uvance/"},
    "提携": {"solution": "共創プログラム", "action": "共創ワークショップを提案", "url": "https://www.fujitsu.com/jp/uvance/"},
    "協業": {"solution": "共創プログラム", "action": "共創パートナーシップを提案", "url": "https://www.fujitsu.com/jp/uvance/"},
    "M&A": {"solution": "PMI支援コンサル", "action": "統合支援・IT基盤統合を提案", "url": "https://www.fujitsu.com/jp/services/consulting/"},
    "業績": {"solution": "経営ダッシュボード", "action": "経営可視化ソリューション提案", "url": "https://www.fujitsu.com/jp/services/consulting/"},
    "増収": {"solution": "ビジネスアナリティクス", "action": "成長戦略支援コンサルを提案", "url": "https://www.fujitsu.com/jp/services/consulting/"},
    "減益": {"solution": "コスト最適化コンサル", "action": "コスト削減ソリューション提案", "url": "https://www.fujitsu.com/jp/services/consulting/"},
}


@st.cache_data(ttl=600)
def ai_semantic_matching(kddi_articles: list[dict], fujitsu_articles: list[dict] = None) -> tuple[list[dict], float]:
    """AI駆動型双方向インテリジェンス - KDDI×富士通のクロスマッチング"""
    print(f"[AI MATCH] HAS_AI: {HAS_AI}, kddi_articles count: {len(kddi_articles) if kddi_articles else 0}")
    if not HAS_AI or not kddi_articles:
        print(f"[AI MATCH] Falling back to simple matching. HAS_AI={HAS_AI}, has_articles={bool(kddi_articles)}")
        return _simple_keyword_matching(kddi_articles if kddi_articles else [])

    try:
        # KDDIニュースをまとめる
        kddi_summary = "\n".join([f"K{i+1}. {a['title']}" for i, a in enumerate(kddi_articles[:10])])

        # 富士通ニュースを取得してまとめる
        if fujitsu_articles is None:
            fujitsu_articles = fetch_news_for("富士通+Uvance+OR+富士通+新製品+OR+富士通+DX+OR+富士通+AI", 10)

        fujitsu_summary = "\n".join([f"F{i+1}. {a['title']}" for i, a in enumerate(fujitsu_articles[:8])])

        response_text = chat_completion(
            messages=[{
                "role": "user",
                "content": f"""あなたは富士通のKDDIアカウントストラテジストです。KDDIと富士通の最新動向を分析し、**双方向のビジネス機会**を発見してください。

# KDDIニュース（直近）
{kddi_summary}

# 富士通ニュース・新製品リリース（直近）
{fujitsu_summary}

# 富士通Uvanceソリューション（参考）
- Digital Shifts: DX推進、業務改革、デジタル変革
- Kozuchi AI Platform: AI/ML基盤、生成AI、LLM
- Hybrid IT: マルチクラウド、仮想化、インフラ統合
- Sustainable Manufacturing: 製造DX、工場IoT、スマートファクトリー
- Business Applications: IoT、エッジコンピューティング、データ利活用
- Trusted Society: スマートシティ、MaaS、地域DX、自治体DX
- Healthy Living: カーボンニュートラル、ESG、サステナビリティ
- Cyber Security: ゼロトラスト、SOC/CSIRT、セキュリティ運用
- Consumer Experience: 顧客体験向上、デジタルマーケティング

# タスク（双方向分析）
1. **KDDI動向分析**: KDDIニュースから戦略意図・ニーズを推測
2. **富士通動向分析**: 富士通の新製品・ソリューションリリースを把握
3. **クロスマッチング**: 両者の時系列的な関連性を発見
   - 例: "KDDIが今週○○を発表 → 富士通は先月△△をリリース済み → 即提案可能"
   - 例: "富士通が新機能××を追加 → KDDIの□□戦略にマッチ → プロアクティブ提案"
4. **スコアリング**:
   - strategic_fit: 戦略適合度（0-100）
   - urgency: 緊急度（0-100）- タイミングの良さも考慮
   - revenue_potential: 商機規模（0-100）
   - confidence: 信頼度（0-100）

# 出力形式（JSON）
{{
  "matches": [
    {{
      "kddi_intent": "KDDIの戦略意図（30文字以内）",
      "kddi_news": "根拠となるKDDIニュース番号（例: K1,K3）",
      "fujitsu_news": "関連する富士通ニュース番号（例: F2）または「既存ソリューション」",
      "fujitsu_solution": "提案ソリューション（複数可）",
      "action": "提案アクション（40文字以内）",
      "strategic_fit": 85,
      "urgency": 70,
      "revenue_potential": 60,
      "confidence": 90,
      "timing_insight": "タイミング情報（例: KDDIが今週発表、富士通は先月リリース済み）",
      "reasoning": "双方向マッチの根拠（60文字以内）"
    }}
  ],
  "synergy_score": 75
}}

必ずJSON形式で返してください。"""
            }],
            max_tokens=4000,
            model="claude-haiku-4-5-20251001",
        )

        # JSONをパース
        import json
        import re
        # JSONを抽出（```json ... ``` がある場合）
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        # 不完全なJSONを修正（末尾のカンマや閉じ括弧の欠落を補完）
        response_text = response_text.strip()
        if not response_text.endswith('}'):
            # 最後の完全なオブジェクトまで切り詰める
            last_brace = response_text.rfind('}')
            if last_brace > 0:
                response_text = response_text[:last_brace + 1]

        result = json.loads(response_text)

        # マッチデータを整形
        matches = []
        for m in result.get("matches", [])[:4]:
            # kddi_newsから実際のニュースリンクを取得
            kddi_news_field = m.get("kddi_news", m.get("source_news", "K1"))
            kddi_indices = []
            for x in kddi_news_field.replace("K", "").split(","):
                if x.strip().isdigit():
                    kddi_indices.append(int(x.strip()) - 1)

            source_link = kddi_articles[kddi_indices[0]]["link"] if kddi_indices and kddi_indices[0] < len(kddi_articles) else kddi_articles[0]["link"]

            # 双方向インサイト情報
            timing_insight = m.get("timing_insight", "")
            fujitsu_news_ref = m.get("fujitsu_news", "")
            reasoning = m.get("reasoning", "")

            # ソース表示を強化
            source_display = f"[双方向分析] {reasoning}"
            if timing_insight:
                source_display = f"⏱ {timing_insight} | {reasoning}"

            matches.append({
                "kddi": m.get("kddi_intent", "戦略意図不明"),
                "source": source_display,
                "fujitsu": m.get("fujitsu_solution", "Digital Shifts"),
                "action": m.get("action", "詳細提案を準備"),
                "link": source_link,
                "fujitsu_url": "https://www.fujitsu.com/jp/uvance/",
                "confidence": m.get("confidence", 70),
                "strategic_fit": m.get("strategic_fit", 70),
                "urgency": m.get("urgency", 50),
                "revenue_potential": m.get("revenue_potential", 50),
                "fujitsu_news_ref": fujitsu_news_ref,
                "reasoning": reasoning,
                "timing_insight": timing_insight,
            })

        synergy_score = result.get("synergy_score", 70)
        return matches, float(synergy_score)

    except Exception as e:
        print(f"[AI MATCH] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return _simple_keyword_matching(kddi_articles)

def _simple_keyword_matching(articles: list[dict]) -> tuple[list[dict], float]:
    """従来型のキーワードマッチング（フォールバック用）"""
    matches = []
    seen_solutions = set()
    total_hits = 0
    keyword_freq: dict[str, int] = {}

    for article in articles:
        title = article["title"]
        for keyword, sol in SOLUTION_MAP.items():
            if keyword in title:
                total_hits += 1
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
                if sol["solution"] not in seen_solutions:
                    seen_solutions.add(sol["solution"])
                    matches.append({
                        "kddi": keyword,
                        "source": title,
                        "fujitsu": sol["solution"],
                        "action": sol["action"],
                        "link": article["link"],
                        "fujitsu_url": sol.get("url", ""),
                        "freq": 0,
                    })

    for m in matches:
        m["freq"] = keyword_freq.get(m["kddi"], 1)

    n_articles = max(len(articles), 1)
    synergy_score = min(99.9, (total_hits / n_articles) * len(matches) * 12.5)

    return matches[:4], round(synergy_score, 1)

def run_insight_matcher() -> tuple[list[dict], float]:
    """INSIGHT MATCHER - AI双方向インテリジェンス"""
    kddi_articles = fetch_news_for("KDDI", 15)
    fujitsu_articles = fetch_news_for("富士通+Uvance+OR+富士通+新製品+OR+富士通+DX+OR+富士通+AI", 10)
    return ai_semantic_matching(kddi_articles, fujitsu_articles)


@st.cache_data(ttl=300)
def check_alerts(kddi_pct, fujitsu_pct, docomo_pct, softbank_pct, ctc_pct) -> list[str]:
    """株価急変・重要ニュースを検知してアラートを返す。"""
    alerts = []
    threshold = 2.0  # 2%以上の変動でアラート
    if kddi_pct is not None and abs(kddi_pct) >= threshold:
        direction = "急騰" if kddi_pct > 0 else "急落"
        alerts.append(f"KDDI {direction} {abs(kddi_pct):.1f}%")
    if fujitsu_pct is not None and abs(fujitsu_pct) >= threshold:
        direction = "急騰" if fujitsu_pct > 0 else "急落"
        alerts.append(f"FUJITSU {direction} {abs(fujitsu_pct):.1f}%")
    if docomo_pct is not None and abs(docomo_pct) >= threshold:
        direction = "急騰" if docomo_pct > 0 else "急落"
        alerts.append(f"NTT docomo {direction} {abs(docomo_pct):.1f}%")
    if softbank_pct is not None and abs(softbank_pct) >= threshold:
        direction = "急騰" if softbank_pct > 0 else "急落"
        alerts.append(f"SoftBank {direction} {abs(softbank_pct):.1f}%")
    if ctc_pct is not None and abs(ctc_pct) >= threshold:
        direction = "急騰" if ctc_pct > 0 else "急落"
        alerts.append(f"CTC {direction} {abs(ctc_pct):.1f}%")
    # 重要キーワード検知
    critical_keywords = ["決算", "下方修正", "上方修正", "不正", "障害", "買収", "提携", "M&A"]
    news = fetch_news_for("KDDI", 5)
    for a in news:
        for kw in critical_keywords:
            if kw in a["title"]:
                alerts.append(f"CRITICAL: {kw}検知")
                break
    return alerts


@st.cache_data(ttl=1800)  # 30分キャッシュ
def fetch_tokyo_weather() -> dict:
    """東京の天気情報を取得"""
    try:
        import requests
        # wttr.in API（無料、APIキー不要）
        response = requests.get("https://wttr.in/Tokyo?format=j1", timeout=5)
        data = response.json()

        current = data["current_condition"][0]
        temp_c = current["temp_C"]
        weather_desc = current["weatherDesc"][0]["value"]
        feels_like = current["FeelsLikeC"]
        humidity = current["humidity"]

        # 天気アイコンマッピング
        weather_code = current["weatherCode"]
        icon = "☀️"  # default sunny
        if weather_code in ["113"]:
            icon = "☀️"  # Clear/Sunny
        elif weather_code in ["116", "119", "122"]:
            icon = "⛅"  # Partly cloudy
        elif weather_code in ["143", "248", "260"]:
            icon = "🌫️"  # Fog/Mist
        elif weather_code in ["176", "263", "266", "293", "296"]:
            icon = "🌧️"  # Light rain
        elif weather_code in ["299", "302", "305", "308", "356"]:
            icon = "🌧️"  # Heavy rain
        elif weather_code in ["227", "230", "323", "326", "329", "332", "335", "338"]:
            icon = "❄️"  # Snow
        elif weather_code in ["200", "386", "389", "392", "395"]:
            icon = "⛈️"  # Thunderstorm

        return {
            "temp": temp_c,
            "feels_like": feels_like,
            "weather": weather_desc,
            "humidity": humidity,
            "icon": icon
        }
    except Exception as e:
        return {
            "temp": "--",
            "feels_like": "--",
            "weather": "N/A",
            "humidity": "--",
            "icon": "☁️"
        }


