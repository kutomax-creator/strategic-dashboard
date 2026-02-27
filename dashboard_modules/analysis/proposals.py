"""
Proposal Framework Generator - Generate proposal documents from opportunities
"""
from __future__ import annotations

import json
from datetime import datetime

import streamlit as st
from ..config import HAS_AI, HAS_GAMMA, APP_ROOT
from ..ai_client import chat_completion
from ..data.uvance_knowledge import get_uvance_context_for_proposal, get_poc_fatigue_context
from ..data.kddi_watcher import get_intelligence_summary
from ..components.context import get_active_context_data

# ─── Proposal Framework Generator ────────────────────────────────
@st.cache_data(ttl=7200)
def generate_proposal_framework(opportunity_title: str, report_content: str) -> str | None:
    """オポチュニティレポートから提案骨子を生成"""
    if not HAS_AI:
        return None

    try:
        return chat_completion(
            messages=[{
                "role": "user",
                "content": f"""# 役割定義 (Role)
あなたは、KDDI（特にWAKONX/KDDI BX）のビジネスを成功に導く経験豊富な提案戦略プランナーです。あなたの強みは、複雑な情報を整理し、相手の課題に寄り添いながら、投資対効果（ROI）を明確に示した、論理的で説得力のあるストーリーを構築することです。

# 目的 (Objective)
提供された「オポチュニティレポート」を基に、KDDI（WAKONX/KDDI BX）のエグゼクティブ（事業部長、部長クラス）が短時間で価値を理解し、意思決定を下せるような、戦略的な「提案書骨子」を生成することです。

# 入力情報
【オポチュニティ】
{opportunity_title}

【詳細レポート】
{report_content}

【自社ソリューション】
富士通Uvance（Digital Shifts, Hybrid IT, Healthy Living等）、Kozuchi AI Platform、Data e-TRUST、プライベート5G、ゼロトラストセキュリティ等

# 出力形式
マークダウン形式で、提案書の構成案を**スライド形式**で示してください。

**各スライドは以下の形式:**
```
## スライド[番号]: [スライドタイトル]
**メッセージライン:** [このスライドで伝えたい核心メッセージ]

[本文・要点を箇条書き]
```

# 提案書骨子構成

## **1. エグゼクティブサマリー（1スライド）**
- KDDI/WAKONX/BXの現状認識と素晴らしいビジョンへの共感
- 本提案の核心（一言で何か）
- 期待される成果とROI予測
- なぜ「今」投資すべきか

## **2. KDDI/WAKONX/BXのビジネス環境と経営課題（2-3スライド）**
各スライド1課題:
- スライド形式: 「課題[番号]: [課題タイトル]」
- メッセージライン: 課題の本質を一言で
- 課題の具体的説明（外部環境、内部構造的課題）

## **3. 提案の方向性（1スライド）**
- 課題解決に向けたアプローチとコンセプト
- 富士通Uvanceの独自性・哲学

## **4. ソリューション提案（2-3スライド）**
各スライド1ソリューション:
- ソリューション概要と主要機能
- どの課題を解決するか明確にマッピング
- WAKONX/KDDI BXでの具体的適用シーン

## **5. 投資対効果（ROI）（1-2スライド）**
- 定量的効果: コスト削減、売上向上、投資回収期間
- 定性的効果: 従業員満足度、意思決定迅速化等
- 試算根拠の明記

## **6. 導入計画（1スライド）**
- フェーズ別タイムライン
- サポート体制

## **7. 富士通の強み（1スライド）**
- 実績、パートナーとしての姿勢

## **8. ネクストステップ（1スライド）**
- 具体的な次のアクション

# 制約事項
- 専門用語は避け、経営者が理解できる平易な言葉で
- 「課題→解決策→効果」のストーリーを意識
- ROIは論理的で現実的に
- WAKONX/KDDI BXに特化した提案内容にする

上記の構成で、提案書骨子を作成してください。"""
            }],
            max_tokens=8000,
            model="claude-sonnet-4-5-20250929",
        ).strip()
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


