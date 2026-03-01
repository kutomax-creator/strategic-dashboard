"""
AI Strategic Opportunities - Generate business opportunities
"""
from __future__ import annotations

import os
import json
import re
from pathlib import Path
from datetime import datetime
import streamlit as st
from ..config import HAS_AI
from ..ai_client import chat_completion

# ─── AI Strategic Opportunities ──────────────────────────────────
STATIC_DIR = str(Path(__file__).resolve().parent.parent.parent / "static")
os.makedirs(STATIC_DIR, exist_ok=True)


MOCK_OPPORTUNITIES = [
    {"title": "WAKONX×Kozuchi生成AI 法人DX加速プラットフォーム", "uvance_area": "Digital Shifts", "score": 94, "score_reason": "WAKONXの生成AI推進と完全合致。法人顧客へのAI導入支援で即座に提案可能"},
    {"title": "KDDI BX×Uvance共創プログラム 事業変革ワークショップ", "uvance_area": "Digital Shifts", "score": 88, "score_reason": "KDDI BXの共創ニーズに直結。Uvance共創メソッドで差別化できる"},
    {"title": "WAKONX×Hybrid IT プライベート5G統合インフラ", "uvance_area": "Hybrid IT", "score": 82, "score_reason": "WAKONXの5G法人展開と技術親和性高。既存インフラ刷新需要あり"},
    {"title": "KDDI BX×Data e-TRUST データ利活用基盤構築", "uvance_area": "Digital Shifts", "score": 76, "score_reason": "BXのデータドリブン経営推進に合致。ただし競合他社の先行あり"},
    {"title": "WAKONX×ゼロトラスト セキュリティ統合提案", "uvance_area": "Digital Shifts", "score": 68, "score_reason": "DXセキュリティは重要だが、既存契約の切替ハードルあり"},
]


def _get_past_titles(n: int = 10) -> list[str]:
    """直近n件の提案タイトルを取得"""
    try:
        from .weekly_scheduler import get_generation_history
        return [h["opportunity_title"] for h in get_generation_history()[-n:] if h.get("opportunity_title")]
    except Exception:
        return []


def _get_underrepresented_verticals() -> list[str]:
    """過去提案で少ないバーティカルを特定"""
    from collections import Counter
    all_verticals = {"Digital Shifts", "Hybrid IT", "Healthy Living", "Trusted Society"}

    try:
        from .weekly_scheduler import get_generation_history
        history = get_generation_history()[-10:]
        past_verticals = []
        for h in history:
            meta = h.get("metadata", {})
            if isinstance(meta, dict) and meta.get("vertical"):
                past_verticals.append(meta["vertical"])
            # uvance_area fallback
            elif h.get("uvance_area"):
                past_verticals.append(h["uvance_area"])
        counts = Counter(past_verticals)
    except Exception:
        counts = Counter()

    # 出現回数が少ない順にソート
    return sorted(all_verticals, key=lambda v: counts.get(v, 0))


