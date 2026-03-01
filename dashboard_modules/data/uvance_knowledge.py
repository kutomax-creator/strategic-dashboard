"""
UVANCE Knowledge Base - Structured product/solution data for hypothesis proposals
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UvanceSolution:
    name: str
    vertical: str
    description: str
    key_features: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    differentiators: list[str] = field(default_factory=list)
    reference_cases: list[str] = field(default_factory=list)
    kddi_relevance: str = ""
    typical_roi: str = ""
    # 新規フィールド
    detailed_scenarios: list[str] = field(default_factory=list)
    implementation_approach: str = ""
    competitive_advantage: str = ""
    success_metrics: list[str] = field(default_factory=list)
    synergy_solutions: list[str] = field(default_factory=list)


# ─── UVANCE Solutions Catalog ─────────────────────────────────────────
UVANCE_SOLUTIONS: list[UvanceSolution] = [
    UvanceSolution(
        name="Uvance Digital Shifts",
        vertical="Digital Shifts",
        description="企業のDX推進を加速するエンドツーエンドソリューション。業務プロセス変革からデータ活用基盤構築まで。",
        key_features=[
            "業務プロセスDX（BPR + デジタル化）",
            "Kozuchi AI Platform連携（生成AI・ML基盤）",
            "Data e-TRUST（データガバナンス・プライバシー保護）",
            "アジャイル共創プログラム",
        ],
        use_cases=[
            "WAKONX連携によるDXプラットフォーム構築",
            "カスタマーエクスペリエンス高度化",
            "データドリブン経営意思決定基盤",
            "生成AIを活用した業務自動化",
        ],
        differentiators=[
            "Kozuchi AI Platformによるマルチモーダル生成AI基盤",
            "Data e-TRUSTの信頼性あるデータ流通",
            "Palantir連携によるデータ分析高度化",
        ],
        reference_cases=[
            "通信事業者向けネットワーク最適化AI",
            "金融機関DX基盤構築プロジェクト",
        ],
        kddi_relevance="WAKONX/BXのDX推進基盤として最も親和性が高い。KDDIの法人事業DX支援サービスとのシナジー。",
        typical_roi="業務効率30-40%改善、データ活用による売上5-10%向上（12-18ヶ月で投資回収）",
        detailed_scenarios=[
            "WAKONX法人DXメニューの共同開発 — Kozuchi AIをWAKONXプラットフォームに統合し、業種別AIテンプレートを提供。法人営業の提案力を強化",
            "KDDI社内業務プロセス変革 — 契約管理・顧客対応・ネットワーク運用の3領域で業務DXを推進、年間工数20万時間削減",
            "au PAY×パーソナライズマーケティング — 3,000万顧客の行動データ×生成AIで個別最適クーポン配信、利用率2.5倍",
            "法人顧客向けデータ活用支援サービス — KDDIが保有する業種横断データを富士通Data e-TRUSTで安全に流通、新規データビジネス創出",
            "KDDI BX部門の事業アイデア評価AI — 新規事業候補の市場性・実現性をAIスコアリング、意思決定速度3倍",
        ],
        implementation_approach="3ヶ月MVP→6ヶ月本番展開→12ヶ月全社拡大",
        competitive_advantage="NEC iExperienceは汎用的だがKDDI通信データとの統合が弱い。NTTデータはSI中心で共創型が苦手。富士通はKozuchi＋Data e-TRUSTの組合せでデータ活用→AI実装を一気通貫で提供可能。",
        success_metrics=[
            "業務プロセス効率化率: 現状→目標40%改善（12ヶ月）",
            "データ活用起点の新規売上: 年間5-10億円（18ヶ月）",
            "法人DXサービスメニュー数: 現状→目標3倍（12ヶ月）",
        ],
        synergy_solutions=["Kozuchi AI Platform", "Data e-TRUST", "Zero Trust Security"],
    ),
    UvanceSolution(
        name="Uvance Hybrid IT",
        vertical="Hybrid IT",
        description="マルチクラウド・オンプレミスのハイブリッドIT基盤を最適化。運用自動化とセキュリティを統合。",
        key_features=[
            "マルチクラウド統合管理",
            "ゼロトラストセキュリティアーキテクチャ",
            "AIOps（AI運用自動化）",
            "クラウドネイティブ移行支援",
        ],
        use_cases=[
            "KDDIデータセンター×クラウドハイブリッド最適化",
            "5Gエッジコンピューティング基盤",
            "通信インフラのクラウドネイティブ化",
        ],
        differentiators=[
            "富士通グローバルDC網との連携",
            "ゼロトラスト＋SASEの統合アプローチ",
            "AIOpsによるIT運用コスト60%削減実績",
        ],
        reference_cases=[
            "大手通信事業者のクラウド移行プロジェクト",
            "グローバルIT基盤統合案件",
        ],
        kddi_relevance="KDDIのデータセンター事業・クラウドサービスとの直接連携。5Gエッジとの統合提案。",
        typical_roi="IT運用コスト30-50%削減、インフラ障害50%減少（投資回収期間9-15ヶ月）",
        detailed_scenarios=[
            "KDDIマルチクラウド統合管理 — AWS/Azure/GCPの混在環境を富士通Hybrid ITで一元管理、運用工数60%削減",
            "5Gエッジコンピューティング基盤 — KDDI 5Gインフラ×富士通エッジサーバで超低遅延AIサービス基盤を構築",
            "KDDI法人向けマネージドクラウドサービス — Hybrid IT基盤をWAKONXメニューとして提供、月額課金モデル",
            "通信インフラのクラウドネイティブ化 — コアネットワーク機能のコンテナ化・マイクロサービス化で運用柔軟性向上",
            "AIOps統合運用基盤 — AI予兆検知でネットワーク障害を事前防止、SLA違反を80%削減",
        ],
        implementation_approach="3ヶ月設計・PoC→6ヶ月段階移行→12ヶ月全面切替",
        competitive_advantage="AWS/Azureは自社クラウドへの囲い込みが前提。富士通はマルチクラウド中立の立場でKDDIの最適アーキテクチャを設計できる。",
        success_metrics=[
            "IT運用コスト削減率: 目標40%（12ヶ月）",
            "インフラ障害件数: 目標60%削減（12ヶ月）",
            "クラウド移行率: 現状30%→目標70%（18ヶ月）",
        ],
        synergy_solutions=["Zero Trust Security", "Private 5G Solution"],
    ),
    UvanceSolution(
        name="Kozuchi AI Platform",
        vertical="Digital Shifts",
        description="富士通の生成AI・機械学習統合プラットフォーム。エンタープライズ向けセキュアなAI基盤。",
        key_features=[
            "マルチモーダル生成AI（テキスト・画像・コード）",
            "企業専用LLMファインチューニング",
            "RAG（検索拡張生成）基盤",
            "AI倫理・ガバナンスフレームワーク",
        ],
        use_cases=[
            "コールセンターAI自動応答",
            "社内ナレッジ検索の高度化",
            "契約書・技術文書の自動生成・分析",
            "コード生成・レビュー自動化",
        ],
        differentiators=[
            "日本語特化の高精度LLM",
            "エンタープライズセキュリティ標準準拠",
            "Fujitsu Research発の独自AI技術",
        ],
        reference_cases=[
            "大手金融機関向け生成AI基盤構築",
            "製造業向けAI品質検査システム",
        ],
        kddi_relevance="KDDIの法人AI活用サービス、AIコールセンター、WAKONX AI機能との統合。",
        typical_roi="業務自動化により人件費20-35%削減、サービス応答速度60%向上",
        detailed_scenarios=[
            "KDDIコールセンター3万席のAI自動応答化 — Kozuchi LLMで一次対応自動化率70%、年間コスト△15億円",
            "WAKONX法人顧客向けAIアシスタント — 営業支援・提案書自動生成で商談リードタイム50%短縮",
            "KDDI社内ナレッジ基盤 — 10万件の技術文書をRAG化、エンジニア問合せ対応時間80%削減",
            "法人向け業種別AIテンプレート — 製造・金融・流通の業種別AIモデルをWAKONXメニューで提供",
            "AIコード生成・レビュー基盤 — KDDI社内開発者2,000人の生産性を40%向上",
            "契約書・技術文書の自動分析 — 年間50万件の契約書レビューをAI化、法務工数70%削減",
        ],
        implementation_approach="3ヶ月AI基盤構築→6ヶ月ユースケース展開→12ヶ月全社導入",
        competitive_advantage="NEC iExperienceは汎用AIが中心。富士通Kozuchiは日本語特化LLM＋RAG＋AI倫理ガバナンスをセットで提供、エンタープライズ要件を満たす。",
        success_metrics=[
            "AI自動応答率: 現状5%→目標70%（12ヶ月）",
            "営業提案書作成時間: 現状8時間→目標1時間（6ヶ月）",
            "社内ナレッジ検索精度: 目標90%以上（6ヶ月）",
        ],
        synergy_solutions=["Data e-TRUST", "Uvance Digital Shifts"],
    ),
    UvanceSolution(
        name="Data e-TRUST",
        vertical="Digital Shifts",
        description="安全・信頼性の高いデータ流通基盤。パーソナルデータの適正管理からビジネスデータ活用まで。",
        key_features=[
            "データガバナンスフレームワーク",
            "プライバシー保護技術（差分プライバシー等）",
            "データカタログ・メタデータ管理",
            "Palantir Foundry連携",
        ],
        use_cases=[
            "顧客データ統合・360度ビュー構築",
            "データマネタイゼーション基盤",
            "規制対応（個人情報保護法等）データ管理",
        ],
        differentiators=[
            "Palantirとの戦略的パートナーシップ",
            "日本の法規制に完全準拠した設計",
            "リアルタイムデータパイプライン",
        ],
        reference_cases=[
            "ヘルスケアデータ流通プラットフォーム",
            "スマートシティデータ統合基盤",
        ],
        kddi_relevance="KDDIの保有する大規模顧客データの安全な活用。位置情報・通信データのデータビジネス推進。",
        typical_roi="データ活用による新規収益5-15%創出、規制対応コスト40%削減",
        detailed_scenarios=[
            "KDDI 3,000万顧客データの安全な活用基盤 — プライバシー保護×データ分析で顧客インサイト自動生成",
            "位置情報データビジネス — 匿名化された人流データを自治体・商業施設に提供、新規データ収益年間10億円",
            "Palantir Foundry連携 — KDDIの通信データ×業界データを統合分析、法人顧客向けデータサービス開発",
            "個人情報保護法対応データガバナンス — KDDI全社のデータ管理を一元化、規制対応コスト40%削減",
            "データマーケットプレイス構築 — 企業間の安全なデータ流通基盤を構築、KDDIをデータハブに",
        ],
        implementation_approach="3ヶ月データカタログ整備→6ヶ月ガバナンス基盤→12ヶ月データ流通開始",
        competitive_advantage="Palantirとの戦略提携が最大の差別化。NTTデータはSI型でプラットフォーム提供力が弱い。",
        success_metrics=[
            "顧客データ活用率: 現状15%→目標60%（18ヶ月）",
            "データ起点の新規収益: 年間10-20億円（24ヶ月）",
            "規制対応コスト: 目標40%削減（12ヶ月）",
        ],
        synergy_solutions=["Kozuchi AI Platform", "Uvance Digital Shifts"],
    ),
    UvanceSolution(
        name="Private 5G Solution",
        vertical="Digital Shifts",
        description="企業・自治体向けプライベート5Gネットワーク構築。超低遅延・大容量通信でDXを実現。",
        key_features=[
            "ローカル5G基地局設計・構築",
            "ネットワークスライシング",
            "エッジコンピューティング連携",
            "AI×5Gリアルタイム分析",
        ],
        use_cases=[
            "スマートファクトリー（製造現場DX）",
            "建設現場遠隔監視",
            "スタジアム・商業施設の高密度通信",
        ],
        differentiators=[
            "富士通のネットワーク技術蓄積（O-RAN推進）",
            "5G＋AI＋エッジの統合ソリューション",
        ],
        reference_cases=[
            "製造業向けローカル5G工場",
            "スマートスタジアム実証",
        ],
        kddi_relevance="KDDIの5G事業との補完関係。KDDI法人向けプライベート5Gサービスとの協業機会。",
        typical_roi="製造ライン稼働率15-25%向上、リモート監視によるコスト20%削減",
        detailed_scenarios=[
            "KDDI法人向けプライベート5G統合サービス — 富士通のローカル5G技術×KDDIの5Gライセンスで法人向けワンストップ提供",
            "スマートファクトリーパッケージ — 5G×AI画像検査×デジタルツインで製造業DXを加速、歩留まり率5%改善",
            "建設現場遠隔監視ソリューション — 5G低遅延通信で重機遠隔操作・安全監視を実現、事故リスク50%削減",
            "スタジアム・イベント会場5G — 高密度通信×AR演出で次世代エンタメ体験、KDDI 5G契約増に貢献",
            "遠隔医療5G基盤 — 5G低遅延で手術支援映像伝送、地方医療格差の解消",
        ],
        implementation_approach="3ヶ月設計・調達→6ヶ月構築・テスト→12ヶ月本番運用・横展開",
        competitive_advantage="富士通のO-RAN推進・ネットワーク技術蓄積は国内トップクラス。NECも5G技術を持つが、AI・エッジとの統合力で富士通が優位。",
        success_metrics=[
            "ローカル5G導入案件数: 目標年間20件（12ヶ月）",
            "製造ライン稼働率: 目標15-25%向上（12ヶ月）",
            "5G×AI活用ユースケース数: 目標10件（18ヶ月）",
        ],
        synergy_solutions=["Uvance Hybrid IT", "Uvance Trusted Society", "Kozuchi AI Platform"],
    ),
    UvanceSolution(
        name="Uvance Healthy Living",
        vertical="Healthy Living",
        description="ヘルスケア・ライフサイエンス向けDXソリューション。医療データ活用から健康経営支援まで。",
        key_features=[
            "医療データ統合プラットフォーム",
            "AI診断支援",
            "リモートヘルスモニタリング",
            "健康経営支援ダッシュボード",
        ],
        use_cases=[
            "遠隔医療基盤構築",
            "従業員健康管理DX",
            "創薬データ分析",
        ],
        differentiators=[
            "医療機関との豊富な実績",
            "PMDA対応のバリデーション体制",
        ],
        reference_cases=[
            "大学病院AI診断支援システム",
            "製薬会社データプラットフォーム",
        ],
        kddi_relevance="KDDIのヘルスケア事業（au WALLET等の健康サービス）との連携。通信×ヘルスケアの新市場。",
        typical_roi="医療コスト15-20%削減、従業員健康リスク30%低減",
        detailed_scenarios=[
            "KDDI通信網×遠隔医療プラットフォーム — 5G低遅延通信で地方病院へのリモート診療支援、医師不足地域カバー率2倍",
            "au健康管理アプリ連携 — ウェアラブルデバイスデータ×AIで健康リスク予測、保険事業との連動",
            "法人向け健康経営DXサービス — 従業員の健康データ可視化×AI予防提案で健康経営優良法人認定支援",
            "製薬会社向けリアルワールドデータ基盤 — KDDIの同意取得基盤×富士通データ分析で創薬データビジネス",
            "介護施設IoTモニタリング — センサー×5G×AIで入居者見守りの自動化、介護人材不足への対応",
        ],
        implementation_approach="3ヶ月基盤設計→6ヶ月パイロット導入→12ヶ月本格展開",
        competitive_advantage="富士通は医療機関との豊富な導入実績（電子カルテ国内シェアトップクラス）。NTTデータは金融中心でヘルスケア弱い。",
        success_metrics=[
            "遠隔診療対応医療機関数: 目標100施設（18ヶ月）",
            "健康経営サービス導入企業数: 目標500社（12ヶ月）",
            "ヘルスケア事業売上: 目標年間20億円（24ヶ月）",
        ],
        synergy_solutions=["Private 5G Solution", "Data e-TRUST", "Kozuchi AI Platform"],
    ),
    UvanceSolution(
        name="Uvance Trusted Society",
        vertical="Trusted Society",
        description="安全・安心な社会基盤をデジタルで実現。スマートシティ・防災・行政DXソリューション。",
        key_features=[
            "スマートシティプラットフォーム",
            "デジタルツイン都市モデル",
            "防災・減災情報基盤",
            "行政DX・マイナンバー連携",
        ],
        use_cases=[
            "自治体DX基盤構築",
            "交通最適化・MaaS",
            "災害対応リアルタイムシステム",
        ],
        differentiators=[
            "日本全国の自治体導入実績",
            "デジタルツイン技術の先進性",
        ],
        reference_cases=[
            "政令指定都市スマートシティ基盤",
            "広域防災情報システム",
        ],
        kddi_relevance="KDDIの自治体向け通信インフラ・IoTサービスとの統合。スマートシティ共同推進。",
        typical_roi="行政コスト20-30%削減、市民サービス満足度25%向上",
        detailed_scenarios=[
            "KDDI 5G×デジタルツイン都市基盤 — 都市のリアルタイムデータを3Dモデルで統合管理、交通・防災・エネルギー最適化",
            "自治体DX共同提案 — KDDI通信インフラ×富士通行政DXで自治体向けワンストップDXサービス提供",
            "防災情報リアルタイム基盤 — 5G×IoTセンサーで災害予兆検知、避難誘導の自動化",
            "MaaS交通最適化 — KDDIの位置情報×デジタルツインで公共交通のリアルタイム最適化、利用者満足度30%向上",
            "スマートビルディング統合管理 — オフィスビル・商業施設のエネルギー・セキュリティ・設備を統合管理",
        ],
        implementation_approach="3ヶ月構想・設計→6ヶ月パイロット都市→12ヶ月複数都市展開",
        competitive_advantage="富士通は全国自治体への導入実績が国内最大規模。NECも公共強いが、デジタルツイン技術の先進性で富士通が優位。",
        success_metrics=[
            "スマートシティ案件受注数: 目標年間10件（12ヶ月）",
            "行政DXサービス利用自治体数: 目標50自治体（18ヶ月）",
            "市民サービスデジタル化率: 目標80%（24ヶ月）",
        ],
        synergy_solutions=["Private 5G Solution", "Data e-TRUST", "Sustainability Transformation"],
    ),
    UvanceSolution(
        name="Zero Trust Security",
        vertical="Hybrid IT",
        description="ゼロトラストアーキテクチャに基づく統合セキュリティソリューション。SASE・XDR・IAM統合。",
        key_features=[
            "SASE（Secure Access Service Edge）",
            "XDR（Extended Detection and Response）",
            "IAM（Identity Access Management）",
            "セキュリティ運用自動化（SOAR）",
        ],
        use_cases=[
            "リモートワーク環境のセキュリティ強化",
            "サプライチェーンセキュリティ",
            "OTセキュリティ（制御系ネットワーク保護）",
        ],
        differentiators=[
            "SOC/CSIRT運用の豊富な実績",
            "国内最大級のセキュリティ監視基盤",
        ],
        reference_cases=[
            "大手通信事業者SOC構築",
            "製造業OTセキュリティ導入",
        ],
        kddi_relevance="KDDIの法人セキュリティサービスとの協業。通信事業者としてのセキュリティ強化ニーズに対応。",
        typical_roi="セキュリティインシデント70%削減、対応時間80%短縮",
        detailed_scenarios=[
            "KDDI法人向けマネージドセキュリティサービス — SASE×ゼロトラストの統合セキュリティをWAKONXメニューで提供",
            "KDDIグループ全体のゼロトラスト移行 — 5万人の従業員・パートナーを対象にゼロトラストアーキテクチャを段階導入",
            "OTセキュリティ統合 — KDDI法人顧客の工場・インフラのOTネットワーク保護、制御系サイバー攻撃を防御",
            "SOC共同運用サービス — 富士通SOC×KDDIネットワーク監視を統合、24/365のサイバーセキュリティ監視体制",
            "サプライチェーンセキュリティ — KDDIパートナー企業のセキュリティレベルを可視化・底上げ",
        ],
        implementation_approach="3ヶ月設計・アセスメント→6ヶ月段階導入→12ヶ月全面展開",
        competitive_advantage="富士通は国内最大級のSOC運用実績を持つ。アクセンチュアはコンサル中心で運用まで一貫対応できない。",
        success_metrics=[
            "セキュリティインシデント削減率: 目標70%（12ヶ月）",
            "インシデント対応時間: 目標80%短縮（12ヶ月）",
            "ゼロトラスト適用範囲: 目標全従業員100%（18ヶ月）",
        ],
        synergy_solutions=["Uvance Hybrid IT", "Data e-TRUST"],
    ),
    UvanceSolution(
        name="Uvance Business Applications",
        vertical="Digital Shifts",
        description="ERPモダナイゼーション・業務アプリケーション刷新。SAP S/4HANA移行を含む。",
        key_features=[
            "SAP S/4HANA移行・最適化",
            "ローコード/ノーコード業務アプリ開発",
            "業務プロセスマイニング",
            "RPA統合自動化",
        ],
        use_cases=[
            "基幹システム刷新（2027年問題対応）",
            "業務プロセス可視化・最適化",
            "部門横断データ統合",
        ],
        differentiators=[
            "SAP認定パートナーとしての豊富な導入実績",
            "業務コンサルからシステム構築まで一貫支援",
        ],
        reference_cases=[
            "大手通信会社ERP刷新プロジェクト",
            "グローバルSAP統合案件",
        ],
        kddi_relevance="KDDIの基幹システム刷新ニーズ。2027年問題への対応支援。",
        typical_roi="業務処理速度40%向上、年間運用コスト25-35%削減（投資回収18-24ヶ月）",
        detailed_scenarios=[
            "KDDI基幹システムSAP S/4HANA移行 — 2027年問題対応と同時にAI業務自動化を実装、基幹業務コスト30%削減",
            "法人顧客向けERP移行支援サービス — KDDIのSI部門と連携しERP移行をパッケージ化、WAKONX法人メニューに追加",
            "業務プロセスマイニング — KDDI社内の業務プロセスを可視化・分析し、RPA×AI自動化の対象領域を特定",
            "ローコード業務アプリ開発基盤 — 現場部門が自らアプリ開発できる基盤を提供、IT部門負荷を50%削減",
            "経理・人事・調達の統合DX — 基幹3部門の業務をSAP S/4HANA上で統合、部門横断データ活用を実現",
        ],
        implementation_approach="6ヶ月アセスメント・設計→12ヶ月移行・構築→24ヶ月全面稼働",
        competitive_advantage="富士通はSAP認定パートナーとして国内最大規模の移行実績。アクセンチュアもSAP強いが、コスト面で富士通が有利。",
        success_metrics=[
            "SAP S/4HANA移行完了率: 目標100%（24ヶ月）",
            "業務処理速度: 目標40%向上（12ヶ月）",
            "基幹システム運用コスト: 目標30%削減（24ヶ月）",
        ],
        synergy_solutions=["Kozuchi AI Platform", "Uvance Digital Shifts"],
    ),
    UvanceSolution(
        name="Sustainability Transformation",
        vertical="Digital Shifts",
        description="サステナビリティ経営をデジタルで推進。CO2排出量可視化からグリーンDXまで。",
        key_features=[
            "CO2排出量可視化・管理プラットフォーム",
            "サプライチェーンESGスコアリング",
            "グリーンIT最適化",
            "サステナビリティレポート自動生成",
        ],
        use_cases=[
            "Scope1/2/3排出量管理",
            "サプライチェーンの脱炭素化支援",
            "TCFDレポート作成支援",
        ],
        differentiators=[
            "富士通自身のカーボンニュートラル実績",
            "グローバルサプライチェーンでの実装経験",
        ],
        reference_cases=[
            "大手製造業CO2管理基盤",
            "サプライチェーンESG評価システム",
        ],
        kddi_relevance="KDDIのカーボンニュートラル宣言・ESG戦略との連携。通信インフラのグリーン化支援。",
        typical_roi="CO2排出量20-30%削減、ESGスコア向上による企業価値増加",
        detailed_scenarios=[
            "KDDIのScope1/2/3排出量リアルタイム可視化 — 通信インフラ・オフィス・サプライチェーン全体のCO2排出を一元管理",
            "auでんき×グリーンエネルギー最適化 — AI予測でエネルギー調達を最適化、再エネ比率向上",
            "KDDI法人向けESGデータ基盤サービス — サプライチェーン全体のESGスコアリングをSaaS提供",
            "通信基地局グリーン化 — 基地局電力消費のAI最適化×再エネ活用で運用コスト15%削減＋CO2削減",
            "TCFDレポート自動生成 — 投資家向けサステナビリティ開示情報を自動収集・レポート化",
        ],
        implementation_approach="3ヶ月現状分析・可視化→6ヶ月削減施策実装→12ヶ月TCFD開示対応",
        competitive_advantage="富士通自身がカーボンニュートラルで先行（2030年目標）。実践知に基づく提案はコンサルファームにない強み。",
        success_metrics=[
            "CO2排出量削減率: 目標20-30%（24ヶ月）",
            "ESGスコア: 目標業界上位10%（18ヶ月）",
            "グリーンIT電力削減: 目標15%（12ヶ月）",
        ],
        synergy_solutions=["Data e-TRUST", "Uvance Trusted Society"],
    ),
]


# ─── Cross-Solution Synergy Map ──────────────────────────────────
CROSS_SOLUTION_SYNERGIES: list[dict] = [
    {
        "name": "AI×データ信頼基盤",
        "solutions": ["Kozuchi AI Platform", "Data e-TRUST"],
        "scenario": "KDDIの3,000万顧客データを安全に活用し、AIで顧客インサイトを自動生成。プライバシー保護とAI活用を両立。",
        "kddi_value": "データビジネス新規収益＋顧客LTV向上",
    },
    {
        "name": "5G×スマートシティ",
        "solutions": ["Private 5G Solution", "Uvance Trusted Society"],
        "scenario": "KDDIの5Gインフラ×富士通デジタルツインで都市のリアルタイム最適化。交通・防災・エネルギーを統合管理。",
        "kddi_value": "自治体DX案件の大型受注＋5G利用拡大",
    },
    {
        "name": "ヘルスケア×通信",
        "solutions": ["Uvance Healthy Living", "Private 5G Solution"],
        "scenario": "KDDI通信網×富士通医療AI基盤で遠隔医療プラットフォーム構築。5G低遅延で手術支援も。",
        "kddi_value": "ヘルスケア事業拡大＋社会課題解決ブランディング",
    },
    {
        "name": "GX×ESG経営",
        "solutions": ["Sustainability Transformation", "Data e-TRUST"],
        "scenario": "KDDIのScope1/2/3排出量をリアルタイム可視化。サプライチェーン全体のESGスコアリングでTCFD対応。",
        "kddi_value": "ESG評価向上→資本コスト低減＋規制先行対応",
    },
    {
        "name": "セキュリティ×ハイブリッドIT",
        "solutions": ["Zero Trust Security", "Uvance Hybrid IT"],
        "scenario": "KDDIのマルチクラウド環境をゼロトラストで統合保護。SASE＋AIOpsで運用自動化。",
        "kddi_value": "法人セキュリティサービスの高付加価値化",
    },
    {
        "name": "ERP刷新×AI",
        "solutions": ["Uvance Business Applications", "Kozuchi AI Platform"],
        "scenario": "KDDI基幹システムのSAP S/4HANA移行と同時にAI業務自動化を実装。2027年問題対応＋DX一括推進。",
        "kddi_value": "基幹業務コスト30%削減＋業務品質向上",
    },
]


# ─── POC Fatigue Context ──────────────────────────────────────────────
POC_FATIGUE_CONTEXT = {
    "executive_quote": "松田社長の「PoC疲れ」「PoC死」言及 — 実証実験が本番展開に繋がらない課題を経営レベルで認識",
    "industry_background": "日本企業のDXプロジェクトの約70%がPoC段階で停滞（経産省DXレポート）",
    "fujitsu_answer": [
        "本番直結型設計: PoCから本番環境への移行を前提としたアーキテクチャ",
        "3ヶ月MVP: 最初の3ヶ月で最小限の本番稼働可能プロダクトを構築",
        "初期段階ROI試算: PoC開始前にビジネスケースを明確化",
        "段階的スケール: Small Start → Quick Win → Full Scale の3ステップ",
        "共創型開発: 顧客と富士通が共同でプロダクトオーナーを務める体制",
        "KPIドリブン: PoC段階から本番と同じKPIで評価",
    ],
    "approach_principles": [
        "PoC ≠ 実験 → PoC = 本番Phase1",
        "成果物はプロトタイプではなくMVP（Minimum Viable Product）",
        "投資判断に必要な定量データを3ヶ月で取得",
        "技術検証と同時にビジネスバリデーションを実施",
    ],
}


# ─── Helper Functions ─────────────────────────────────────────────────
def get_uvance_context_for_proposal(
    opportunity_title: str,
    preferred_vertical: str = "",
) -> str:
    """AIプロンプト用にUVANCEナレッジをテキスト化

    Parameters
    ----------
    opportunity_title : str
        オポチュニティタイトル
    preferred_vertical : str
        優先バーティカル（指定時はそのバーティカルのソリューションを優先）
    """
    title_lower = opportunity_title.lower()
    relevant = []
    for sol in UVANCE_SOLUTIONS:
        score = 0
        keywords = sol.name.lower().split() + sol.vertical.lower().split()
        keywords += [kw.lower() for kw in sol.key_features[:3]]
        for kw in keywords:
            if kw in title_lower:
                score += 1
        # KDDI関連性が言及されていれば加点
        if any(w in title_lower for w in ["kddi", "通信", "5g", "dx", "ai", "データ", "セキュリティ", "クラウド"]):
            score += 1
        # 優先バーティカル指定時は大幅加点
        if preferred_vertical and sol.vertical == preferred_vertical:
            score += 5
        if score > 0:
            relevant.append((score, sol))

    # スコア順ソート、最低3件は含める
    relevant.sort(key=lambda x: x[0], reverse=True)
    if not relevant:
        relevant = [(1, sol) for sol in UVANCE_SOLUTIONS[:5]]
    selected = [sol for _, sol in relevant[:5]]

    lines = ["# 富士通Uvance ソリューション情報\n"]
    for sol in selected:
        lines.append(f"## {sol.name} ({sol.vertical})")
        lines.append(f"概要: {sol.description}")
        lines.append(f"主要機能: {', '.join(sol.key_features)}")
        lines.append(f"ユースケース: {', '.join(sol.use_cases[:3])}")
        lines.append(f"差別化要素: {', '.join(sol.differentiators)}")
        if sol.reference_cases:
            lines.append(f"参考事例: {', '.join(sol.reference_cases)}")
        lines.append(f"KDDI関連性: {sol.kddi_relevance}")
        lines.append(f"典型的ROI: {sol.typical_roi}")
        # 新規フィールド出力
        if sol.detailed_scenarios:
            lines.append(f"KDDI具体適用シナリオ:")
            for scenario in sol.detailed_scenarios[:3]:
                lines.append(f"  - {scenario}")
        if sol.competitive_advantage:
            lines.append(f"競合優位性: {sol.competitive_advantage}")
        if sol.success_metrics:
            lines.append(f"成功KPI: {', '.join(sol.success_metrics[:2])}")
        if sol.synergy_solutions:
            lines.append(f"シナジーソリューション: {', '.join(sol.synergy_solutions)}")
        lines.append("")

    # クロスソリューションシナジー情報を追加
    synergy_lines = _get_relevant_synergies(selected)
    if synergy_lines:
        lines.append("# クロスソリューションシナジー\n")
        lines.extend(synergy_lines)

    return "\n".join(lines)


def _get_relevant_synergies(selected_solutions: list[UvanceSolution]) -> list[str]:
    """選定ソリューションに関連するシナジー情報を返す"""
    selected_names = {sol.name for sol in selected_solutions}
    lines = []
    for synergy in CROSS_SOLUTION_SYNERGIES:
        if any(s in selected_names for s in synergy["solutions"]):
            lines.append(f"## {synergy['name']}")
            lines.append(f"組合せ: {' × '.join(synergy['solutions'])}")
            lines.append(f"シナリオ: {synergy['scenario']}")
            lines.append(f"KDDI価値: {synergy['kddi_value']}")
            lines.append("")
    return lines


def get_poc_fatigue_context() -> str:
    """POC疲れ対策コンテキストをテキスト化"""
    ctx = POC_FATIGUE_CONTEXT
    lines = [
        "# PoC疲れ対策アプローチ\n",
        f"## 背景",
        f"- {ctx['executive_quote']}",
        f"- {ctx['industry_background']}\n",
        "## 富士通の回答:",
    ]
    for answer in ctx["fujitsu_answer"]:
        lines.append(f"- {answer}")
    lines.append("\n## アプローチ原則:")
    for principle in ctx["approach_principles"]:
        lines.append(f"- {principle}")
    return "\n".join(lines)


def get_all_verticals() -> list[str]:
    """全バーティカル名を返す"""
    return sorted(set(sol.vertical for sol in UVANCE_SOLUTIONS))


def find_solutions_by_vertical(vertical: str) -> list[UvanceSolution]:
    """バーティカル名でソリューションをフィルタ"""
    return [sol for sol in UVANCE_SOLUTIONS if sol.vertical == vertical]
