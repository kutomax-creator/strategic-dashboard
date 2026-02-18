"""
Image processing utilities
"""
from __future__ import annotations

import os
import base64
import io
from PIL import Image
from ..config import ASSET_DIR


def load_image_b64(filename: str, max_size: int = 1000) -> str | None:
    """画像をBase64エンコードして返す"""
    path = os.path.join(ASSET_DIR, filename)
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path)
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        buf = io.BytesIO()
        if img.mode == "RGBA":
            img.save(buf, format="WEBP", quality=70)
        else:
            img = img.convert("RGB")
            img.save(buf, format="WEBP", quality=70)
        return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def img_tag(data_uri: str | None, cls: str) -> str:
    """画像タグまたはプレースホルダーを返す"""
    if data_uri:
        return f'<img src="{data_uri}" class="{cls}">'
    return f'<div class="{cls} placeholder"></div>'


# プリロード画像
IMG_BG = load_image_b64("bg_frame.png")
IMG_MAP = load_image_b64("map_hologram.png")