@st.cache_data(ttl=7200)
def _fetch_opportunities_api(kddi_news: tuple[str, ...], fujitsu_news: tuple[str, ...],
                             kddi_press: tuple[str, ...] = (), fujitsu_press: tuple[str, ...] = ()) -> list[dict]:
    """Claude APIでオポチュニティを取得（API有効時のみ呼ばれる）。"""
    if not kddi_news and not fujitsu_news:
        return []
    try:
        kddi_text = "\n".join(f"- {t}" for t in kddi_news) if kddi_news else "（取得なし）"
        fujitsu_text = "\n".join(f"- {t}" for t in fujitsu_news) if fujitsu_news else "（取得なし）"
        kddi_press_text = "\n".join(f"- {t}" for t in kddi_press) if kddi_press else "（取得なし）"
        fujitsu_press_text = "\n".join(f"- {t}" for t in fujitsu_press) if fujitsu_press else "（取得なし）"

        # 過去提案タイトル・バーティカル情報を収集
        past_titles = _get_past_titles()
        underrepresented = _get_underrepresented_verticals()
        past_titles_text = "\n".join(f"- {t}" for t in past_titles) if past_titles else "（過去提案なし）"
        underrepresented_text = ", ".join(underrepresented[:3]) if underrepresented else "特になし"

        # 業界・競合コンテキスト取得
        from ..data.industry_context import get_industry_context_for_proposal, get_kddi_strategic_context
        industry_ctx = get_industry_context_for_proposal("Digital Shifts")  # 汎用的に取得
        kddi_strategy = get_kddi_strategic_context()

        text = chat_completion(
            messages=[{
                "role": "user",
                "content": f"""あなたは富士通のKDDI担当アカウントストラテジストです。**WAKONX（KDDIのDX事業ブランド）とKDDI BX（ビジネス変革部門）**での共創ビジネス創出がミッションです。

以下のKDDI（特にWAKONX/BX）と富士通の最新動向・公式プレスリリースをクロス分析し、**期待度スコアの高い上位3件のビジネスオポチュニティのみ**抽出してください。

【KDDI（WAKONX/BX重点）の最新動向】
{kddi_text}

【KDDIプレスリリース（公式発表）】
{kddi_press_text}

【富士通・Uvanceの最新動向】
{fujitsu_text}

【富士通プレスリリース（UVANCE含む）】
{fujitsu_press_text}

【KDDI中期経営戦略】
{kddi_strategy[:1500]}

【競合・業界トレンド】
{industry_ctx[:1500]}

**重要:**
- KDDIプレスリリースから読み取れる課題・ニーズを仮説として活用
- 富士通プレスリリースのUVANCEソリューションとの交差点を見出す
- WAKONX（DX推進、AI活用、データ利活用）との連携機会を最優先
- KDDI BX（事業変革、共創、新規事業）との協業機会を重視
- 具体的な提案アクション（どのUvanceソリューションで何を提案するか）を明記

# バリエーション要求（必ず遵守）
- 3件のオポチュニティは必ず**異なるUvanceバーティカル**から選ぶこと
- 以下のバーティカルから最低2つ含めること: {underrepresented_text}
- Uvanceバーティカル: Digital Shifts, Hybrid IT, Healthy Living, Trusted Society
- 過去に生成済みのテーマと重複しないこと

# 過去の提案テーマ（重複回避）
{past_titles_text}

以下のJSON形式で出力してください。他のテキストは一切不要です。JSONのみ出力してください。

[
  {{"title": "オポチュニティのタイトル（WAKONX/BXとの具体的連携内容）", "uvance_area": "関連するUvance領域", "score": 85, "score_reason": "スコアの根拠（WAKONX/BXでの実現可能性とインパクト）"}},
  ...
]

scoreは0-100のAI推奨度スコアです。WAKONX/BXでの実現可能性、事業インパクト、緊急度を総合評価してください。スコアの高い順に並べてください。"""
            }],
            max_tokens=800,
            model="claude-haiku-4-5-20251001",
        ).strip()
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return []
    except Exception:
        return []


def generate_opportunities(kddi_news: tuple[str, ...], fujitsu_news: tuple[str, ...],
                           kddi_press: tuple[str, ...] = (), fujitsu_press: tuple[str, ...] = ()) -> list[dict]:
    """オポチュニティ一覧を返す。API未設定時はモックデータ。"""
    if not HAS_AI:
        return MOCK_OPPORTUNITIES
    result = _fetch_opportunities_api(kddi_news, fujitsu_news, kddi_press, fujitsu_press)
    if not result:
        # キャッシュに空リストが残っている場合クリアしてリトライ
        _fetch_opportunities_api.clear()
        result = _fetch_opportunities_api(kddi_news, fujitsu_news, kddi_press, fujitsu_press)
    return result if result else MOCK_OPPORTUNITIES


