# FpML Wiki Chronological Event Log

This is an event log tracking all Ingest, Query compounding, and Lint operations performed on the Wiki (ordered reverse-chronologically).

## [2026-08-13] query | ecore:reference メタデータの詳細構造・XSDEcoreBuilder マッピング情報ソースおよび FpML アーキテクチャ設計背景の追記
- `confirmation/fpml-shared-5-12.xsd` (L7, L2845)、W3C XML Schema 1.0 仕様 (Sec 3.3.9)、および Eclipse EMF `ExtendedMetaData.java` / `XSDEcoreBuilder` クラス仕様を具体的に引用。
- `ecore:reference` が `containment=false` かつ `eType=Party` である `EReference` インスタンスへマッピングされる具体的処理クラス (`org.eclipse.xsd.ecore.XSDEcoreBuilder`) の情報ソースを明示。
- FpML 標準化委員会 (AWG) による FpML 4.3 以降の Ecore アノテーション導入の技術的・歴史的設計背景 (4.2.3) を追加。
- `wiki/common/shared-foundation.md` Section 4.2 (4.2.1~4.2.3) を改訂・追記。

## [2026-08-13] lint | エージェントハーネス (AGENTS.md & wiki.md) における外部URL提示前実アクセス検証ルールの厳格化
- エージェント行動規範 `.agents/AGENTS.md` の `Strict Execution & Anti-Hallucination Protocol` および `docs/agents/wiki.md` に **`Mandatory Live URL Verification Protocol`** を追加・制定。
- 今後エージェントがユーザーへの回答、ドキュメント、Wiki 内で外部 Web ページの URL を提示・還元する際は、必ず同一ターン内で `read_url_content` ツール等を用いて実アクセス検証（200 OK かつコンテンツ実在確認）を実施してから出力することを義務付け。

## [2026-08-12] query | PartyReference における xsd:IDREF と ecore:reference="Party" の定義と構造的役割
- `confirmation/fpml-shared-5-12.xsd` 内の `PartyReference` complexType における `href` 属性の `type="xsd:IDREF"` および `ecore:reference="Party"` の定義と設計目的を調査。
- `xsd:IDREF` (W3C XML Schema 組込み型) による XML 文書内ポインタ・参照整合性検証の仕組みと、`ecore:reference` (Eclipse Modeling Framework / Ecore 拡張メタデータ) によるコード自動生成・強型付けドメインモデル補強の役割を整理。
- ツール (`read_url_content`) を用いて W3C 公式仕様 URL (`xmlschema-2/#IDREF`, `xmlschema11-2/#IDREF`)、Eclipse EMF 公式プロジェクト URL (`eclipse.dev/modeling/emf/`)、Eclipse ExtendedMetaData Official GitHub URL を実アクセス検証（200 OK 確認済み）。
- `wiki/common/shared-foundation.md` に Section 4 (4.1~4.3) を追加し更新。

## [2026-08-07] query | NDS Fixing Rate ResetEvent の最上位 Root Element 選択肢と構造比較評価
- NDS (Non-Deliverable Swap) 等における Fixing 結果データ保持・伝送のた​​めの `ResetEvent` (`<reset>`) のコンテナとなる Root Element の選択肢を評価。
- `fpml-confirmation-processes-5-12.xsd` の `<executionAdvice>` (標準/推奨), `<responseData>`, `<tradeChangeAdvice>` および `fpml-doc-5-12.xsd` の `<dataDocument>` (XSD上不適合) を比較。
- `wiki/processes/reset-events.md` を作成し `wiki/index.md` を更新。

## [2026-07-29] query | FloatingRateDefinitionにおける複数capRate/floorRate要素の定義と実務用途の解釈
- `confirmation/fpml-ird-5-12.xsd` 内の `FloatingRateDefinition` 型において `capRate` / `floorRate` が `maxOccurs="unbounded"` で定義されている根拠と用途を調査・解釈。
- キャップ・スプレッド (Cap Spread) / コリドー・スワップ (Corridor Swap) やフロア・スプレッド (Floor Spread) において、同一計算期間に売買方向（`buyer`/`seller`）およびストライク水準の異なる複数のオプションが同一レグ上に同居する実務上の必要性を整理。
- `wiki/products/ird.md` に Section 4 として Strike 3.0% Long Cap / Strike 5.0% Short Cap の具体的な FpML XML スニペット、ネット実効支払金利 ($R_{\text{net}}$) の全体算式、およびPayoffダイアグラムを追加。

