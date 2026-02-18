"""
Dashboard Configuration
"""
import os
from pathlib import Path

# アプリルートディレクトリ（dashboard_modules の親）
APP_ROOT = Path(__file__).resolve().parent.parent

# AI プロバイダ判定
_AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").lower()

# APIキー設定（Anthropic使用時のみ）
if _AI_PROVIDER == "anthropic":
    ANTHROPIC_API_KEY = os.getenv(
        "ANTHROPIC_API_KEY",
        "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"
    )
    os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
else:
    ANTHROPIC_API_KEY = ""

# Anthropic利用可否チェック
try:
    import anthropic
    HAS_ANTHROPIC = True
except Exception:
    HAS_ANTHROPIC = False

# AI利用可否チェック（AnthropicまたはFujitsu社内APIのいずれかが使えればTrue）
from .ai_client import HAS_AI  # noqa: E402

# Asset directory
ASSET_DIR = str(APP_ROOT / "assets")

# Page config
PAGE_CONFIG = {
    "page_title": "Strategic Dashboard",
    "page_icon": "🛡️",
    "layout": "wide",
    "initial_sidebar_state": "collapsed",
}
