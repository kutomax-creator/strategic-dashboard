"""
Weekly Hypothesis Proposal Scheduler
Streamlit起動時チェック方式で週次自動生成を管理
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from ..config import APP_ROOT

_SCHEDULE_FILE = APP_ROOT / "data" / "weekly_schedule.json"
_PROPOSALS_DIR = APP_ROOT / "static" / "proposals"
_GENERATION_INTERVAL_DAYS = 7


@dataclass
class WeeklyResult:
    success: bool = False
    opportunity_title: str = ""
    gamma_input: str = ""
    approach_plan: str = ""
    gamma_url: str = ""
    generated_at: str = ""
    error: str = ""
    metadata: dict = field(default_factory=dict)


def _load_schedule() -> dict:
    try:
        if _SCHEDULE_FILE.exists():
            return json.loads(_SCHEDULE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_schedule(data: dict) -> None:
    try:
        _SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _SCHEDULE_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        print(f"[SCHEDULER] Save failed: {e}")


def is_generation_due() -> bool:
    """週次生成の期限が来ているかチェック"""
    schedule = _load_schedule()
    last_gen = schedule.get("last_generation")
    if not last_gen:
        return True  # 一度も生成していない
    try:
        last_dt = datetime.fromisoformat(last_gen)
        return datetime.now() - last_dt >= timedelta(days=_GENERATION_INTERVAL_DAYS)
    except Exception:
        return True


def days_since_last_generation() -> int | None:
    """前回生成からの経過日数（生成歴なしならNone）"""
    schedule = _load_schedule()
    last_gen = schedule.get("last_generation")
    if not last_gen:
        return None
    try:
        last_dt = datetime.fromisoformat(last_gen)
        return (datetime.now() - last_dt).days
    except Exception:
        return None


def run_weekly_generation(
    kddi_news: tuple | list,
    fujitsu_news: tuple | list,
    progress_callback=None,
) -> WeeklyResult:
    """週次パイプライン: インテリジェンス蓄積 → 仮説提案生成 → Gamma送信（設定時）

    Parameters
    ----------
    kddi_news : tuple | list
        KDDIニュースタイトル一覧
    fujitsu_news : tuple | list
        富士通ニュースタイトル一覧
    progress_callback : callable | None
        (progress_pct: int, status_text: str) -> None

    Returns
    -------
    WeeklyResult
    """
    now = datetime.now()

    # Step 1: インテリジェンス蓄積
    if progress_callback:
        progress_callback(10, "KDDIインテリジェンス蓄積中...")
    try:
        from ..data.kddi_watcher import accumulate_kddi_intelligence
        intel_result = accumulate_kddi_intelligence()
        print(f"[SCHEDULER] Intelligence accumulated: {intel_result['new_entries']} new entries")
    except Exception as e:
        print(f"[SCHEDULER] Intelligence accumulation failed: {e}")

    # Step 2: オポチュニティタイトル選定（最新ニュースから自動選定）
    if progress_callback:
        progress_callback(20, "オポチュニティ分析中...")

    opportunity_title = _select_opportunity(kddi_news, fujitsu_news)
    report_content = _build_report_context(kddi_news, fujitsu_news)

    # Step 3: 仮説提案生成（内部で30→40→50→60%に進捗）
    if progress_callback:
        progress_callback(25, "仮説提案書生成中...")

    from .proposals import generate_hypothesis_proposal
    proposal = generate_hypothesis_proposal(
        opportunity_title=opportunity_title,
        report_content=report_content,
        kddi_news=kddi_news,
        fujitsu_news=fujitsu_news,
        progress_callback=progress_callback,
    )

    if not proposal.get("gamma_input"):
        return WeeklyResult(
            success=False,
            opportunity_title=opportunity_title,
            error="提案テキストの生成に失敗しました",
            generated_at=now.isoformat(),
        )

    # Step 4: Gamma API送信（利用可能な場合）
    gamma_url = ""
    gamma_error = ""
    from ..integrations.gamma_client import is_available as gamma_available, generate_and_wait
    if gamma_available():
        if progress_callback:
            progress_callback(70, "Gamma APIでスライド生成中...")
        try:
            gamma_result = generate_and_wait(
                proposal["gamma_input"],
                callback=lambda msg: progress_callback(70, msg) if progress_callback else None,
            )
            if gamma_result.gamma_url:
                gamma_url = gamma_result.gamma_url
            elif gamma_result.error:
                gamma_error = gamma_result.error
                print(f"[SCHEDULER] Gamma generation failed: {gamma_error}")
        except Exception as e:
            gamma_error = str(e)
            print(f"[SCHEDULER] Gamma API error: {e}")
    else:
        gamma_error = "GAMMA_API_KEY not configured"

    # Step 5: 結果保存
    if progress_callback:
        progress_callback(90, "結果を保存中...")

    merged_meta = dict(proposal["metadata"])
    if gamma_error:
        merged_meta["gamma_error"] = gamma_error

    result = WeeklyResult(
        success=True,
        opportunity_title=opportunity_title,
        gamma_input=proposal["gamma_input"],
        approach_plan=proposal["approach_plan"],
        gamma_url=gamma_url,
        generated_at=now.isoformat(),
        metadata=merged_meta,
    )

    _save_generation_result(result)

    if progress_callback:
        progress_callback(100, "完了!")

    return result


def run_manual_generation(
    opportunity_title: str,
    report_content: str,
    kddi_news: tuple | list = (),
    fujitsu_news: tuple | list = (),
    progress_callback=None,
) -> WeeklyResult:
    """手動トリガーの仮説提案生成

    Parameters
    ----------
    opportunity_title : str
        オポチュニティ名
    report_content : str
        レポート内容
    progress_callback : callable | None
        (progress_pct: int, status_text: str) -> None

    Returns
    -------
    WeeklyResult
    """
    now = datetime.now()

    # インテリジェンス蓄積
    if progress_callback:
        progress_callback(10, "KDDIインテリジェンス蓄積中...")
    try:
        from ..data.kddi_watcher import accumulate_kddi_intelligence
        accumulate_kddi_intelligence()
    except Exception:
        pass

    # 仮説提案生成（内部で30→40→50→60%に進捗）
    if progress_callback:
        progress_callback(25, "仮説提案書生成中...")

    from .proposals import generate_hypothesis_proposal
    proposal = generate_hypothesis_proposal(
        opportunity_title=opportunity_title,
        report_content=report_content,
        kddi_news=kddi_news,
        fujitsu_news=fujitsu_news,
        progress_callback=progress_callback,
    )

    if not proposal.get("gamma_input"):
        return WeeklyResult(
            success=False,
            opportunity_title=opportunity_title,
            error="提案テキストの生成に失敗しました",
            generated_at=now.isoformat(),
        )

    # Gamma API送信（利用可能な場合）
    gamma_url = ""
    gamma_error = ""
    from ..integrations.gamma_client import is_available as gamma_available, generate_and_wait as gamma_gen
    if gamma_available():
        if progress_callback:
            progress_callback(70, "Gamma APIでスライド生成中...")
        try:
            gamma_result = gamma_gen(
                proposal["gamma_input"],
                callback=lambda msg: progress_callback(70, msg) if progress_callback else None,
            )
            if gamma_result.gamma_url:
                gamma_url = gamma_result.gamma_url
            elif gamma_result.error:
                gamma_error = gamma_result.error
                print(f"[MANUAL_GEN] Gamma error: {gamma_error}")
        except Exception as e:
            gamma_error = str(e)
            print(f"[MANUAL_GEN] Gamma API error: {e}")
    else:
        gamma_error = "GAMMA_API_KEY not configured"

    if progress_callback:
        progress_callback(90, "結果を保存中...")

    merged_meta = dict(proposal["metadata"])
    if gamma_error:
        merged_meta["gamma_error"] = gamma_error

    result = WeeklyResult(
        success=True,
        opportunity_title=opportunity_title,
        gamma_input=proposal["gamma_input"],
        approach_plan=proposal["approach_plan"],
        gamma_url=gamma_url,
        generated_at=now.isoformat(),
        metadata=merged_meta,
    )

    _save_generation_result(result)

    if progress_callback:
        progress_callback(100, "完了!")

    return result


def _select_opportunity(kddi_news: tuple | list, fujitsu_news: tuple | list) -> str:
    """ニュースから最適なオポチュニティタイトルを自動選定"""
    # キーワードスコアリングで最も関連性の高いニュースを選択
    from ..config import HAS_AI
    from ..ai_client import chat_completion

    if HAS_AI and kddi_news:
        try:
            news_text = "\n".join(f"- {t}" for t in list(kddi_news)[:10])
            result = chat_completion(
                messages=[{
                    "role": "user",
                    "content": f"""以下のKDDI関連ニュースから、富士通UVANCEで提案できる最も有望なオポチュニティを1つ選び、
