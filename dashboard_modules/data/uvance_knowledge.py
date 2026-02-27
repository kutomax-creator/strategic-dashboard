"""
UVANCE Knowledge Base - Structured product/solution data for hypothesis proposals
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UvanceSolution:
    name: str
    vertical: str
    description: str
    key_features: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    differentiators: list[str] = field(default_factory=list)
    reference_cases: list[str] = field(default_factory=list)
    kddi_relevance: str = ""
    typical_roi: str = ""


# ─── UVANCE Solutions Catalog ─────────────────────────────────────────
UVANCE_SOLUTIONS: list[UvanceSolution] = [
    UvanceSolution(
        name="Uvance Digital Shifts",
        vertical="Digital Shifts",
        description="企業のDX推進を加速するエンドツーエンドソリューション。業務プロセス変革からデータ活用基盤構築まで。",
        key_features=[
            "業務プロセスDX（BPR + デジタル化）",
            "Kozuchi AI Platform連携（生成AI・ML基盤）",
            "Data e-TRUST（データガバナンス・プライバシー保護）",
            "アジャイル共創プログラム",
        ],
        use_cases=[
            "WAKONX連携によるDXプラットフォーム構築",
            "カスタマーエクスペリエンス高度化",
            "データドリブン経営意思決定基盤",
            "生成AIを活用した業務自動化",
        ],
        differentiators=[
            "Kozuchi AI Platformによるマルチモーダル生成AI基盤",
            "Data e-TRUSTの信頼性あるデータ流通",
            "Palantir連携によるデータ分析高度化",
        ],
        reference_cases=[
            "通信事業者向けネットワーク最適化AI",
            "金融機関DX基盤構築プロジェクト",
        ],
        kddi_relevance="WAKONX/BXのDX推進基盤として最も親和性が高い。KDDIの法人事業DX支援サービスとのシナジー。",
        typical_roi="業務効率30-40%改善、データ活用による売上5-10%向上（12-18ヶ月で投資回収）",
    ),
    UvanceSolution(
        name="Uvance Hybrid IT",
        vertical="Hybrid IT",
        description="マルチクラウド・オンプレミスのハイブリッドIT基盤を最適化。運用自動化とセキュリティを統合。",
        key_features=[
            "マルチクラウド統合管理",
            "ゼロトラストセキュリティアーキテクチャ",
            "AIOps（AI運用自動化）",
            "クラウドネイティブ移行支援",
        ],
        use_cases=[
            "KDDIデータセンター×クラウドハイブリッド最適化",
            "5Gエッジコンピューティング基盤",
            "通信インフラのクラウドネイティブ化",
        ],
        differentiators=[
            "富士通グローバルDC網との連携",
            "ゼロトラスト＋SASEの統合アプローチ",
            "AIOpsによるIT運用コスト60%削減実績",
        ],
        reference_cases=[
            "大手通信事業者のクラウド移行プロジェクト",
            "グローバルIT基盤統合案件",
        ],
        kddi_relevance="KDDIのデータセンター事業・クラウドサービスとの直接連携。5Gエッジとの統合提案。",
        typical_roi="IT運用コスト30-50%削減、インフラ障害50%減少（投資回収期間9-15ヶ月）",
    ),
    UvanceSolution(
        name="Kozuchi AI Platform",
        vertical="Digital Shifts",
        description="富士通の生成AI・機械学習統合プラットフォーム。エンタープライズ向けセキュアなAI基盤。",
        key_features=[
            "マルチモーダル生成AI（テキスト・画像・コード）",
            "企業専用LLMファインチューニング",
            "RAG（検索拡張生成）基盤",
            "AI倫理・ガバナンスフレームワーク",
        ],
        use_cases=[
            "コールセンターAI自動応答",
            "社内ナレッジ検索の高度化",
            "契約書・技術文書の自動生成・分析",
            "コード生成・レビュー自動化",
        ],
        differentiators=[
            "日本語特化の高精度LLM",
            "エンタープライズセキュリティ標準準拠",
            "Fujitsu Research発の独自AI技術",
        ],
        reference_cases=[
            "大手金融機関向け生成AI基盤構築",
            "製造業向けAI品質検査システム",
        ],
        kddi_relevance="KDDIの法人AI活用サービス、AIコールセンター、WAKONX AI機能との統合。",
        typical_roi="業務自動化により人件費20-35%削減、サービス応答速度60%向上",
    ),
    UvanceSolution(
        name="Data e-TRUST",
        vertical="Digital Shifts",
        description="安全・信頼性の高いデータ流通基盤。パーソナルデータの適正管理からビジネスデータ活用まで。",
        key_features=[
            "データガバナンスフレームワーク",
            "プライバシー保護技術（差分プライバシー等）",
            "データカタログ・メタデータ管理",
            "Palantir Foundry連携",
        ],
        use_cases=[
            "顧客データ統合・360度ビュー構築",
            "データマネタイゼーション基盤",
            "規制対応（個人情報保護法等）データ管理",
        ],
        differentiators=[
            "Palantirとの戦略的パートナーシップ",
            "日本の法規制に完全準拠した設計",
            "リアルタイムデータパイプライン",
        ],
        reference_cases=[
            "ヘルスケアデータ流通プラットフォーム",
            "スマートシティデータ統合基盤",
        ],
        kddi_relevance="KDDIの保有する大規模顧客データの安全な活用。位置情報・通信データのデータビジネス推進。",
        typical_roi="データ活用による新規収益5-15%創出、規制対応コスト40%削減",
    ),
    UvanceSolution(
        name="Private 5G Solution",
        vertical="Digital Shifts",
        description="企業・自治体向けプライベート5Gネットワーク構築。超低遅延・大容量通信でDXを実現。",
        key_features=[
            "ローカル5G基地局設計・構築",
            "ネットワークスライシング",
            "エッジコンピューティング連携",
            "AI×5Gリアルタイム分析",
        ],
        use_cases=[
            "スマートファクトリー（製造現場DX）",
            "建設現場遠隔監視",
            "スタジアム・商業施設の高密度通信",
        ],
        differentiators=[
            "富士通のネットワーク技術蓄積（O-RAN推進）",
            "5G＋AI＋エッジの統合ソリューション",
        ],
        reference_cases=[
            "製造業向けローカル5G工場",
            "スマートスタジアム実証",
        ],
        kddi_relevance="KDDIの5G事業との補完関係。KDDI法人向けプライベート5Gサービスとの協業機会。",
        typical_roi="製造ライン稼働率15-25%向上、リモート監視によるコスト20%削減",
    ),
    UvanceSolution(
        name="Uvance Healthy Living",
        vertical="Healthy Living",
        description="ヘルスケア・ライフサイエンス向けDXソリューション。医療データ活用から健康経営支援まで。",
        key_features=[
            "医療データ統合プラットフォーム",
            "AI診断支援",
            "リモートヘルスモニタリング",
            "健康経営支援ダッシュボード",
        ],
        use_cases=[
            "遠隔医療基盤構築",
            "従業員健康管理DX",
            "創薬データ分析",
        ],
        differentiators=[
            "医療機関との豊富な実績",
            "PMDA対応のバリデーション体制",
        ],
        reference_cases=[
            "大学病院AI診断支援システム",
            "製薬会社データプラットフォーム",
        ],
        kddi_relevance="KDDIのヘルスケア事業（au WALLET等の健康サービス）との連携。通信×ヘルスケアの新市場。",
        typical_roi="医療コスト15-20%削減、従業員健康リスク30%低減",
    ),
    UvanceSolution(
        name="Uvance Trusted Society",
        vertical="Trusted Society",
        description="安全・安心な社会基盤をデジタルで実現。スマートシティ・防災・行政DXソリューション。",
        key_features=[
            "スマートシティプラットフォーム",
            "デジタルツイン都市モデル",
            "防災・減災情報基盤",
            "行政DX・マイナンバー連携",
        ],
        use_cases=[
            "自治体DX基盤構築",
            "交通最適化・MaaS",
            "災害対応リアルタイムシステム",
        ],
        differentiators=[
            "日本全国の自治体導入実績",
            "デジタルツイン技術の先進性",
        ],
        reference_cases=[
            "政令指定都市スマートシティ基盤",
            "広域防災情報システム",
        ],
        kddi_relevance="KDDIの自治体向け通信インフラ・IoTサービスとの統合。スマートシティ共同推進。",
        typical_roi="行政コスト20-30%削減、市民サービス満足度25%向上",
    ),
    UvanceSolution(
        name="Zero Trust Security",
        vertical="Hybrid IT",
        description="ゼロトラストアーキテクチャに基づく統合セキュリティソリューション。SASE・XDR・IAM統合。",
        key_features=[
            "SASE（Secure Access Service Edge）",
            "XDR（Extended Detection and Response）",
            "IAM（Identity Access Management）",
            "セキュリティ運用自動化（SOAR）",
        ],
        use_cases=[
            "リモートワーク環境のセキュリティ強化",
            "サプライチェーンセキュリティ",
            "OTセキュリティ（制御系ネットワーク保護）",
        ],
        differentiators=[
            "SOC/CSIRT運用の豊富な実績",
            "国内最大級のセキュリティ監視基盤",
        ],
        reference_cases=[
            "大手通信事業者SOC構築",
            "製造業OTセキュリティ導入",
        ],
        kddi_relevance="KDDIの法人セキュリティサービスとの協業。通信事業者としてのセキュリティ強化ニーズに対応。",
        typical_roi="セキュリティインシデント70%削減、対応時間80%短縮",
    ),
    UvanceSolution(
        name="Uvance Business Applications",
        vertical="Digital Shifts",
        description="ERPモダナイゼーション・業務アプリケーション刷新。SAP S/4HANA移行を含む。",
        key_features=[
            "SAP S/4HANA移行・最適化",
            "ローコード/ノーコード業務アプリ開発",
            "業務プロセスマイニング",
            "RPA統合自動化",
        ],
        use_cases=[
            "基幹システム刷新（2027年問題対応）",
            "業務プロセス可視化・最適化",
            "部門横断データ統合",
        ],
        differentiators=[
            "SAP認定パートナーとしての豊富な導入実績",
            "業務コンサルからシステム構築まで一貫支援",
        ],
        reference_cases=[
            "大手通信会社ERP刷新プロジェクト",
            "グローバルSAP統合案件",
        ],
        kddi_relevance="KDDIの基幹システム刷新ニーズ。2027年問題への対応支援。",
        typical_roi="業務処理速度40%向上、年間運用コスト25-35%削減（投資回収18-24ヶ月）",
    ),
    UvanceSolution(
        name="Sustainability Transformation",
        vertical="Digital Shifts",
        description="サステナビリティ経営をデジタルで推進。CO2排出量可視化からグリーンDXまで。",
        key_features=[
            "CO2排出量可視化・管理プラットフォーム",
            "サプライチェーンESGスコアリング",
            "グリーンIT最適化",
            "サステナビリティレポート自動生成",
        ],
        use_cases=[
            "Scope1/2/3排出量管理",
            "サプライチェーンの脱炭素化支援",
            "TCFDレポート作成支援",
        ],
        differentiators=[
            "富士通自身のカーボンニュートラル実績",
            "グローバルサプライチェーンでの実装経験",
        ],
        reference_cases=[
            "大手製造業CO2管理基盤",
            "サプライチェーンESG評価システム",
        ],
        kddi_relevance="KDDIのカーボンニュートラル宣言・ESG戦略との連携。通信インフラのグリーン化支援。",
        typical_roi="CO2排出量20-30%削減、ESGスコア向上による企業価値増加",
    ),
]


# ─── POC Fatigue Context ──────────────────────────────────────────────
POC_FATIGUE_CONTEXT = {
    "executive_quote": "松田社長の「PoC疲れ」「PoC死」言及 — 実証実験が本番展開に繋がらない課題を経営レベルで認識",
    "industry_background": "日本企業のDXプロジェクトの約70%がPoC段階で停滞（経産省DXレポート）",
    "fujitsu_answer": [
        "本番直結型設計: PoCから本番環境への移行を前提としたアーキテクチャ",
        "3ヶ月MVP: 最初の3ヶ月で最小限の本番稼働可能プロダクトを構築",
        "初期段階ROI試算: PoC開始前にビジネスケースを明確化",
        "段階的スケール: Small Start → Quick Win → Full Scale の3ステップ",
        "共創型開発: 顧客と富士通が共同でプロダクトオーナーを務める体制",
        "KPIドリブン: PoC段階から本番と同じKPIで評価",
    ],
    "approach_principles": [
        "PoC ≠ 実験 → PoC = 本番Phase1",
        "成果物はプロトタイプではなくMVP（Minimum Viable Product）",
        "投資判断に必要な定量データを3ヶ月で取得",
        "技術検証と同時にビジネスバリデーションを実施",
    ],
}


# ─── Helper Functions ─────────────────────────────────────────────────
def get_uvance_context_for_proposal(opportunity_title: str) -> str:
    """AIプロンプト用にUVANCEナレッジをテキスト化"""
    # タイトルからキーワードマッチでソリューションを選定
    title_lower = opportunity_title.lower()
    relevant = []
    for sol in UVANCE_SOLUTIONS:
        score = 0
        keywords = sol.name.lower().split() + sol.vertical.lower().split()
        keywords += [kw.lower() for kw in sol.key_features[:3]]
        for kw in keywords:
            if kw in title_lower:
                score += 1
        # KDDI関連性が言及されていれば加点
        if any(w in title_lower for w in ["kddi", "通信", "5g", "dx", "ai", "データ", "セキュリティ", "クラウド"]):
            score += 1
        if score > 0:
            relevant.append((score, sol))

    # スコア順ソート、最低3件は含める
    relevant.sort(key=lambda x: x[0], reverse=True)
    if not relevant:
        relevant = [(1, sol) for sol in UVANCE_SOLUTIONS[:5]]
    selected = [sol for _, sol in relevant[:5]]

    lines = ["# 富士通Uvance ソリューション情報\n"]
    for sol in selected:
        lines.append(f"## {sol.name} ({sol.vertical})")
        lines.append(f"概要: {sol.description}")
        lines.append(f"主要機能: {', '.join(sol.key_features)}")
        lines.append(f"ユースケース: {', '.join(sol.use_cases[:3])}")
        lines.append(f"差別化要素: {', '.join(sol.differentiators)}")
        if sol.reference_cases:
            lines.append(f"参考事例: {', '.join(sol.reference_cases)}")
        lines.append(f"KDDI関連性: {sol.kddi_relevance}")
        lines.append(f"典型的ROI: {sol.typical_roi}")
        lines.append("")

    return "\n".join(lines)


def get_poc_fatigue_context() -> str:
    """POC疲れ対策コンテキストをテキスト化"""
    ctx = POC_FATIGUE_CONTEXT
    lines = [
        "# PoC疲れ対策アプローチ\n",
        f"## 背景",
        f"- {ctx['executive_quote']}",
        f"- {ctx['industry_background']}\n",
        "## 富士通の回答:",
    ]
    for answer in ctx["fujitsu_answer"]:
        lines.append(f"- {answer}")
    lines.append("\n## アプローチ原則:")
    for principle in ctx["approach_principles"]:
        lines.append(f"- {principle}")
    return "\n".join(lines)


def get_all_verticals() -> list[str]:
    """全バーティカル名を返す"""
    return sorted(set(sol.vertical for sol in UVANCE_SOLUTIONS))


def find_solutions_by_vertical(vertical: str) -> list[UvanceSolution]:
    """バーティカル名でソリューションをフィルタ"""
    return [sol for sol in UVANCE_SOLUTIONS if sol.vertical == vertical]
