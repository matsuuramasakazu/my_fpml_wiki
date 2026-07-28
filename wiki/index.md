# FpML Knowledge Base Index

Welcome to the FpML (Financial Products Markup Language) Wiki for Confirmation View 5.12.
This wiki is continuously compiled and maintained by LLM agents following the Karpathy LLM Wiki pattern.

---

## 1. Core Wiki Overview & Architecture

- [Overview & Architecture](./overview.md) - FpML 5.12 Confirmation View の全体像、ディレクトリ構造、基本スキーマの関係性。
- [Front-Office Pricing & Confirmation Bounded Contexts](./architecture/pricing-bounded-contexts.md) - フロントオフィス（プライシング・約定・コンファーメーション）の業務フローを支える5つの境界付けられたコンテキスト（Bounded Context）およびマイクロサービス設計の解説。
- [XML Document Root Elements](./architecture/root-elements.md) - FpML 5.12 Confirmation View で定義されている最上位 XML ルートエレメントの一覧と用途・役割の解説。
- [Wiki Event Log](./log.md) - Ingest / Query / Lint の変更追記ログ。

---

## 2. Common Foundation & Core Types

- [Shared Foundation](./common/shared-foundation.md) - [`fpml-main-5-12.xsd`](../confirmation/fpml-main-5-12.xsd), [`fpml-shared-5-12.xsd`](../confirmation/fpml-shared-5-12.xsd), [`fpml-enum-5-12.xsd`](../confirmation/fpml-enum-5-12.xsd), [`fpml-asset-5-12.xsd`](../confirmation/fpml-asset-5-12.xsd) などの共通スキーマおよび基本構造 (`Party`, `Money`, `BusinessDayAdjustments` 等)。

---

## 3. Product Class Summaries

- [Interest Rate Derivatives (IRD)](./products/ird.md) - 金利スワップ (Swap)、FRA、キャップ/フロア、スワップション等の構造と [`fpml-ird-5-12.xsd`](../confirmation/fpml-ird-5-12.xsd) の解説。
- [Cross-Currency Swaps (通貨スワップ)](./products/xccy-swap.md) - RFR（USD SOFR vs JPY TONA）ベースの通貨スワップ構造、2レグ `swapStream`、元本交換（Principal Exchange）および元本リセット型（mtMスワップ）の期中 Rate Reset / Fixing イベント表現。
- [Non-Deliverable Swap (NDS) の期中 Fixing 済みキャッシュフロー表現とイベントモデル](./products/nds-cashflows-and-fixing.md) - NDS の期中 Fixing 済み・支払い未済キャッシュフロー（`fixingDate` / `fixingFxRate`）の表現、および `Business Event` / `TradeChangeAdvice` を用いた 4 つのアプローチの解説。
- [Foreign Exchange (FX)](./products/fx.md) - FX Spot/Forward, FX Option, FX Swap, Accruals/Targets 構造と [`fpml-fx-5-12.xsd`](../confirmation/fpml-fx-5-12.xsd) 他の解説。
- [Credit Derivatives](./products/credit.md) - Credit Default Swap (CDS)、Basket CDS、Credit Event Notice と [`fpml-cd-5-12.xsd`](../confirmation/fpml-cd-5-12.xsd) の解説。
- [Equity Derivatives](./products/equity.md) - Equity Swap, Equity Option, Forward, Variance Swap と [`fpml-eqd-5-12.xsd`](../confirmation/fpml-eqd-5-12.xsd) の解説。

---

## 4. Business Processes & Messaging

- [Front-Office Pricing & Confirmation Process Flow](./processes/pricing-and-confirmation-flow.md) - 時価ゼロ（NPV=0 / Par Swap）条件の計算ソルバー処理、対顧マージン乗せ、約定（Trade Capture）、照合（Confirmation Matching）、日々の Rate Fixing に至るフロントオフィス実務フロー。
- [Business Processes](./processes/business-processes.md) - Trade Confirmation（コンフィメーション）, Clearing（中央清算/CCP）, Allocation（アロケーション）, Option Events（権利行使等）などの業務プロセス・メッセージ表現。

---

## 5. Raw Sources Reference

- [fpml_xsd_catalog.md](../fpml_xsd_catalog.md) - 全 XSD スキーマファイルの一覧と関連プロダクトの対応マップ。
- [confirmation/](../confirmation) - 一次情報ソース (XSD スキーマ、サンプル XML ディレクトリ)。
