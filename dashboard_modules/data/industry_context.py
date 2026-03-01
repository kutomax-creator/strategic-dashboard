"""
Industry Context - Competitor profiles, industry trends, and KDDI strategic context
"""
from __future__ import annotations


# ─── Competitor Profiles ─────────────────────────────────────────
COMPETITOR_PROFILES: dict[str, dict] = {
    "NEC": {
        "strengths": ["iExperience顔認証", "海底ケーブル", "公共系SI"],
        "weaknesses": ["クラウドネイティブ弱い", "共創型提案の実績薄い"],
        "kddi_relationship": "ネットワーク機器で取引あり。AI/DX領域では富士通が優位。",
        "watch_areas": ["生体認証×5G", "デジタルガバメント"],
    },
    "NTTデータ": {
        "strengths": ["大規模SI実績", "グローバルデリバリー", "金融系基盤"],
        "weaknesses": ["グループ内利益相反（NTTドコモ）", "プロダクト型提案が弱い"],
        "kddi_relationship": "NTTグループとの競合関係でKDDIは警戒。富士通は中立的パートナー。",
        "watch_areas": ["Generative AI SI", "データセンター統合"],
    },
    "アクセンチュア": {
        "strengths": ["戦略コンサル", "グローバルベストプラクティス", "DX変革手法"],
        "weaknesses": ["実装力がSIベンダー依存", "コスト高", "日本固有課題への理解"],
        "kddi_relationship": "コンサル案件で採用あり。富士通は実装力＋コンサルの一体提供で差別化。",
        "watch_areas": ["CxOアドバイザリー", "業務変革"],
    },
    "AWS / Azure": {
        "strengths": ["クラウドインフラ", "AI/MLサービス", "エコシステム"],
        "weaknesses": ["日本語対応", "カスタマイズ性", "オンプレ連携"],
        "kddi_relationship": "KDDIはAWSパートナー。富士通はハイブリッドIT＋日本固有要件で補完。",
        "watch_areas": ["エッジAI", "業種別クラウド"],
    },
}


# ─── Industry Trends ─────────────────────────────────────────────
INDUSTRY_TRENDS_2025: list[dict] = [
    {
        "trend": "生成AI企業導入の本格化",
        "impact_on_kddi": "法人向けAIサービス需要急増。WAKONXのAI機能強化が急務。",
        "fujitsu_angle": "Kozuchi AI Platformでセキュアなエンタープライズ生成AI基盤を提供",
        "related_verticals": ["Digital Shifts"],
    },
    {
        "trend": "通信×非通信の収益多角化",
        "impact_on_kddi": "ARPU成長鈍化→金融・エネルギー・ヘルスケア等の非通信事業拡大が経営課題",
        "fujitsu_angle": "Healthy Living, Trusted Societyの業種特化ソリューションで非通信領域を共同開拓",
        "related_verticals": ["Healthy Living", "Trusted Society"],
    },
    {
        "trend": "サプライチェーンESG規制強化",
        "impact_on_kddi": "Scope3排出量開示義務化に向けた準備。通信インフラのグリーン化圧力。",
        "fujitsu_angle": "Sustainability Transformationで排出量可視化→削減を一貫支援",
        "related_verticals": ["Digital Shifts"],
    },
    {
        "trend": "ゼロトラスト・SASE移行の加速",
        "impact_on_kddi": "法人セキュリティサービスの高付加価値化。KDDI自身のインフラ保護も。",
        "fujitsu_angle": "Zero Trust Securityの統合アプローチで差別化",
        "related_verticals": ["Hybrid IT"],
    },
    {
        "trend": "デジタルツイン・メタバース都市",
        "impact_on_kddi": "5G×XRのユースケース拡大。スマートシティ案件の増加。",
        "fujitsu_angle": "Trusted Societyのデジタルツイン技術でKDDI 5Gインフラと統合",
        "related_verticals": ["Trusted Society"],
    },
    {
        "trend": "2027年問題（SAP ECC保守終了）",
        "impact_on_kddi": "KDDI自身および法人顧客の基幹システム刷新需要。",
        "fujitsu_angle": "Business ApplicationsのSAP移行実績で大型案件獲得",
        "related_verticals": ["Digital Shifts"],
    },
]


