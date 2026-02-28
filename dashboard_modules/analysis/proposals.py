"""
Proposal Framework Generator - Generate proposal documents from opportunities
"""
from __future__ import annotations

import json
import os
from datetime import datetime

import streamlit as st
from ..config import HAS_AI, APP_ROOT
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
あなたは、KDDI（特にWAKONX/KDDI BX）のビジネスを成功に導く経験豊富な提案戦略プランナーです。
あなたの強みは、ピラミッド・ストラクチャー（ミント・ピラミッド原則）に基づき、複雑な情報を論理的に構造化し、相手の課題に寄り添いながら、投資対効果（ROI）を明確に示した説得力あるストーリーを構築することです。

# 目的 (Objective)
提供された「オポチュニティレポート」を基に、KDDI（WAKONX/KDDI BX）のエグゼクティブ（事業部長、部長クラス）が短時間で価値を理解し、意思決定を下せるような、戦略的な「提案書骨子」を生成することです。

# 提案書作成の原則（必ず遵守）

## ピラミッド・ストラクチャー
- 最も重要な結論を頂点に据え、メインメッセージからマイナーメッセージへと展開
- 全体構成はArgument型（状況・事実→意味合い・判断→実施策）
- 各章レベルはGrouping型（MECEな根拠で結論をサポート）
- すべての要素に「So What?（だから何？）」テストを適用

## What / Why / How
- What: 相手への提案の中身そのもの
- Why: なぜこのWhatを提案するのか、その根拠
- How: Whatをどうやって実現するのか

## 各スライドの構成（厳守）
各スライドは必ず以下の3要素で構成:
- **タイトル**: そのスライドの章題
- **メッセージライン**: この頁を一言でいうと何か（伝えたいこと）
- **ボディ**: メッセージラインの詳細説明、根拠の証明

## 品質基準
- **1スライド＝1メッセージ**を徹底（複数メッセージは混乱を招く）
- **メッセージラインだけを順番に読めば、提案全体のストーリーが伝わる**こと
- **買い手（KDDI）の目線**で書く。売り手の理論の押し付けにしない
- メッセージを研ぎ澄ます：余計な装飾は不要、定量的・具体的に
- イカ資料禁止：「以下で説明する」「下図で～」等の曖昧表現は使わない
- 必ず自分の意見を言語化する（状況や選択肢の提示だけで終わらない）

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
## スライド[番号]: [タイトル]
**メッセージライン:** [この頁で伝えたい核心メッセージ（1文で完結）]

