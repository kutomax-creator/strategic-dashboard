"""
Gamma API Client - Generate presentations via Gamma.app API
Docs: https://developers.gamma.app/docs/getting-started
API v1.0 (GA since 2025-11-05)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import requests

from ..config import GAMMA_API_KEY

_BASE_URL = "https://public-api.gamma.app/v1.0"
_POLL_INTERVAL = 5  # seconds
_MAX_POLL_TIME = 300  # 5 minutes


@dataclass
class GammaGeneration:
    generation_id: str = ""
    status: str = ""  # "pending", "completed", "failed"
    gamma_url: str = ""
    error: str = ""
    credits_deducted: int = 0
    credits_remaining: int = 0
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
    tone: str = "KDDI経営層向けプロフェッショナル",
    audience: str = "KDDI CTO/CDO/事業部長クラスのエグゼクティブ",
) -> GammaGeneration:
    """Gamma APIで提案書生成を開始する（非同期）。

    Parameters
    ----------
    input_text : str
        AIが生成した提案テキスト（スライド構成）
    num_cards : int
        スライド枚数 (Pro: 1-60)
    language : str
        出力言語コード
    tone : str
        トーン説明（最大500文字）
    audience : str
        対象読者の説明

    Returns
    -------
    GammaGeneration  生成ジョブ情報
    """
    if not GAMMA_API_KEY:
        return GammaGeneration(error="GAMMA_API_KEY is not configured")

    payload = {
        "inputText": input_text,
        "textMode": "generate",
        "format": "presentation",
        "numCards": num_cards,
        "language": language,
        "textOptions": {
            "amount": "medium",
            "tone": tone,
            "audience": audience,
        },
        "imageOptions": {
            "source": "pictographic",
        },
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
            generation_id=data.get("generationId", ""),
            status="pending",
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
        create_presentationで取得したgenerationId

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

        credits = data.get("credits", {})
        return GammaGeneration(
            generation_id=generation_id,
            status=data.get("status", "unknown"),
            gamma_url=data.get("gammaUrl", ""),
            credits_deducted=credits.get("deducted", 0),
            credits_remaining=credits.get("remaining", 0),
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
        return GammaGeneration(error="No generationId returned")

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
