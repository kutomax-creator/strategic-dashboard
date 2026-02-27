# Strategic Dashboard Project

## 概要
SF映画風の戦略コックピット・ダッシュボード（Streamlit）
富士通アカウントセールスマネージャー向け KDDI動向監視ツール

## 起動方法
```
cd ~/Projects/StrategicDashboard
python3 -m streamlit run app_new.py
```
URL: http://localhost:8502

## プロジェクト構成
- `app_new.py` — メインエントリポイント（Streamlit render/ボタン処理）
- `dashboard_modules/` — モジュール群
  - `config.py` — 設定・APIキー・定数
  - `ai_client.py` — AI API抽象レイヤー（Anthropic / 富士通切替）
  - `components/` — UIコンポーネント
    - `news.py` — ニュース・プレスリリース取得
    - `stock.py` — 株価取得・SVGチャート
    - `weather.py` — 天気取得
    - `intelligence.py` — WAKONX/BX インテリジェンス
    - `images.py` — 画像ヘルパー
    - `chat.py` — Strategy Chat
    - `context.py` — Context Library（ファイル管理）
  - `analysis/` — 分析ロジック
    - `opportunities.py` — AI Strategic Opportunities生成
    - `insights.py` — Insight Matcher
    - `proposals.py` — 提案フレームワーク生成
  - `ui/`
    - `html_builder.py` — ダッシュボードHTML構築（最大のファイル）

## 注意事項
- 実行ファイルは必ず `app_new.py`（モジュール分割版）
- AI APIキーは `config.py` で管理
- プロジェクトルート: `~/Projects/StrategicDashboard/`
