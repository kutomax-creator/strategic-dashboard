"""
KDDI Intelligence Watcher - Accumulate and persist KDDI news intelligence
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ..config import APP_ROOT, HAS_AI
from ..components.news import fetch_kddi_press_releases, fetch_news_for

_INTEL_FILE = APP_ROOT / "data" / "kddi_intelligence.json"
_MAX_ENTRIES = 1000


def _load_intelligence() -> list[dict]:
    """永続化されたインテリジェンスデータを読み込む"""
    try:
        if _INTEL_FILE.exists():
            return json.loads(_INTEL_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_intelligence(entries: list[dict]) -> None:
    """インテリジェンスデータを永続化（FIFOで最大エントリ数を制限）"""
    try:
        _INTEL_FILE.parent.mkdir(parents=True, exist_ok=True)
        # FIFOで上限を維持
        trimmed = entries[-_MAX_ENTRIES:]
        _INTEL_FILE.write_text(
            json.dumps(trimmed, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[KDDI_WATCHER] Save failed: {e}")


def accumulate_kddi_intelligence() -> dict:
    """KDDIニュース・プレスリリースを取得し、インテリジェンスとして蓄積する。

    Returns:
        dict: {"new_entries": int, "total_entries": int, "themes": list[str]}
    """
    existing = _load_intelligence()
    existing_titles = {e["title"] for e in existing}

    # ニュースソースからフェッチ
    press_releases = fetch_kddi_press_releases(8)
    general_news = fetch_news_for("KDDI", 8)
    wakonx_news = fetch_news_for("KDDI+WAKONX", 5)
    bx_news = fetch_news_for("KDDI+BX+事業変革", 5)

    all_articles = press_releases + general_news + wakonx_news + bx_news
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entries = []
    for article in all_articles:
        title = article.get("title", "")
        if not title or title in existing_titles:
            continue
        existing_titles.add(title)
        entry = {
            "title": title,
            "link": article.get("link", ""),
            "published": article.get("published", ""),
            "description": article.get("description", ""),
            "source": "press" if article in press_releases else "news",
            "accumulated_at": now_str,
        }
        new_entries.append(entry)

    if new_entries:
        existing.extend(new_entries)
        _save_intelligence(existing)

    # テーマ抽出（AIなしでもキーワードベースで簡易抽出）
    themes = _extract_themes(new_entries) if new_entries else []

    return {
        "new_entries": len(new_entries),
        "total_entries": len(existing),
        "themes": themes,
    }


def _extract_themes(entries: list[dict]) -> list[str]:
    """エントリからキーワードベースで主要テーマを抽出"""
    theme_keywords = {
        "AI・生成AI": ["AI", "生成AI", "人工知能", "LLM", "ChatGPT"],
        "5G・通信": ["5G", "通信", "ネットワーク", "OPEN RAN", "基地局"],
        "DX推進": ["DX", "デジタル", "トランスフォーメーション", "WAKONX"],
        "事業変革(BX)": ["BX", "事業変革", "共創", "イノベーション"],
        "データ活用": ["データ", "ビッグデータ", "分析", "データドリブン"],
        "セキュリティ": ["セキュリティ", "ゼロトラスト", "サイバー"],
        "サステナビリティ": ["カーボン", "ESG", "サステナ", "グリーン"],
        "金融・決済": ["金融", "決済", "フィンテック", "au PAY"],
        "PoC疲れ": ["PoC", "実証実験", "PoC疲れ", "PoC死"],
    }

    found_themes = []
    all_text = " ".join(e.get("title", "") + " " + e.get("description", "") for e in entries)
    for theme, keywords in theme_keywords.items():
        if any(kw in all_text for kw in keywords):
            found_themes.append(theme)

    return found_themes


def get_intelligence_summary(max_entries: int = 20) -> str:
    """蓄積データからAIプロンプト用サマリーを生成"""
    entries = _load_intelligence()
    if not entries:
        return "KDDIインテリジェンスデータなし（初回蓄積が必要）"

    # 最新エントリをソート
    recent = sorted(entries, key=lambda e: e.get("accumulated_at", ""), reverse=True)[:max_entries]

    lines = ["# KDDI最新インテリジェンス\n"]
    for i, entry in enumerate(recent, 1):
        source_tag = "[PR]" if entry.get("source") == "press" else "[NEWS]"
        desc = entry.get("description", "")
        desc_text = f" — {desc[:100]}" if desc else ""
        lines.append(f"{i}. {source_tag} {entry['title']}{desc_text}")
        if entry.get("published"):
            lines.append(f"   発行日: {entry['published']}")

    # テーマサマリー
    themes = _extract_themes(recent)
    if themes:
        lines.append(f"\n## 検出テーマ: {', '.join(themes)}")

    lines.append(f"\n（蓄積データ総数: {len(entries)}件、表示: 最新{len(recent)}件）")
    return "\n".join(lines)


def get_poc_fatigue_references() -> list[dict]:
    """POC疲れ関連の蓄積エントリを返却"""
    entries = _load_intelligence()
    poc_keywords = ["PoC", "実証実験", "PoC疲れ", "PoC死", "概念実証", "パイロット"]
    results = []
    for entry in entries:
        text = entry.get("title", "") + " " + entry.get("description", "")
        if any(kw in text for kw in poc_keywords):
            results.append(entry)
    return results
