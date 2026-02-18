"""
Strategy Chat - AI-powered chat for strategic discussions
"""
import streamlit as st
from ..config import HAS_AI
from ..ai_client import chat_completion
from .context import get_active_context_data

# ─── Strategy Chat ────────────────────────────────────────────────
def get_chat_response(user_message: str, chat_history: list[dict]) -> str:
    """戦略議論チャットのレスポンスを生成"""
    if not HAS_AI:
        return "エラー: AI APIが利用できません。"

    try:
        # コンテキストデータを取得
        context_data = get_active_context_data()
        context_section = f"\n\n# アップロード済みコンテキスト情報\n{context_data}" if context_data else ""

        # レポートデータを取得（もしあれば）
        report_data = st.session_state.get("report_data_cache", {})
        report_titles = [rd.get("title", "") for rd in report_data.values() if rd.get("title")]
        reports_section = ""
        if report_titles:
            reports_section = f"\n\n# 生成済みAIレポート\n" + "\n".join(f"- {t}" for t in report_titles[:5])

        system_prompt = f"""あなたは富士通のKDDI担当アカウントストラテジストのアシスタントです。

# あなたの役割
- KDDI（特にWAKONX/KDDI BX）向けのビジネス戦略について議論・ブレスト
- 生成されたAIレポートの内容について深掘り質問に回答
- 提案書作成のアイデア出し
- 市場動向・競合分析のディスカッション
- ダッシュボードの活用方法についてアドバイス

# 富士通Uvanceソリューション（参考）
- Digital Shifts: DX推進コンサル、業務改革
- Hybrid IT: マルチクラウド統合、仮想化基盤
- Sustainable Manufacturing: 製造DX、工場IoT
- Kozuchi AI Platform: AI/ML基盤、生成AI活用
- Consumer Experience: 顧客体験向上、デジタルマーケ
- Cyber Security: セキュリティソリューション
{context_section}{reports_section}

# 応答スタイル
- 簡潔で実践的なアドバイス
- 必要に応じて箇条書きで整理
- KDDIの経営課題・戦略方針を意識した提案
- 具体的なアクション案を含める
"""

        # メッセージ履歴を構築
        messages = []
        for msg in chat_history[-10:]:  # 最新10件まで
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        messages.append({
            "role": "user",
            "content": user_message
        })

        return chat_completion(
            messages=messages,
            max_tokens=2000,
            system=system_prompt,
            model="claude-sonnet-4-5-20250929",
        )
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"


