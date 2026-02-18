# Strategic Dashboard - モジュール構造

## 概要
元の53,000トークン（3,932行）の巨大なapp.pyを、機能ごとに分割してモジュール化しました。

## ファイル構造

```
dashboard_modules/
├── config.py              (設定・APIキー)
├── components/            (UI コンポーネント)
│   ├── images.py         (画像処理: 約40行)
│   ├── stock.py          (株価・チャート: 約60行)
│   ├── news.py           (ニュース取得: 約25行)
│   ├── weather.py        (天気情報: 約55行)
│   ├── intelligence.py   (BU情報: 約65行)
│   ├── context.py        (ファイル管理: 約117行)
│   └── chat.py           (AIチャット: 約69行)
├── analysis/              (分析機能)
│   ├── insights.py       (AI分析: 約269行)
│   ├── opportunities.py  (機会発見: 約360行)
│   └── proposals.py      (提案書生成: 約94行)
├── ui/                    (UI生成)
│   └── html_builder.py   (HTMLビルダー: 約2,450行)
└── app_new.py            (メイン: 337行)
```

## 元との比較

| 項目 | 元のapp.py | 分割後 |
|------|-----------|--------|
| メインファイル | 3,932行 | 337行 |
| トークン消費 | ~53,000 | ~500 (メインのみ読む場合) |
| 変更コスト | 非常に高い | 低い |

## 使用方法

```bash
# 新しいモジュール化版を使用
cd /Users/takaakikutose
streamlit run app_new.py

# 元のバックアップ
# app.py.backup
```

## 今後の変更例

### 株価表示を変更したい場合
```bash
# 元: app.py全体（53,000トークン）を読む必要
# 新: components/stock.py（約60行、~1,000トークン）だけ読めばOK
```

### チャット機能を変更したい場合
```bash
# 元: app.py全体（53,000トークン）を読む必要
# 新: components/chat.py（約69行、~1,200トークン）だけ読めばOK
```

## トークン節約効果

1回の変更で約50倍のトークン節約が可能になりました！
