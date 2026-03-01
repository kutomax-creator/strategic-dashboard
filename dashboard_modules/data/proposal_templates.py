"""
Proposal Templates - 4 types of slide templates for hypothesis proposals
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class ProposalTemplate:
    name: str
    description: str
    slide_structure: str
    suitable_for: list[str] = field(default_factory=list)
    tone: str = ""


# ─── Template Definitions ────────────────────────────────────────

TEMPLATES: dict[str, ProposalTemplate] = {
    "STANDARD": ProposalTemplate(
        name="STANDARD",
        description="汎用提案書テンプレート。初回提案やフォーマルな場面に最適。8-12スライドで課題分析からROI、Why Fujitsuまで網羅的にカバー。",
        slide_structure="""## スライド構成（STANDARD: 8-12スライド、Argument型: 状況→判断→実施策）

# スライド1: エグゼクティブサマリー
ピラミッドの頂点＝提案全体の結論
- 「KDDIの[課題]に対し、[UVANCEソリューション]で[期待成果]を実現する」を一言で
- KDDIの経営ビジョンへの共感（買い手目線）
- 期待成果（定量数値必須）

# スライド2: KDDI経営課題①（状況・事実）
- 最も重要な経営課題を構造化
- 外部環境の変化との因果関係
- 定量的インパクト（放置した場合のリスク）

# スライド3: KDDI経営課題②（状況・事実）
- 2番目の経営課題（スライド2とMECEの関係）
- 業界トレンドとの関連
- 定量的インパクト

# スライド4: 仮説提案（意味合い・判断）
Argument型の「判断」＝痛点に対する富士通の見解
- 「こうすればKDDIの課題が解決する」を明言
- 痛点→仮説のロジックを1枚で
- UVANCEソリューションとの紐付け

# スライド5: UVANCE具体提案①（実施策・How）
- ソリューション名と概要
- KDDIでの具体的適用シーン
- 課題→ソリューション→期待効果のマッピング

# スライド6: UVANCE具体提案②（実施策・How）
- 2つ目のソリューション
- スライド5とのシナジー効果
- 課題②との明確なマッピング

# スライド7: 共創型推進アプローチ（How）
- 本番環境を前提とした段階的推進（Small Start → Quick Win → Full Scale）
- 3ヶ月で本番稼働可能なMVP構築
- 初期段階からKPIを設定

# スライド8: ROI試算
- 定量効果（コスト削減額、売上向上額）を具体数値で
- 投資回収期間と試算根拠

# スライド9: Why Fujitsu
- KDDIの課題解決に対する富士通固有の差別化要素
- 競合（NEC/NTTデータ/アクセンチュア）との明確な差分

# スライド10: Next Steps
- 具体的な次のアクション（日程入り）
- 初回共創ワークショップ提案

※必要に応じてスライド5-6の間にソリューション③を追加、またはROI前に導入計画スライドを追加可能（最大12スライド）""",
        suitable_for=["Digital Shifts", "Hybrid IT", "Healthy Living", "Trusted Society"],
        tone="フォーマル、論理的、データドリブン",
    ),

    "CO_CREATION": ProposalTemplate(
        name="CO_CREATION",
        description="共創ワークショップ型テンプレート。BX部門向け新規事業共創に最適。対等なパートナーシップの姿勢で、一緒に作る提案。6-8スライド。",
        slide_structure="""## スライド構成（CO_CREATION: 6-8スライド、共創ワークショップ型）

# スライド1: 共創ビジョン — なぜKDDI×富士通なのか
- 両社のアセットが交わる「スイートスポット」を1枚で示す
- KDDIの通信基盤×富士通のクロスインダストリー知見
- 共創で生まれる価値の全体像

# スライド2: KDDI×富士通の接点マップ
- KDDIの事業ポートフォリオと富士通UVANCEの接点を可視化
- 既に成果が出ている領域と、未開拓の共創機会
- 「一緒にやるからこそ」生まれる新しい価値

