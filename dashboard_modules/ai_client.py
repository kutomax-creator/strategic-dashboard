"""
AI Client Abstraction Layer
===========================
環境変数 AI_PROVIDER で切り替え:
  - "anthropic"（デフォルト）: Anthropic Claude API
  - "fujitsu": 富士通社内 GPT-5.1 API
"""
from __future__ import annotations

import os

AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").lower()

# --- Anthropic ---
_anthropic_client = None

try:
    import anthropic as _anthropic_mod
    _HAS_ANTHROPIC = True
except Exception:
    _HAS_ANTHROPIC = False

# --- Fujitsu ---
_FUJITSU_ENDPOINT = (
    "https://api.ai-service.global.fujitsu.com"
    "/ai-foundation/chat-ai/gpt/gpt-5.1"
)
_FUJITSU_API_KEY = os.getenv("FUJITSU_AI_KEY", "")
_HAS_FUJITSU = bool(_FUJITSU_API_KEY)

# --- 公開フラグ ---
HAS_AI: bool = (
    (_HAS_ANTHROPIC if AI_PROVIDER == "anthropic" else False)
    or (_HAS_FUJITSU if AI_PROVIDER == "fujitsu" else False)
)

# モデルマッピング（Anthropic → Fujitsu）
_MODEL_MAP_FUJITSU: dict[str, str] = {
    "claude-haiku-4-5-20251001": "gpt-5.1",
    "claude-sonnet-4-5-20250929": "gpt-5.1",
}


def chat_completion(
    messages: list[dict],
    max_tokens: int,
    system: str | None = None,
    model: str | None = None,
) -> str:
    """AI APIへチャット補完リクエストを送信し、テキストを返す。

    Parameters
    ----------
    messages : list[dict]
        {"role": "user"|"assistant", "content": "..."} のリスト
    max_tokens : int
        最大トークン数
    system : str | None
        システムプロンプト（任意）
    model : str | None
        使用モデル（省略時はプロバイダのデフォルト）

    Returns
    -------
    str  応答テキスト
    """
    if AI_PROVIDER == "fujitsu":
        return _call_fujitsu(messages, max_tokens, system=system, model=model)
    else:
        return _call_anthropic(messages, max_tokens, system=system, model=model)


def _call_anthropic(
    messages: list[dict],
    max_tokens: int,
    *,
    system: str | None = None,
    model: str | None = None,
) -> str:
    global _anthropic_client
    if not _HAS_ANTHROPIC:
        raise RuntimeError("Anthropic library is not available")

    if _anthropic_client is None:
        _anthropic_client = _anthropic_mod.Anthropic()

    kwargs: dict = {
        "model": model or "claude-sonnet-4-5-20250929",
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    response = _anthropic_client.messages.create(**kwargs)
    return response.content[0].text


def _call_fujitsu(
    messages: list[dict],
    max_tokens: int,
    *,
    system: str | None = None,
    model: str | None = None,
) -> str:
    import requests

    if not _FUJITSU_API_KEY:
        raise RuntimeError("FUJITSU_AI_KEY is not set")

    # モデル名を変換
    fujitsu_model = _MODEL_MAP_FUJITSU.get(model, "gpt-5.1") if model else "gpt-5.1"

    # メッセージ構築（systemはmessages配列の先頭に含める）
    api_messages: list[dict] = []
    if system:
        api_messages.append({"role": "system", "content": system})
    api_messages.extend(messages)

    payload = {
        "model": fujitsu_model,
        "max_tokens": max_tokens,
        "messages": api_messages,
    }

    headers = {
        "api-key": _FUJITSU_API_KEY,
        "Content-Type": "application/json",
    }

    resp = requests.post(_FUJITSU_ENDPOINT, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