[ボディ: メッセージラインの根拠・詳細を箇条書き]
```

# 提案書骨子構成（Argument型: 状況→判断→実施策）

## **1. エグゼクティブサマリー（1スライド）**
- 提案全体の結論（ピラミッドの頂点）
- KDDIの経営ビジョンへの共感と現状認識
- 期待される成果とROI予測（数値必須）
- なぜ「今」投資すべきか

## **2. KDDI/WAKONX/BXのビジネス環境と経営課題（2-3スライド）**
各スライド1課題（Grouping型・MECE）:
- メッセージライン: その課題の本質を一言で断言する
- ボディ: 外部環境の変化、内部構造的課題、定量的インパクト
- 課題間の論理的つながりを意識

## **3. 提案の方向性とコンセプト（1スライド）**
- 課題に対する富士通の判断・意味合い（Argument型の「判断」部分）
- 「この課題はこうすれば解決できる」という仮説を明言
- 富士通Uvanceの哲学との紐付け

## **4. ソリューション提案（2-3スライド）**
各スライド1ソリューション（How）:
- ソリューション概要と主要機能
- どの課題を解決するか明確にマッピング（課題→ソリューション→効果）
- WAKONX/KDDI BXでの具体的適用シーン

## **5. 投資対効果（ROI）（1-2スライド）**
- 定量効果: コスト削減額、売上向上額、投資回収期間（試算根拠必須）
- 定性効果: 従業員満足度、意思決定迅速化等
- 数値は具体的かつ現実的に

## **6. 導入計画と体制（1スライド）**
- フェーズ別タイムライン（3ヶ月で初期成果を出す設計）
- 共同推進体制

## **7. 富士通の強み / Why Fujitsu（1スライド）**
- KDDIの課題解決に対する富士通の差別化要素
- 実績とパートナーとしての姿勢

## **8. ネクストステップ（1スライド）**
- 具体的な次のアクション（日程入り）
- 初回ワークショップ提案

# 制約事項
- 経営者が理解できる平易な言葉で（専門用語は最小限）
- 全体を通じて「課題→解決策→効果」のストーリーを一貫させる
- ROIは論理的で現実的な試算根拠付き
- WAKONX/KDDI BXに特化した提案内容にする
- 「PoC」「実証実験」は使わず「Phase1本番稼働」「MVP構築」等を使う

上記の構成と原則に従い、提案書骨子を作成してください。"""
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
    progress_callback=None,
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
    from ..data.uvance_knowledge import get_uvance_context_for_proposal, get_poc_fatigue_context
    from ..data.kddi_watcher import get_intelligence_summary
    from ..components.context import get_active_context_data

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
    if progress_callback:
        progress_callback(30, "仮説提案ドラフト生成中...")

    gamma_prompt = f"""# 役割
あなたは「UVANCE×KDDI仮説提案書」を作成するエキスパートです。
ピラミッド・ストラクチャー（ミント・ピラミッド原則）に基づき、KDDI経営層（CTO/CDO/事業部長クラス）が10枚のスライドで意思決定できる提案書を作成します。

# 提案書作成の原則（必ず遵守）

## ピラミッド・ストラクチャー
- 最も重要な結論を頂点に据え、メインメッセージからマイナーメッセージへと展開する
- 全体構成はArgument型（状況・事実→意味合い・判断→実施策）
- 各章レベルはGrouping型（MECEな根拠で結論をサポート）
- すべての要素に「So What?（だから何？）」テストを適用する
- 相手の疑問に答えるような上から下への流れを作る

## What / Why / How
- What: KDDIへの提案内容そのもの
- Why: なぜこの提案が必要か、その根拠と判断
- How: 提案をどうやって実現するか

## 各スライドの構成（厳守）
各スライドは必ず以下の3要素で構成すること:
- **タイトル**: そのスライドの章題
- **メッセージライン**: この頁を一言でいうと何か。伝えたいことを1文で完結させる
- **ボディ**: メッセージラインの詳細説明、根拠の証明（箇条書き主体）

## 品質基準
- **1スライド＝1メッセージ**を徹底する。1スライドに言いたいことは1つだけ
- **全スライドのメッセージラインだけを順番に読めば、提案全体のストーリーが伝わる**こと
- **買い手（KDDI）の目線**で書く。売り手の理論の押し付けにしない
- メッセージを研ぎ澄ます：余計な装飾は不要。定量的・具体的な表現を使う
- イカ資料禁止：「以下で説明する」「下図で～」等の曖昧表現は使わない
- 必ず自分の意見・判断を言語化する（状況や選択肢の提示だけで終わらない）
- 頁数は最小限に。聞き手にとって冗長な情報は削る

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
- 各スライドは以下の形式で記述:
  ```
  # スライドN: [タイトル]
  **メッセージライン:** [この頁で伝えたい核心メッセージ（1文で完結）]

  [ボディ: メッセージラインの根拠・詳細を箇条書き（200字以内）]
  ```
- 箇条書きを主体に、平易な日本語で
- 数値・ROIは具体的に
- 専門用語は最小限

## スライド構成（Argument型: 状況→判断→実施策）

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
- 初期段階からKPIを設定し、投資判断に必要なデータを取得
- 富士通×KDDIの共同プロダクトオーナー体制

# スライド8: ROI試算
- 定量効果（コスト削減額、売上向上額）を具体数値で
- 投資回収期間と試算根拠
- 定性効果も含む

# スライド9: Why Fujitsu
- KDDIの課題解決に対する富士通固有の差別化要素
- KDDI×富士通の過去実績・信頼関係
- パートナーとしての姿勢と覚悟

# スライド10: Next Steps
- 具体的な次のアクション（日程入り）
- 初回共創ワークショップ提案
- 担当者・連絡先

## 重要な方針
- 「PoC」「実証実験」という言葉は使わない。代わりに「Phase1本番稼働」「MVP構築」「共創推進」等を使う
- 提案全体が「実験で終わらず本番に直結する」設計であること
- 机上の空論ではなく、3ヶ月で成果が出る具体性を持たせること
- メッセージラインだけを10個並べて読み、ストーリーとして成立するか自己チェックすること

上記の構成・原則・方針に従い、提案書テキストを生成してください。"""

    try:
        gamma_input = chat_completion(
            messages=[{"role": "user", "content": gamma_prompt}],
            max_tokens=6000,
            model="claude-sonnet-4-5-20250929",
        ).strip()
    except Exception as e:
        gamma_input = f"提案テキスト生成エラー: {e}"

    # Phase 1.5: エグゼクティブ批評
    executive_critique = ""
    refinement_applied = False

    if gamma_input and not gamma_input.startswith("提案テキスト生成エラー"):
        if progress_callback:
            progress_callback(40, "エグゼクティブ批評生成中...")

        critique_prompt = f"""# 役割
あなたは日本の大企業（売上1兆円以上）のCTO/CDOクラスの意思決定者です。
数多くのベンダー提案を見てきた経験から、「刺さる提案」と「ゴミ箱行きの提案」を瞬時に見分けます。
あなたは懐疑的で、バズワードや抽象論には厳しく、具体性と実現可能性を重視します。

# タスク
以下の提案書ドラフトを、KDDIの経営層（CTO/CDO/事業部長）の目線で厳しく批評してください。

# 評価軸（各5点満点）
1. **具体性**: 数値・期間・体制が具体的か。「〜等」「〜など」で逃げていないか
2. **KDDI特殊性**: KDDI固有の課題に踏み込んでいるか。他社にも使い回せる汎用提案になっていないか
3. **リスク評価**: 失敗シナリオや前提条件が明示されているか。楽観的すぎないか
4. **ROI現実性**: 試算根拠が論理的か。「〜が期待できる」等の曖昧表現でないか
5. **バズワード汚染度**: DX、AI、共創等のバズワードが実体なく使われていないか（低いほど良い）
6. **意思決定有効性**: この提案書で「Go/No-Go」の判断ができるか

# 提案書ドラフト
{gamma_input[:5000]}

# 出力形式（厳守）
## 総合評価: [A/B/C/D/E]
（A=即採用レベル, B=修正後採用可, C=大幅修正必要, D=方向性から再検討, E=却下）

## 致命的問題点（最大3つ）
- [問題1]: [具体的な問題と、なぜ致命的か]
- [問題2]: ...

## 改善必須事項（最大5つ）
1. [改善事項]: [具体的にどう改善すべきか]
2. ...

## 想定質問（経営層が必ず聞く質問3つ）
1. [質問]: [現状の提案では答えられない理由]
2. ...

## スライド別修正指示
- スライドN: [具体的な修正内容]
（特に問題のあるスライドのみ）"""

        try:
            executive_critique = chat_completion(
                messages=[{"role": "user", "content": critique_prompt}],
                max_tokens=2000,
                model="claude-sonnet-4-5-20250929",
            ).strip()
        except Exception as e:
            print(f"[PROPOSAL] Executive critique failed: {e}")
            executive_critique = ""

        # Phase 1.6: 批評反映リファイン
        if executive_critique:
            if progress_callback:
                progress_callback(50, "批評を反映した改善版を生成中...")

            refine_prompt = f"""# 役割
あなたは提案書ブラッシュアップの専門家です。
エグゼクティブからの厳しい批評を受け、すべての指摘を解消した改善版を作成します。

# タスク
以下の「元の提案書」に対する「エグゼクティブ批評」を踏まえ、批評の全指摘事項を解消した**改善版10スライド**を生成してください。

# 元の提案書
{gamma_input[:5000]}

# エグゼクティブ批評
{executive_critique}

# 改善の原則
- 批評で指摘された「致命的問題点」は必ず解消する
- 「改善必須事項」の全項目に対応する
- 「想定質問」に先回りして答えられる内容にする
- 「スライド別修正指示」は該当スライドに反映する
- 元の提案の良い部分は維持する
- 数値・根拠をより具体的にする
- バズワードを実体のある表現に置き換える

# 出力形式
元の提案書と同じフォーマット（10スライド構成、各スライドにタイトル・メッセージライン・ボディ）で改善版を出力してください。
フォーマットルールは元の提案書と同一です。"""

            try:
                refined_input = chat_completion(
                    messages=[{"role": "user", "content": refine_prompt}],
                    max_tokens=6000,
                    model="claude-sonnet-4-5-20250929",
                ).strip()
                if refined_input and len(refined_input) > 500:
                    gamma_input = refined_input
                    refinement_applied = True
                else:
                    print("[PROPOSAL] Refined output too short, keeping original")
            except Exception as e:
                print(f"[PROPOSAL] Refinement failed, using original: {e}")

    # Phase 2: アプローチ計画生成
    if progress_callback:
        progress_callback(60, "アプローチ計画生成中...")
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
        "has_gamma_api": bool(os.getenv("GAMMA_API_KEY", "")),
        "uvance_solutions_referenced": _count_uvance_references(gamma_input),
        "executive_critique": executive_critique,
        "refinement_applied": refinement_applied,
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


def _compute_proposal_score(metadata: dict) -> int:
    """メタデータからUI表示用スコア(0-100)を算出"""
    base = 50
    uvance_refs = metadata.get("uvance_solutions_referenced", 0)
    base += min(uvance_refs * 8, 24)
    if metadata.get("has_roi"):
        base += 12
    if not metadata.get("has_poc_fatigue"):
        base += 8
    if metadata.get("has_gamma_api"):
        base += 6
    if metadata.get("refinement_applied"):
        base += 5
    return min(base, 100)


def _save_proposal_history(result: dict) -> None:
    """提案履歴を保存"""
    try:
        _PROPOSAL_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if _PROPOSAL_HISTORY_FILE.exists():
            history = json.loads(_PROPOSAL_HISTORY_FILE.read_text(encoding="utf-8"))

        # 履歴エントリ（全文保存 — overlayタブで全文表示するため）
        meta = result["metadata"]
        lightweight_meta = {k: v for k, v in meta.items() if k != "executive_critique"}
        lightweight_meta["refinement_applied"] = meta.get("refinement_applied", False)

        entry = {
            "opportunity_title": result["opportunity_title"],
            "generated_at": result["generated_at"],
            "metadata": lightweight_meta,
            "gamma_input": result["gamma_input"],
            "gamma_input_preview": result["gamma_input"][:300],
            "executive_critique": meta.get("executive_critique", ""),
            "approach_plan": result.get("approach_plan", ""),
            "score": _compute_proposal_score(result.get("metadata", {})),
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