# スライド3: 共創テーマ提案 — 3つの方向性
- テーマA: [KDDI課題起点のテーマ]
- テーマB: [業界トレンド起点のテーマ]
- テーマC: [両社アセット掛け合わせのテーマ]
- ワークショップで優先順位を一緒に決める設計

# スライド4: ワークショップ設計
- Day 1: 課題共有・アイデア発散（両社混成チーム）
- Day 2: プロトタイプ検討・ビジネスモデル仮説
- 参加者構成（KDDIからBX＋事業部門、富士通からUVANCE＋コンサル）
- アウトプット: 共創ロードマップドラフト

# スライド5: 期待アウトプットと成功イメージ
- ワークショップから3ヶ月後のマイルストーン
- MVP定義と本番への道筋
- KPI設定（共同で合意する指標）

# スライド6: 3ヶ月ロードマップ
- Month 1: ワークショップ → テーマ選定 → チーム組成
- Month 2: 深掘りリサーチ → MVPスコープ定義
- Month 3: MVP開発 → 初期検証 → 本番移行判断
- 各月の具体的なデリバラブル

# スライド7: 参加者・体制
- KDDI側: 推奨参加者（BX部門、事業部門、技術部門）
- 富士通側: UVANCE専門チーム、業界コンサル、技術アーキテクト
- 共同プロダクトオーナー制度

# スライド8: Next Steps — 最初の一歩
- ワークショップ日程候補（2週間以内に実施）
- 事前インプット資料
- 連絡先・窓口""",
        suitable_for=["Digital Shifts", "Trusted Society"],
        tone="対等なパートナーシップ、一緒に作る姿勢、カジュアルだが本質的",
    ),

    "QUICK_WIN": ProposalTemplate(
        name="QUICK_WIN",
        description="短期成果型テンプレート。PoC疲れ対策やスモールスタートに最適。3ヶ月で成果を出す具体性とスピード感を重視。5-7スライド。",
        slide_structure="""## スライド構成（QUICK_WIN: 5-7スライド、短期成果型）

# スライド1: 課題の緊急性 — なぜ「今」動くべきか
- KDDIが直面する具体的な課題と、対応が遅れた場合の定量的リスク
- 競合の動き（「○○社は既に△△を開始」等の具体情報）
- 「3ヶ月で初期成果を出す」というコミットメント

# スライド2: 3ヶ月で得られる成果（ゴール設定）
- 定量的な成果目標（コスト削減額、効率化率、売上インパクト）
- Before/After の具体イメージ
- 成果測定の方法とKPI

# スライド3: MVPスコープ — やること・やらないこと
- スコープIN: 3ヶ月で実現する機能・範囲（明確にリスト化）
- スコープOUT: Phase2以降に回す項目（意図的に絞る理由）
- 本番環境での稼働を前提とした設計
- 「実験ではなく、本番Phase1」の位置付け

# スライド4: 実施体制と進め方
- Week 1-4: 要件確認・環境構築・初期開発
- Week 5-8: コア機能実装・データ連携
- Week 9-12: 統合テスト・本番投入・効果測定
- 富士通×KDDIの共同推進体制（週次レビュー）

# スライド5: 投資対効果（即効性重視）
- 初期投資額（3ヶ月分のみ。大型予算不要）
- 3ヶ月後の定量効果（具体数値）
- Full Scale展開時の年間効果見込み
- 投資回収期間: ○ヶ月

# スライド6: リスクと対策
- 想定リスクTOP3と具体的な対策
- エスカレーションルール
- Go/No-Go判断基準（3ヶ月後の評価指標）

# スライド7: 即時アクション — 来週から動く
- 来週: キックオフミーティング設定
- 2週目: 要件ヒアリング＆環境準備開始
- 必要な意思決定事項（予算承認、担当者アサイン）
- 連絡先・窓口""",
        suitable_for=["Digital Shifts", "Hybrid IT"],
        tone="スピード重視、実行力アピール、具体的かつ簡潔",
    ),

    "EXECUTIVE_BRIEF": ProposalTemplate(
        name="EXECUTIVE_BRIEF",
        description="経営ブリーフ型テンプレート。CxOレベルの短時間プレゼンに最適。数字中心で判断材料を簡潔に提供。4-6スライド。",
        slide_structure="""## スライド構成（EXECUTIVE_BRIEF: 4-6スライド、経営ブリーフ型）