# ─── KDDI Strategic Context (IR-based) ───────────────────────────
KDDI_STRATEGIC_CONTEXT = {
    "vision": "「つなぐチカラ」を進化させ、誰もが思いを実現できる社会を作る",
    "mid_term_plan": "サテライトグロース戦略 — 通信を核に周辺領域（金融・エネルギー・教育・ヘルスケア）へ拡大",
    "key_initiatives": [
        "WAKONX: 法人DXプラットフォーム事業（AI・データ・クラウド統合）",
        "BX: ビジネス変革部門（新規共創事業の創出）",
        "Starlink連携: 衛星通信によるカバレッジ拡大",
        "金融事業: auじぶん銀行・au PAYの金融エコシステム拡大",
        "エネルギー事業: auでんき・カーボンニュートラル推進",
        "ヘルスケア: 遠隔医療・健康管理サービス",
    ],
    "pain_points": [
        "通信ARPU成長の限界 → 非通信収益の拡大が急務",
        "法人DX案件の大型化 → パートナーの実装力が必要",
        "PoC疲れ → 本番直結のアプローチを求めている",
        "セキュリティリスクの高度化 → ゼロトラスト対応",
        "人材不足 → AI/自動化による生産性向上",
        "ESG/サステナビリティ → 投資家からの要請強化",
    ],
    "financial_highlights": {
        "revenue": "約5.7兆円（2024年度）",
        "operating_income": "約1.1兆円",
        "capex": "約6,500億円（うちDX投資比率拡大中）",
        "subscriber_base": "au: 約3,100万、UQ: 約1,200万",
    },
}


# ─── Helper Functions ─────────────────────────────────────────────
def get_industry_context_for_proposal(vertical: str) -> str:
    """バーティカルに関連する業界トレンドと競合情報をテキスト化"""
    lines = ["# 業界トレンド・競合コンテキスト\n"]

    # 関連トレンド抽出
    lines.append("## 関連する業界トレンド")
    matched = False
    for trend in INDUSTRY_TRENDS_2025:
        if vertical in trend.get("related_verticals", []):
            lines.append(f"- **{trend['trend']}**")
            lines.append(f"  KDDI影響: {trend['impact_on_kddi']}")
            lines.append(f"  富士通アプローチ: {trend['fujitsu_angle']}")
            matched = True
    if not matched:
        for trend in INDUSTRY_TRENDS_2025[:3]:
            lines.append(f"- **{trend['trend']}**")
            lines.append(f"  KDDI影響: {trend['impact_on_kddi']}")
            lines.append(f"  富士通アプローチ: {trend['fujitsu_angle']}")
    lines.append("")

    # 競合差別化
    lines.append("## 主要競合との差別化ポイント")
    for name, profile in COMPETITOR_PROFILES.items():
        lines.append(f"- **{name}**: {profile['kddi_relationship']}")
        lines.append(f"  弱点: {', '.join(profile['weaknesses'])}")
    lines.append("")

    return "\n".join(lines)


def get_competitor_differentiation(opportunity_title: str) -> str:
    """オポチュニティに関連する競合差別化ポイントをテキスト化"""
    title_lower = opportunity_title.lower()
    lines = ["## 競合差別化"]

    for name, profile in COMPETITOR_PROFILES.items():
        relevant = False
        for area in profile.get("watch_areas", []):
            if any(kw in title_lower for kw in area.lower().split("×")):
                relevant = True
                break
        if relevant or name in ["NEC", "NTTデータ"]:
            lines.append(f"### vs {name}")
            lines.append(f"強み: {', '.join(profile['strengths'])}")
            lines.append(f"弱点: {', '.join(profile['weaknesses'])}")
            lines.append(f"KDDI関係: {profile['kddi_relationship']}")
            lines.append("")

    return "\n".join(lines)


def get_kddi_strategic_context() -> str:
    """KDDI戦略コンテキストをプロンプト用にフォーマット"""
    ctx = KDDI_STRATEGIC_CONTEXT
    fin = ctx["financial_highlights"]
    lines = [
        "# KDDI中期経営戦略\n",
        f"## ビジョン: {ctx['vision']}",
        f"## 中期計画: {ctx['mid_term_plan']}\n",
        "## 重点施策:",
    ]
    for initiative in ctx["key_initiatives"]:
        lines.append(f"- {initiative}")

    lines.append("\n## 経営課題・ペインポイント:")
    for pain in ctx["pain_points"]:
        lines.append(f"- {pain}")

    lines.append("\n## 財務ハイライト:")
    lines.append(f"- 売上: {fin['revenue']}")
    lines.append(f"- 営業利益: {fin['operating_income']}")
    lines.append(f"- 設備投資: {fin['capex']}")
    lines.append(f"- 加入者: {fin['subscriber_base']}")

    return "\n".join(lines)