# ─── Hypothesis Proposal Generator ───────────────────────────────
_PROPOSAL_HISTORY_FILE = APP_ROOT / "data" / "proposal_history.json"


def generate_hypothesis_proposal(
    opportunity_title: str,
    report_content: str,
    kddi_news: tuple | list = (),
    fujitsu_news: tuple | list = (),
) -> dict:
    """仮説提案書用の構造化テキストを生成する。

    Returns:
        dict: {
            "gamma_input": str,       # Gamma API投入用テキスト（10スライド構成）
            "approach_plan": str,     # テキストベースの週次アプローチ計画
            "metadata": dict,         # pain_points, central_hypothesis, slide_count等
            "generated_at": str,
            "opportunity_title": str,
        }
    """
    if not HAS_AI:
        return {
            "gamma_input": "",
            "approach_plan": "AI APIが利用できません。ANTHROPIC_API_KEYを設定してください。",
            "metadata": {},
            "generated_at": datetime.now().isoformat(),
            "opportunity_title": opportunity_title,
        }

    # コンテキスト情報を収集
    uvance_context = get_uvance_context_for_proposal(opportunity_title)
    poc_context = get_poc_fatigue_context()
    intel_summary = get_intelligence_summary(15)
    context_data = get_active_context_data() or ""

    kddi_news_text = "\n".join(f"- {t}" for t in kddi_news[:10]) if kddi_news else "（最新ニュースなし）"
    fujitsu_news_text = "\n".join(f"- {t}" for t in fujitsu_news[:10]) if fujitsu_news else "（最新ニュースなし）"

    context_section = ""
    if context_data:
        context_section = f"""
# IR資料・追加コンテキスト
{context_data[:5000]}
"""

    # Phase 1: 仮説提案テキスト生成（Gamma投入用）
    gamma_prompt = f"""# 役割
あなたは「UVANCE×KDDI仮説提案書」を作成するエキスパートです。
KDDI経営層（CTO/CDO/事業部長クラス）が10枚のスライドで意思決定できる提案書を作成します。

# 入力情報

## オポチュニティ
{opportunity_title}

## レポート内容
{report_content[:4000]}

## KDDI最新動向
{kddi_news_text}

## 富士通最新動向
{fujitsu_news_text}

## KDDIインテリジェンス
{intel_summary[:2000]}

{uvance_context}

{poc_context}
{context_section}

# 出力指示
以下の10スライド構成で**Gamma.app用のプレーンテキスト**を生成してください。

**フォーマットルール:**
- 各スライドは「# スライドN: タイトル」で開始
- 各スライド本文は200字以内
- 箇条書きを主体に、平易な日本語で
- 数値・ROIは具体的に
- 専門用語は最小限

## スライド構成

# スライド1: エグゼクティブサマリー
- 提案の核心を一言で
- KDDIの経営ビジョンへの共感
- 期待成果（数値入り）

# スライド2: KDDI経営課題①
- 最も重要な痛点を構造化
- 外部環境の変化との関連
- 定量的インパクト

# スライド3: KDDI経営課題②
- 2番目の痛点
- 「PoC疲れ」への言及（松田社長発言の文脈）
- 業界トレンドとの関連

# スライド4: 仮説提案（中心メッセージ）
- 痛点→仮説のロジック
- 「こうすればKDDIの課題が解決する」を一枚で
- UVANCEソリューションとの紐付け

# スライド5: UVANCE具体提案①
- ソリューション名と概要
- KDDIでの具体的適用シーン
- 期待効果

# スライド6: UVANCE具体提案②
- 2つ目のソリューション
- 課題とのマッピング
- シナジー効果

# スライド7: PoC疲れ解消アプローチ
- 「PoC ≠ 実験 → PoC = 本番Phase1」
- 3ヶ月MVPアプローチ
- 具体的な成功指標（KPI）

# スライド8: ROI試算
- 定量効果（コスト削減額、売上向上額）
- 投資回収期間
- 試算根拠

# スライド9: Why Fujitsu
- 富士通の差別化要素
- KDDI×富士通の実績
- パートナーとしての姿勢

# スライド10: Next Steps
- 具体的な次のアクション（日程入り）
- 初回ワークショップ提案
- 担当者・連絡先

上記の構成に従い、提案書テキストを生成してください。"""

    try:
        gamma_input = chat_completion(
            messages=[{"role": "user", "content": gamma_prompt}],
            max_tokens=6000,
            model="claude-sonnet-4-5-20250929",
        ).strip()
    except Exception as e:
        gamma_input = f"提案テキスト生成エラー: {e}"

    # Phase 2: アプローチ計画生成
    approach_prompt = f"""# 役割
あなたはKDDIアカウント戦略の専門家です。

# タスク
以下の仮説提案に基づき、**4週間のアプローチ計画**を作成してください。

## 提案内容
{gamma_input[:3000]}

# 出力形式（マークダウン）

## 週次アプローチ計画

### Week 1: 初期アプローチ
- 具体的なアクション（誰に・何を・どうやって）
- 準備すべき資料

### Week 2: 深堀り
- フォローアップアクション
- 追加調査項目

### Week 3: 提案精緻化
- 提案書のブラッシュアップ
- 社内承認プロセス

### Week 4: クロージング
- 最終プレゼンテーション
- 契約に向けたアクション

## Key Person Map
- アプローチすべきKDDI側のキーパーソン（役職・部門・関心事）

## リスクと対策
- 想定されるリスクと対策案

各週のアクションは具体的かつ実行可能な内容にしてください。"""

    try:
        approach_plan = chat_completion(
            messages=[{"role": "user", "content": approach_prompt}],
            max_tokens=3000,
            model="claude-sonnet-4-5-20250929",
        ).strip()
    except Exception as e:
        approach_plan = f"アプローチ計画生成エラー: {e}"

    # メタデータ抽出
    metadata = {
        "slide_count": 10,
        "has_poc_fatigue": "PoC" in gamma_input,
        "has_roi": "ROI" in gamma_input or "投資回収" in gamma_input,
        "has_gamma_api": HAS_GAMMA,
        "uvance_solutions_referenced": _count_uvance_references(gamma_input),
    }

    result = {
        "gamma_input": gamma_input,
        "approach_plan": approach_plan,
        "metadata": metadata,
        "generated_at": datetime.now().isoformat(),
        "opportunity_title": opportunity_title,
    }

    # 履歴に保存
    _save_proposal_history(result)

    return result