# スライド1: 経営インパクト — 数字で語る
- ヘッドライン: 「[X億円]の事業機会」または「[Y%]のコスト構造改革」
- KDDI中期計画との整合（サテライトグロース戦略のどこに効くか）
- 3年間の財務インパクト試算（売上/利益/コスト削減）
- 1スライドで意思決定の全体像を把握できること

# スライド2: 競合との差分 — なぜ今、富士通か
- 競合3社（NEC/NTTデータ/アクセンチュア）の動向と富士通の差別化
- 「富士通だからできること」を3つの具体的ファクトで
- 時間軸の優位性（今動けば先行者利益を取れる根拠）

# スライド3: 提案骨子 — What × How × When
- What: 提案の核心を1行で
- How: UVANCEソリューションの組合せと導入アプローチ
- When: 3段階のタイムライン（3ヶ月/6ヶ月/12ヶ月）
- 各段階の具体的成果物

# スライド4: 意思決定ポイント
- Go/No-Go の判断基準
- 必要な投資額と期待リターン（ROI表）
- リスク要因と軽減策（TOP3）
- 「今日決めていただきたいこと」を明確に

# スライド5（オプション）: 参考データ
- 類似案件の実績データ
- 業界ベンチマーク
- 富士通の関連実績

# スライド6（オプション）: Next Steps
- 即時アクション（1週間以内）
- 30日ロードマップ""",
        suitable_for=["Digital Shifts", "Hybrid IT", "Healthy Living", "Trusted Society"],
        tone="簡潔、数字中心、判断材料提供、経営者目線",
    ),
}


# ─── Template Selection Logic ────────────────────────────────────

def select_template(
    opportunity_title: str,
    vertical: str,
    past_templates: list[str] | None = None,
) -> ProposalTemplate:
    """過去の使用テンプレートと被らないよう選択する。

    Parameters
    ----------
    opportunity_title : str
        オポチュニティのタイトル
    vertical : str
        UVANCEバーティカル名
    past_templates : list[str] | None
        直近で使用したテンプレート名リスト

    Returns
    -------
    ProposalTemplate
    """
    if past_templates is None:
        past_templates = []

    # 1. バーティカルに適合するテンプレートを候補に
    candidates = []
    for name, tmpl in TEMPLATES.items():
        if vertical in tmpl.suitable_for or not tmpl.suitable_for:
            candidates.append((name, tmpl))

    if not candidates:
        candidates = list(TEMPLATES.items())

    # 2. 直近3回で使ったテンプレートを除外
    recent = set(past_templates[-3:])
    filtered = [(n, t) for n, t in candidates if n not in recent]

    # 除外しすぎたらリセット
    if not filtered:
        filtered = candidates

    # 3. タイトルのキーワードでスコアリング
    title_lower = opportunity_title.lower()
    scored = []
    for name, tmpl in filtered:
        score = 0
        if name == "CO_CREATION" and any(kw in title_lower for kw in ["共創", "bx", "ワークショップ", "新規事業"]):
            score += 3
        elif name == "QUICK_WIN" and any(kw in title_lower for kw in ["poc", "スモール", "mvp", "短期", "即効"]):
            score += 3
        elif name == "EXECUTIVE_BRIEF" and any(kw in title_lower for kw in ["経営", "cxo", "戦略", "投資"]):
            score += 3
        # ランダム要素を加えてバリエーション確保
        score += random.random() * 2
        scored.append((score, name, tmpl))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][2]


def get_past_template_names(n: int = 5) -> list[str]:
    """直近n件の提案で使われたテンプレート名を取得"""
    try:
        from ..analysis.weekly_scheduler import get_generation_history
        history = get_generation_history()
        return [
            h.get("metadata", {}).get("template_used", "STANDARD")
            if isinstance(h.get("metadata"), dict) else "STANDARD"
            for h in history[-n:]
        ]
    except Exception:
        return []
