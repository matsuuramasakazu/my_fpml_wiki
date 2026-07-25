---
title: FpML 5.12 Confirmation View Overview
tags: [fpml, overview, confirmation-view, schema]
updated: 2026-07-25
---

# FpML 5.12 Confirmation View 概要

## 1. FpML 5.12 とは
FpML (Financial Products Markup Language) は、OTC（店頭）デリバティブ取引の契約・確認・決済・イベント伝達等を電子的に交換するための ISDA（国際スワップ・デリバティブ協会）標準 XML 規格です。

本ワークスペースで扱っている **Confirmation View**（コンファーメーション・ビュー）は、取引当事者間（カウンターパーティ間）で取引の確定経済条件（Economic Terms）やコンファーメーション（Confirmation / 契約確認書）を交換するための最も詳細で厳密なビューです。

---

## 2. リポジトリ構成と Raw Sources

本ワークスペースにおける一次情報（Raw Sources）は以下の通りです：

- **スキーマ本体**: [`confirmation/`](../confirmation)
  - ルート要素スキーマ: [`fpml-main-5-12.xsd`](../confirmation/fpml-main-5-12.xsd)
  - 共有データ型: [`fpml-shared-5-12.xsd`](../confirmation/fpml-shared-5-12.xsd)
  - 列挙型: [`fpml-enum-5-12.xsd`](../confirmation/fpml-enum-5-12.xsd)
  - 各アセットクラス別スキーマ ([`fpml-ird-5-12.xsd`](../confirmation/fpml-ird-5-12.xsd), [`fpml-fx-5-12.xsd`](../confirmation/fpml-fx-5-12.xsd), [`fpml-cd-5-12.xsd`](../confirmation/fpml-cd-5-12.xsd), [`fpml-eqd-5-12.xsd`](../confirmation/fpml-eqd-5-12.xsd) 等)
- **サンプル XML**:
  - プロダクト別サンプル: [`confirmation/products/`](../confirmation/products)
  - 業務プロセス別サンプル: [`confirmation/business-processes/`](../confirmation/business-processes)
- **カタログインデックス**: [`fpml_xsd_catalog.md`](../fpml_xsd_catalog.md)

---

## 3. 基本的な要素階層構造

FpML 取引メッセージの典型的なXMLルート構造は以下のようになっています：

```xml
<requestConfirmation xmlns="http://www.fpml.org/FpML-5/confirmation" ...>
    <header>
        <messageId messageIdScheme="...">MSG12345</messageId>
        <sentBy>PARTY_A</sentBy>
        <sendTo>PARTY_B</sendTo>
        <creationTimestamp>2026-07-25T12:00:00Z</creationTimestamp>
    </header>
    <trade>
        <tradeHeader>
            <partyTradeIdentifier>...</partyTradeIdentifier>
            <tradeDate>2026-07-25</tradeDate>
        </tradeHeader>
        <!-- 各プロダクト定義 (swap, fxSingleLeg, creditDefaultSwap, etc.) -->
        <swap> ... </swap>
        <party id="party1"> ... </party>
        <party id="party2"> ... </party>
    </trade>
</requestConfirmation>
```

---

## 4. 関連Wikiページ

- [Shared Foundation](./common/shared-foundation.md) - 共通型や営業日調整ルールの詳細
- [Interest Rate Derivatives](./products/ird.md) - 金利デリバティブ等の詳細
- [Foreign Exchange](./products/fx.md) - 為替取引の詳細
- [Credit Derivatives](./products/credit.md) - クレジット・デリバティブの詳細
- [Equity Derivatives](./products/equity.md) - 株式デリバティブの詳細
- [Business Processes](./processes/business-processes.md) - コンファーメーション・中央清算（Clearing）フローの詳細
