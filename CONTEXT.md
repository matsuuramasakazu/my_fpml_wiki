# Domain Context: FpML 5.12 Confirmation View Knowledge Base & Wiki

## 1. Domain & Scope

本リポジトリは、**FpML (Financial Products Markup Language) Version 5.12 Confirmation View** を対象とした、店頭（OTC）デリバティブ取引のデータモデル、メッセージング、業務プロセス、およびフロントオフィス・アーキテクチャに関する自律的ナレッジベース（Karpathy LLM Wiki パターン）です。

- **対象プロダクト**: 
  - 金利デリバティブ (IRD: Interest Rate Swap, XCCY Swap, FRA, Cap/Floor, Swaption)
  - 為替デリバティブ (FX: Spot, Forward, FX Option, NDF, Accruals, Targets)
  - 株式デリバティブ (EQD: Equity Option, Forward, Equity Swap, Variance Swap)
  - クレジットデリバティブ (CD: Single Name CDS, Basket CDS, Credit Event Notice)
  - コモディティ (COM) / インフレ (INF) / レポ・ローン (Repo, Loan)
- **対象ビュー**: **Confirmation View** (約定確認・コンファーメーション、約定後業務プロセス、ライフサイクルイベント、CCP清算等に特化したビュー)
- **市場コンテキスト**: 東京 OTC デリバティブ市場（日本の大手行・信託・証券・外銀東京支店）におけるフロントオフィス・クオンツ・決済・システム実務。

---

## 2. Repository Architecture (Three-Layer Model)

```text
my_fpml_wiki/
├── CONTEXT.md                    ← 本ドメイン定義（エージェントが最初に見る基盤）
├── fpml_xsd_catalog.md           ← 全 XSD スキーマの対応カタログ
├── confirmation/                 ← 【Layer 1: Raw Sources】(XSD スキーマ、XML サンプル - イミュータブル)
│   ├── fpml-*.xsd                ← 各プロダクト・共通・メッセージスキーマ
│   ├── products/                 ← プロダクト別 XML サンプル
│   └── business-processes/       ← 業務プロセス別 XML サンプル
├── wiki/                         ← 【Layer 2: Compounding LLM Wiki】(Markdown ナレッジベース)
│   ├── index.md                  ← コンテンツカタログ（全ページのリンクと要約）
│   ├── overview.md               ← Wiki 概要
│   ├── log.md                    ← Ingest / Query / Lint 更新履歴
│   ├── common/                   ← 共通基盤・共通型 (Party, Money, Shared Types)
│   ├── products/                 ← プロダクト・契約データモデル
│   ├── processes/                ← 業務プロセス・ライフサイクル・プライシング計算フロー
│   └── architecture/             ← DDD Bounded Contexts・マイクロサービス・非機能要件
├── docs/agents/                  ← 【Layer 3: Protocol & Agent Guidance】
│   ├── wiki.md                   ← LLM Wiki 運用プロトコル
│   ├── domain.md                 ← ドメイン文書参照規約
│   ├── issue-tracker.md          ← GitHub Issues 連携規約
│   └── triage-labels.md          ← トリアージラベル規約
├── docs/adr/                     ← アーキテクチャ決定記録 (ADR)
├── scripts/                      ← ハーネス自動化スクリプト (Linter, XSD Query)
└── .agents/                      ← エージェント設定・特化スキル
    ├── AGENTS.md                 ← ペルソナ・行動規範・検証義務
    └── skills/                   ← 実行スキル (fpml-wiki-lint, fpml-compound, fpml-xsd-query 等)
```

---

## 3. Standard Vocabulary & Terminology Rules

東京 OTC デリバティブ市場における実務用語を厳格に使用します。機械翻訳・直訳は固く禁止されます。

| 概念 / 英語 | NG 表現（機械翻訳・誤用） | OK 表現（日本の金融実務標準） |
|---|---|---|
| **Overnight Rate** | 一夜物金利 | **オーバーナイト金利 / 翌日物金利** (TONA: 無担保コール翌日物) |
| **Leg** / **Stream** | 脚、USD脚、JPY脚 | **レグ** (固定レグ、変動レグ、USDレグ、JPYレグ) |
| **Novation** | 契約改済 | **ノベーション / 契約更改** |
| **Confirmation** | コンフィメーション | **コンファーメーション / 約定確認** |
| **Discrepancy** | 不一致 | **相違 (Discrepancy) / アンマッチ** |
| **Derivative** | 誘導体 | **デリバティブ** |
| **Rate Fixing / Reset** | レート固定 | **レートFixing / リセット / 指標決定** |
| **Par Pricing** | 同等価格設定 | **パー・プライシング (NPV=0)** |
| **Principal Exchange** | 元金交換 | **元本交換 (期初/期末/期中)** |
| **Mark-to-Market Swap** | 市場評価スワップ | **mtMスワップ / 元本リセット型通貨スワップ** |

---

## 4. Front-Office Bounded Contexts (DDD)

フロントオフィス〜コンファーメーションに至るシステム設計では、以下の 5 つの境界付けられたコンテキストを前提とします：

1. **Pricing & Analytics Context**:
   - イールドカーブ・ボラティリティサーフェス構築、Parレート計算（NPV=0）、対顧スプレッド・マージン乗せ、感応度（Delta/Gamma/Vega）計算。
2. **Trade Capture & Booking Context**:
   - 取引合意内容のシステム入力、内部取引ID採番、ステータス管理、FpML `executionNotification` 生成。
3. **Confirmation & Matching Context**:
   - 取引相手（カウンターパーティ）との FpML メッセージ送受信（`requestConfirmation`）、主要経済条件（Economic terms）の自動照合・相違（アンマッチ）検知・アファメーション。
4. **Lifecycle & Fixing Event Context**:
   - 期中の金利リセット・Fixing、キャッシュフロー計算、元本交換、クーポン支払い、ノベーション（契約更改）、中途解約（Unwind/Termination）。
5. **Clearing & Settlement Context**:
   - CCP（JSCC, LCH等）への清算指図（`requestClearing`）、受託・清算完了通知、決済機関連携。

---

## 5. Harness Tools & Agent Commands

エージェントは以下の CLI ツールを活用して正確な作業を行います：

- **Wiki Linter**: `python scripts/wiki_lint.py`
  - リンク切れ、未登録ページ、ログ形式、NG 用語を検証。
- **XSD Query Tool**: `python scripts/xsd_query.py <command> <name>`
  - `python scripts/xsd_query.py element swap`
  - `python scripts/xsd_query.py type Swap`
  - `python scripts/xsd_query.py enum FloatingRateIndex`
  - `python scripts/xsd_query.py sub Payment`

---

## 6. Grounding & Anti-Hallucination Principles

1. **Grounding Priority**: XSD スキーマおよび XML サンプルを必ず検索・閲覧して根拠（ファイルパス・行番号）を取得する。
2. **Action-First**: Wiki やドキュメントの更新は必ずツールで実ファイルを変更してから完了報告を行う。
3. **Live URL Verification**: 外部 URL を提示する際は、事前に `read_url_content` 等で HTTP 200 を確認する。