提案書のタイトル（30-50文字）を生成してください。タイトルのみ出力してください。

ニュース:
{news_text}""",
                }],
                max_tokens=100,
                model="claude-haiku-4-5-20251001",
            ).strip()
            return result
        except Exception:
            pass

    # フォールバック: 最初のニュースタイトルベース
    if kddi_news:
        first = list(kddi_news)[0]
        return f"KDDI×UVANCE: {first[:40]}"
    return "KDDI DX推進×UVANCE統合ソリューション提案"


def _build_report_context(kddi_news: tuple | list, fujitsu_news: tuple | list) -> str:
    """ニュースからレポートコンテキストを構築"""
    lines = ["# KDDI最新動向"]
    for t in list(kddi_news)[:8]:
        lines.append(f"- {t}")
    lines.append("\n# 富士通最新動向")
    for t in list(fujitsu_news)[:8]:
        lines.append(f"- {t}")
    return "\n".join(lines)


def _save_generation_result(result: WeeklyResult) -> None:
    """生成結果をスケジュールファイルと履歴に保存"""
    schedule = _load_schedule()
    schedule["last_generation"] = result.generated_at
    schedule["last_opportunity"] = result.opportunity_title
    schedule["last_gamma_url"] = result.gamma_url

    # 履歴
    history = schedule.get("history", [])
    history.append({
        "opportunity_title": result.opportunity_title,
        "generated_at": result.generated_at,
        "gamma_url": result.gamma_url,
        "success": result.success,
        "approach_plan": result.approach_plan,
        "gamma_input": result.gamma_input,
        "executive_critique": result.metadata.get("executive_critique", ""),
        "score": _compute_display_score(result.metadata),
    })
    schedule["history"] = history[-20:]  # 最大20件

    _save_schedule(schedule)

    # 提案テキストをファイル保存
    if result.gamma_input:
        try:
            _PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            proposal_file = _PROPOSALS_DIR / f"proposal_{ts}.md"
            content = f"# {result.opportunity_title}\n\n"
            content += f"Generated: {result.generated_at}\n\n"
            if result.gamma_url:
                content += f"Gamma URL: {result.gamma_url}\n\n"
            content += "---\n\n"
            content += result.gamma_input
            # 批評セクション追加
            critique_text = result.metadata.get("executive_critique", "")
            if critique_text:
                content += "\n\n---\n\n# Executive Critique\n\n"
                content += critique_text
            content += "\n\n---\n\n# Approach Plan\n\n"
            content += result.approach_plan
            proposal_file.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"[SCHEDULER] Proposal file save failed: {e}")


def _compute_display_score(metadata: dict) -> int:
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


def get_generation_history() -> list[dict]:
    """生成履歴を返す"""
    schedule = _load_schedule()
    return schedule.get("history", [])