## [2026-07-28] query | Compounded mtM Cross-Currency Swap Rate Reset Event & Trade State Cashflows modeling
- Analyzed FpML 5.12 Business Events schema (`fpml-business-events-5-12.xsd`), IRD schema (`fpml-ird-5-12.xsd`), and sample XMLs (`reset_ex01.xml`, `ird-ex26-fxnotional-swap-with-cfs.xml`).
- Documented mtM Swap Rate Reset / Fixing event structures using `<reset>` (`ResetEvent`) for lifecycle event notification, and `swapStream/cashflows` (`Cashflows` / `paymentCalculationPeriod` / `fxLinkedNotionalAmount` / `principalExchange`) for current Trade State representation.
- Compounded knowledge into `wiki/products/xccy-swap.md` Section 5 (5.1-5.4) and updated `wiki/index.md`.

## [2026-07-28] query | Compounded Day Count Fraction 30E/360 vs 30E/360.ISDA comparative analysis
- Analyzed FpML CodeList (`codelist/day-count-fraction-2-3.xml` L67-L100) and ISDA Definitions (2006/2021).
- Formulated math algorithms and Termination Date exception rules for Eurobond Basis (`30E/360`) vs ISDA Eurobond Method (`30E/360.ISDA`).
- Compounded knowledge into `wiki/common/shared-foundation.md` Section 3 and updated `wiki/index.md`.

## [2026-07-25] lint | Converted all unlinked Raw source file mentions (XSD schemas) to relative links
- Updated `docs/agents/wiki.md` formatting guidelines to mandate linking all Raw file mentions.
- Replaced unlinked inline code mentions of XSD schemas (`fpml-main-5-12.xsd`, `fpml-shared-5-12.xsd`, `fpml-ird-5-12.xsd`, etc.) with relative Markdown links in `index.md`, `overview.md`, `shared-foundation.md`, and `architecture/root-elements.md`.

## [2026-07-25] lint | Migrated all Wiki inter-file Markdown links to relative paths
- Updated `docs/agents/wiki.md` Agent formatting guidelines to mandate relative Markdown links.
- Replaced all absolute `file:///...` links with relative paths (`./`, `../`, `../../`) across all Wiki pages (`index.md`, `overview.md`, `shared-foundation.md`, `ird.md`, `fx.md`, `credit.md`, `equity.md`, `business-processes.md`, `root-elements.md`).

## [2026-07-25] query | Compounded FpML 5.12 Confirmation View XML Document Root Elements Analysis
- Analyzed XSD schemas in `confirmation/` (`fpml-main-5-12.xsd`, `fpml-confirmation-processes-5-12.xsd`, `fpml-clearing-processes-5-12.xsd`, `fpml-msg-5-12.xsd` etc.).
- Compiled full taxonomy and usage explanation of XML Document Root Elements.
- Created new Wiki page: `wiki/architecture/root-elements.md` and updated `wiki/index.md`.

## [2026-07-25] lint | Comprehensive Japanese OTC derivative market terminology review across all Wiki pages
- Reviewed all Markdown files under `wiki/` against standard Japanese OTC market terminology.
- `wiki/processes/business-processes.md`: Fixed typo `termation` -> `termination` (中途解約). Standardized `Clearing` (中央清算/CCP), `Confirmation` (コンファーメーション / 約定確認), `Novation` (ノベーション / 契約更改).
- `wiki/overview.md`: Refined ISDA (国際スワップ・デリバティブ協会), Confirmation (コンファーメーション・ビュー).
- `wiki/common/shared-foundation.md`: Standardized `Party` (取引当事者 / カウンターパーティ), `BusinessDayAdjustments` (営業日調整コンベンション・休業日都市).
- `wiki/products/fx.md`: Standardized FX Spot (直物), FX Forward (先物), Accruals (アクルーアル), Value Date (受渡日/決済日).
- `wiki/products/ird.md`: Standardized Floating Rate Index (参照金利指標: SOFR, EURIBOR, TONA, TORF), Stub Period (スタブ期 / 変則計算期間).
- `wiki/products/credit.md`: Standardized Reference Entity (参照体 / 参照企業), Protection Terms / Credit Events (プロテクション条件・信用事由), Deliverable Obligation (現物決済対象債務要件).
- `wiki/products/equity.md`: Standardized Extraordinary Events (特別事象: 組織再編・合併、株式分割、上場廃止等), Strike (権利行使価格 / ストライク).

