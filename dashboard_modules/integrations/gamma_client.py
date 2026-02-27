"""
Gamma API Client - Generate presentations via Gamma.app API
Docs: https://gamma.app/docs/api
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import requests

from ..config import GAMMA_API_KEY

_BASE_URL = "https://api.gamma.app/v1"
_POLL_INTERVAL = 5  # seconds
_MAX_POLL_TIME = 300  # 5 minutes


@dataclass
class GammaGeneration:
    generation_id: str = ""
    status: str = ""  # "pending", "in_progress", "completed", "failed"
    gamma_url: str = ""
    download_url: str = ""
    error: str = ""
    card_count: int = 0
    metadata: dict = field(default_factory=dict)


def _headers() -> dict:
    return {
        "X-API-KEY": GAMMA_API_KEY,
        "Content-Type": "application/json",
    }


def create_presentation(
    input_text: str,
    num_cards: int = 10,
    language: str = "ja",
    tone: str = "professional",
    audience: str = "executive",
    export_as: str = "pptx",
) -> GammaGeneration:
    """Gamma APIで提案書生成を開始する（非同期）。

    Parameters
    ----------
    input_text : str
        AIが生成した提案テキスト（スライド構成）
    num_cards : int
        スライド枚数
    language : str
        出力言語
    tone : str
        トーン（professional, casual等）
    audience : str
        対象者
    export_as : str
        エクスポート形式

    Returns
    -------
    GammaGeneration  生成ジョブ情報
    """
    if not GAMMA_API_KEY:
        return GammaGeneration(error="GAMMA_API_KEY is not configured")

    payload = {
        "input_text": input_text,
        "num_cards": num_cards,
        "language": language,
        "tone": tone,
        "audience": audience,
        "export_as": export_as,
    }

    try:
        resp = requests.post(
            f"{_BASE_URL}/generations",
            json=payload,
            headers=_headers(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return GammaGeneration(
            generation_id=data.get("id", ""),
            status=data.get("status", "pending"),
            metadata=data,
        )
    except requests.HTTPError as e:
        error_detail = ""
        try:
            error_detail = e.response.json().get("message", str(e))
        except Exception:
            error_detail = str(e)
        return GammaGeneration(error=f"Gamma API error: {error_detail}")
    except Exception as e:
        return GammaGeneration(error=f"Request failed: {e}")


def poll_generation(generation_id: str) -> GammaGeneration:
    """生成ジョブのステータスをポーリングする。

    Parameters
    ----------
    generation_id : str
        create_presentationで取得したID

    Returns
    -------
    GammaGeneration  最新ステータス
    """
    if not GAMMA_API_KEY:
        return GammaGeneration(error="GAMMA_API_KEY is not configured")

    try:
        resp = requests.get(
            f"{_BASE_URL}/generations/{generation_id}",
            headers=_headers(),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return GammaGeneration(
            generation_id=generation_id,
            status=data.get("status", "unknown"),
            gamma_url=data.get("gamma_url", ""),
            download_url=data.get("download_url", ""),
            card_count=data.get("card_count", 0),
            metadata=data,
        )
    except Exception as e:
        return GammaGeneration(
            generation_id=generation_id,
            error=f"Poll failed: {e}",
        )


def generate_and_wait(
    input_text: str,
    num_cards: int = 10,
    callback=None,
) -> GammaGeneration:
    """提案書生成を開始し、完了まで待機する。

    Parameters
    ----------
    input_text : str
        スライド構成テキスト
    num_cards : int
        スライド枚数
    callback : callable | None
        進捗コールバック (status_text: str) -> None

    Returns
    -------
    GammaGeneration  完了結果
    """
    if callback:
        callback("Gamma APIへ送信中...")

    gen = create_presentation(input_text, num_cards=num_cards)
    if gen.error:
        return gen

    if not gen.generation_id:
        return GammaGeneration(error="No generation ID returned")

    if callback:
        callback("スライド生成中...")

    elapsed = 0
    while elapsed < _MAX_POLL_TIME:
        time.sleep(_POLL_INTERVAL)
        elapsed += _POLL_INTERVAL

        result = poll_generation(gen.generation_id)
        if result.error:
            return result

        if callback:
            callback(f"スライド生成中... ({elapsed}s)")

        if result.status == "completed":
            return result
        elif result.status == "failed":
            return GammaGeneration(
                generation_id=gen.generation_id,
                status="failed",
                error=result.metadata.get("error", "Generation failed"),
            )

    return GammaGeneration(
        generation_id=gen.generation_id,
        status="timeout",
        error=f"Generation timed out after {_MAX_POLL_TIME}s",
    )


def is_available() -> bool:
    """Gamma APIが利用可能か"""
    return bool(GAMMA_API_KEY)