@st.cache_data(ttl=7200)
def generate_detail_report(opportunity_title: str, kddi_news: tuple[str, ...], fujitsu_news: tuple[str, ...],
                           kddi_press: tuple[str, ...] = (), fujitsu_press: tuple[str, ...] = ()) -> str | None:
    """指定オポチュニティの詳細戦略レポートHTMLを生成し、staticフォルダに保存。ファイル名を返す。"""
    mock_mode = not HAS_AI
    if mock_mode:
        report_text = f"""■ 想定仮説
＜KDDIの課題認識＞ KDDIのプレスリリースから、法人DX領域での競争激化と5G/AI活用による新サービス創出への強いニーズが読み取れる。
＜潜在ニーズ＞ {opportunity_title}に関連して、WAKONX推進におけるパートナーエコシステム強化、データ利活用基盤の高度化が急務と推察される。
＜仮説＞ KDDIは自社単独でのDXソリューション開発に限界を感じており、Uvanceのようなクロスインダストリー知見を持つパートナーとの共創を模索している。

■ 解決の方向性・コンセプト
＜UVANCE×KDDI戦略の交差点＞ 富士通UvanceのDigital Shifts/Hybrid ITと、KDDIのWAKONXブランドが目指す「通信×DX」の融合領域に最大の共創機会がある。
＜コンセプト＞ 「WAKONX × Uvance 共創DXプラットフォーム」— KDDIの通信インフラ・顧客基盤と富士通のクロスインダストリーDX知見を統合し、法人顧客の事業変革を加速する。
＜アプローチ＞ Kozuchi AIプラットフォームをWAKONXサービス基盤に統合し、業界特化型AIソリューションを共同開発・展開する。

■ 提案内容
＜ソリューション構成＞ Uvance Hybrid ITのマルチクラウド統合管理基盤をKDDI法人向けクラウドサービスに連携。Kozuchi AI Platformによるネットワーク最適化・予知保全機能を付加。
＜対象部門＞ KDDIソリューション事業本部・WAKONX推進室・法人営業部門
＜展開シナリオ＞ Phase1: 製造業向けローカル5G＋エッジAIパッケージのPoC、Phase2: 3業種横展開、Phase3: WAKONX標準メニュー化
＜想定案件規模＞ 初年度8-12億円、3年間で30億円規模。

■ 期待される効果
＜定量効果＞ KDDI法人顧客のDX導入率20%向上。運用コスト年間1.5億円削減。新規法人契約獲得による売上増: 年間5-8億円。
＜定性効果＞ WAKONXブランドの差別化強化。富士通のクロスインダストリー知見によるKDDI法人営業力の底上げ。エンタープライズ領域でのKDDI-富士通アライアンスの象徴案件化。
＜顧客価値＞ 法人顧客にとって「通信＋DX＋AI」のワンストップ提供が実現し、ベンダー統合による調達効率化とTime-to-Value短縮が期待できる。

■ ROI試算
＜初期投資＞ 約3億円（基盤構築・PoC・共同開発費用）
＜年間運用コスト＞ 約0.8億円（保守・運用・アップデート）
＜売上見込＞ 初年度: 8-12億円、2年目: 15-20億円、3年目: 25-30億円
＜コスト削減効果＞ 運用効率化による年間コスト削減: 1.5億円
＜想定ROI＞ 初年度150%、3年累計で400%超。BreakEven: 導入後8ヶ月。

■ Why Fujitsu
＜クロスインダストリー知見＞ Uvanceは7つの重点分野で業界横断のDX知見を蓄積。通信業界だけでなく製造・金融・公共など幅広い業界の課題解決実績が、KDDI法人顧客への提案力を飛躍的に高める。
＜Kozuchi AIの技術優位性＞ 富士通独自のAIプラットフォームKozuchiは、説明可能AI・因果発見など他社にない技術を保有。KDDIのAIサービスに組み込むことで明確な差別化を実現。
＜グローバルデリバリー体制＞ 国内最大級のSI人材リソースとグローバル13万人体制により、大規模案件の確実な遂行力を担保。NECやEricssonと比較し、End-to-End提案力で優位。
＜共創パートナーとしての信頼＞ KDDI既存取引関係による信頼基盤と、Uvance共創メソッドによる体系的な事業変革支援力が、単なるSIベンダーではなく戦略パートナーとしての価値を提供する。"""
    else:
        report_text = None
    try:
        if not mock_mode:
            kddi_text = "\n".join(f"- {t}" for t in kddi_news) if kddi_news else "（取得なし）"
            fujitsu_text = "\n".join(f"- {t}" for t in fujitsu_news) if fujitsu_news else "（取得なし）"
            kddi_press_text = "\n".join(f"- {t}" for t in kddi_press) if kddi_press else "（取得なし）"
            fujitsu_press_text = "\n".join(f"- {t}" for t in fujitsu_press) if fujitsu_press else "（取得なし）"
            print(f"[DEBUG-REPORT] Calling API for: {opportunity_title[:40]}...")
            report_text = chat_completion(
                messages=[{
                    "role": "user",
                    "content": f"""あなたは富士通のKDDI担当アカウントストラテジストです。**WAKONX（KDDIのDX事業ブランド）とKDDI BX（ビジネス変革部門）**でのビジネス創出がミッションです。

以下のオポチュニティについて、KDDIおよび富士通の公式プレスリリースの内容を踏まえた詳細戦略レポートを作成してください。

【オポチュニティ】
{opportunity_title}

【KDDI（WAKONX/BX重点）の最新動向】
{kddi_text}

【KDDIプレスリリース（公式発表）】
{kddi_press_text}

【富士通・Uvanceの最新動向】
{fujitsu_text}

【富士通プレスリリース（UVANCE含む）】
{fujitsu_press_text}

以下の6セクションで構成してください。**KDDIプレスリリースの内容を根拠とし、富士通プレスリリースのUVANCEソリューションを活用した具体的な提案**にしてください。

1. 想定仮説（KDDIプレスリリースから読み取れる課題・ニーズの仮説。公式発表の内容を引用・分析し、KDDIが抱える潜在課題と事業ニーズを構造化する）
2. 解決の方向性・コンセプト（UVANCE＋KDDI戦略の交差点。富士通UvanceのソリューションとKDDI/WAKONXの戦略が交わるポイントを明確化し、共創コンセプトを提示する）
3. 提案内容（具体的なソリューション提案。対象部門、展開シナリオ、想定案件規模を含む具体的な提案を記述する）
4. 期待される効果（定量・定性の効果。導入による定量的な効果（コスト削減額、売上増加見込み等）と定性的な効果（ブランド価値、競争力等）を明記する）
5. ROI試算（投資対効果。初期投資額、年間コスト、売上見込み、BreakEvenポイントを試算する）
6. Why Fujitsu（富士通だからこそのビジネス優位性。Uvanceのクロスインダストリー知見、Kozuchi AI、グローバルデリバリー体制、共創パートナーとしての信頼など、競合他社ではなく富士通を選ぶべき理由を明確に示す）

各セクションの見出しは「■ セクション名」形式で記述してください。
セクション内のサブ見出し・キーワード（KDDIの課題認識、潜在ニーズ、仮説、コンセプト、ソリューション構成、対象部門、定量効果、定性効果、初期投資、クロスインダストリー知見等）は必ず「＜サブ見出し＞」の形式（全角山括弧）で記述してください。マークダウン記法（#, **, * 等）は一切使わないでください。"""
                }],
                max_tokens=8000,
                model="claude-haiku-4-5-20251001",
            ).strip()

        # HTMLテンプレートに埋め込み
        print(f"[DEBUG-REPORT] report_text length={len(report_text) if report_text else 0}, first 200 chars: {(report_text or '')[:200]}")
        sections_html = ""
        current_section = ""
        current_lines = []
        section_icons = {
            "想定仮説": "&#9670;",
            "解決の方向性・コンセプト": "&#9733;",
            "提案内容": "&#9654;",
            "期待される効果": "&#9673;",
            "ROI試算": "&#9650;",
            "Why Fujitsu": "&#9632;",
        }
        # Why Fujitsuセクションは特別なCSSクラスを付与
        highlight_sections = {"Why Fujitsu"}

        for line in report_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            is_section = False
            line_upper = line.upper()
            for sec_name in section_icons:
                if sec_name.upper() in line_upper:
                    if current_section and current_lines:
                        icon = section_icons.get(current_section, "&#9670;")
                        content = "<br>".join(current_lines)
                        extra_cls = " section-uvance" if current_section in highlight_sections else ""
                        sections_html += f'<div class="report-section{extra_cls}"><div class="section-header">{icon} {current_section}</div><div class="section-body">{content}</div></div>'
                    current_section = sec_name
                    current_lines = []
                    rest = line
                    for prefix in [f"■ {sec_name}", f"■{sec_name}", sec_name]:
                        rest = re.sub(re.escape(prefix), "", rest, flags=re.IGNORECASE).strip()
                    if rest:
                        current_lines.append(rest)
                    is_section = True
                    break
            if not is_section:
                cleaned = line.lstrip("■・- ")
                # マークダウン記法を除去
                cleaned = re.sub(r'^#{1,6}\s*', '', cleaned)
                cleaned = cleaned.replace('**', '').replace('__', '')
                cleaned = re.sub(r'^[\-\*]{3,}$', '', cleaned)
                cleaned = re.sub(r'^\*\s+', '', cleaned)
                # ＜サブ見出し＞をスタイル付きspanに変換
                cleaned = re.sub(r'＜([^＞]+)＞', r'<span class="sub-heading">＜\1＞</span>', cleaned)
                cleaned = cleaned.strip()
                if not cleaned:
                    continue
                current_lines.append(cleaned)

        if current_section and current_lines:
            icon = section_icons.get(current_section, "&#9670;")
            content = "<br>".join(current_lines)
            extra_cls = " section-uvance" if current_section in highlight_sections else ""
            sections_html += f'<div class="report-section{extra_cls}"><div class="section-header">{icon} {current_section}</div><div class="section-body">{content}</div></div>'

        now = datetime.now()

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Strategic Report - {opportunity_title}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
    background: #000;
    color: #c8aaff;
    font-family: 'Share Tech Mono', monospace;
    min-height: 100vh;
}}
.report-container {{
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 30px;
    position: relative;
}}
.report-container::before {{
    content: "";
    position: fixed; inset: 0;
    background: radial-gradient(ellipse at center, rgba(30,10,60,0.3) 0%, rgba(0,0,0,0.95) 70%);
    z-index: -1;
}}
.report-header {{
    text-align: center;
    margin-bottom: 40px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(180,120,255,0.15);
}}
.report-label {{
    font-family: 'Orbitron', monospace;
    font-size: 0.55rem;
    letter-spacing: 6px;
    color: rgba(180,120,255,0.4);
    margin-bottom: 12px;
}}
.report-title {{
    font-family: 'Orbitron', monospace;
    font-size: 1.4rem;
    font-weight: 900;
    color: rgba(180,120,255,0.9);
    letter-spacing: 2px;
    text-shadow: 0 0 20px rgba(180,120,255,0.3);
    line-height: 1.6;
}}
.report-meta {{
    font-size: 0.6rem;
    color: rgba(180,120,255,0.3);
    margin-top: 10px;
    letter-spacing: 2px;
}}
.report-section {{
    margin-bottom: 28px;
    padding: 16px 20px;
    border: 1px solid rgba(180,120,255,0.08);
    border-radius: 6px;
    background: rgba(10,5,20,0.6);
    box-shadow: 0 0 15px rgba(180,120,255,0.02);
}}
.section-header {{
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: rgba(180,120,255,0.9);
    letter-spacing: 3px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(180,120,255,0.15);
    text-shadow: 0 0 8px rgba(180,120,255,0.3);
}}
.section-body {{
    font-size: 0.95rem;
    line-height: 2.2;
    color: rgba(220,200,255,0.85);
}}
/* Uvance highlight section */
.section-uvance {{
    border-color: rgba(0,180,255,0.2);
    background: rgba(0,20,40,0.6);
    box-shadow: 0 0 20px rgba(0,180,255,0.04);
}}
.section-uvance .section-header {{
    color: rgba(0,200,255,0.9);
    border-bottom-color: rgba(0,180,255,0.2);
    text-shadow: 0 0 10px rgba(0,180,255,0.4);
}}
.report-footer {{
    text-align: center;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(180,120,255,0.08);
    font-family: 'Orbitron', monospace;
    font-size: 0.4rem;
    color: rgba(180,120,255,0.2);
    letter-spacing: 4px;
}}
.scanlines {{
    position: fixed; inset: 0; z-index: 100;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
    pointer-events: none;
}}
</style>
</head>
<body>
<div class="scanlines"></div>
<div class="report-container">
    <div class="report-header">
        <div class="report-label">FUJITSU // STRATEGIC INTELLIGENCE REPORT</div>
        <div class="report-title">{opportunity_title}</div>
        <div class="report-meta">GENERATED: {now.strftime("%Y-%m-%d %H:%M:%S")} // CLASSIFICATION: CONFIDENTIAL</div>
    </div>
    {sections_html}
    <div class="report-footer">
        FUJITSU // ACCOUNT INTELLIGENCE DIVISION // KDDI SECTOR // END OF REPORT
    </div>
</div>
</body></html>"""

        # ファイル名はタイトルのハッシュで安定させる
        import hashlib
        name_hash = hashlib.md5(opportunity_title.encode()).hexdigest()[:8]
        filename = f"report_{name_hash}.html"
        filepath = os.path.join(STATIC_DIR, filename)
        with open(filepath, "w", encoding="utf-8-sig") as f:
            f.write(html)
        print(f"[DEBUG-REPORT] sections_html length={len(sections_html)}")
        return filename, sections_html, opportunity_title
    except Exception as e:
        print(f"[DEBUG-REPORT] EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return None, "", ""