def _count_uvance_references(text: str) -> int:
    """テキスト中のUVANCEソリューション参照数をカウント"""
    keywords = [
        "Digital Shifts", "Hybrid IT", "Healthy Living", "Trusted Society",
        "Kozuchi", "Data e-TRUST", "ゼロトラスト", "プライベート5G",
    ]
    return sum(1 for kw in keywords if kw in text)


def _save_proposal_history(result: dict) -> None:
    """提案履歴を保存"""
    try:
        _PROPOSAL_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if _PROPOSAL_HISTORY_FILE.exists():
            history = json.loads(_PROPOSAL_HISTORY_FILE.read_text(encoding="utf-8"))

        # 履歴エントリ（テキスト全文は除外し軽量に）
        entry = {
            "opportunity_title": result["opportunity_title"],
            "generated_at": result["generated_at"],
            "metadata": result["metadata"],
            "gamma_input_preview": result["gamma_input"][:300],
        }
        history.append(entry)
        # 最大50件
        history = history[-50:]
        _PROPOSAL_HISTORY_FILE.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[PROPOSAL] History save failed: {e}")


def get_proposal_history() -> list[dict]:
    """提案生成履歴を返す"""
    try:
        if _PROPOSAL_HISTORY_FILE.exists():
            return json.loads(_PROPOSAL_HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []

