"""
Proposal Framework Generator - Generate proposal documents from opportunities
"""
from __future__ import annotations

import streamlit as st
from ..config import HAS_AI
from ..ai_client import chat_completion

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