## [2026-07-25] lint | Fixed market terminology across Agent rules & Wiki pages
- Corrected "誘導体" to "デリバティブ" across all documentation.
- Corrected "先渡金利協定" to "FRA" / "金利先渡取引".
- Corrected "固定脚・変動脚" to "固定レグ・変動レグ".
- Generalized terminology guideline principles in `AGENTS.md` and `docs/agents/wiki.md`.

## [2026-07-25] ingest | Initial setup of FpML 5.12 Wiki base structure
- Initialized LLM Wiki pattern framework (Raw sources, Wiki, Schema protocol).
- Added `docs/agents/wiki.md` protocol and linked from `AGENTS.md`.
- Created main index `wiki/index.md` and initial domain pages: `overview.md`, `common/shared-foundation.md`, `products/ird.md`, `products/fx.md`, `products/credit.md`, `products/equity.md`, and `processes/business-processes.md`.

## [2026-07-25] query | Compound Back: Added Front-Office Pricing & Confirmation Bounded Contexts page
- Synthesized query analysis of FpML 5.12 reference model for USD/JPY SOFR/TONA XCCY Basis Swaps.
- Documented 5 Bounded Contexts (Booking, Market Data, Pricing & Risk, Confirmation, Rate Observation).
- Linked DDD microservice architecture with the 8 core microservice values.
- Created `wiki/architecture/pricing-bounded-contexts.md` and updated `wiki/index.md`.

## [2026-07-25] query | Compound Back: Refactored Wiki to correctly distribute Product, Process, and Architecture domain knowledge
- Created `wiki/products/xccy-swap.md`: Deep product structure for USD/JPY SOFR vs TONA Cross-Currency Basis Swap (2-leg `swapStream`, `principalExchanges`, RFR Compounding).
- Created `wiki/processes/pricing-and-confirmation-flow.md`: In-depth front-office business process flow (NPV=0 Par Pricing Solver, Sales/Dealer Margin adjustment, RFQ, Execution, Trade Capture, Confirmation Matching, Rate Fixing).
- Refactored `wiki/architecture/pricing-bounded-contexts.md`: Re-defined Pricing & Risk Analytics BC around Par Swap NPV=0 Solver and Greeks simulation; linked to products and processes.
- Updated `wiki/index.md` to cleanly categorize all 3 new/refactored files.

## [2026-07-25] lint | Standardized OTC derivative market terminology across all Wiki pages
- Standardized `Leg` to 「レグ (Leg)」 (replaced literal translation 「脚」 in `xccy-swap.md`, `pricing-and-confirmation-flow.md`, `index.md`).
- Standardized `Confirmation` to 「コンファーメーション (Confirmation)」 (replaced 「コンフィメーション」 in `business-processes.md`, `overview.md`, `root-elements.md`).
- Standardized `Novation` to 「ノベーション (Novation / 契約更改)」 (replaced literal translation 「契約改済」 in `business-processes.md`).
- Standardized `Discrepancy` to 「相違 (Discrepancy) / アンマッチ」.

## [2026-07-25] query | Compounded NDS mid-life fixing cashflows & event modeling guidelines
- Analyzed FpML 5.12 Confirmation View XSD schemas and sample XMLs for NDS / NDF mid-life fixing representation.
- Documented schema constraints (`PaymentCalculationPeriod` vs `settlementProvision/nonDeliverableSettlement`).
- Formulated 4 implementation approaches: `forecastPaymentAmount` (Trade state), Vendor extension (`ext:fxFixing`), Business Events (`reset` / `observation`), and `TradeChangeAdvice` (`TradeChangeContent` with `versionedTradeId`).
- Created `wiki/products/nds-cashflows-and-fixing.md` and updated `wiki/products/ird.md`, `wiki/index.md`.
