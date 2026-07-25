---
title: FpML Common Foundation & Shared Schemas
tags: [fpml, shared, foundation, types, schemas]
updated: 2026-07-25
---

# FpML 共通基盤 & 共有型 (Shared Foundation)

## 1. 共通スキーマ構成

すべての FpML 5.12 プロダクト構造は、以下の基盤 XSD スキーマに依存しています：

| スキーマファイル | 役割・概要 |
| --- | --- |
| [`fpml-main-5-12.xsd`](../../confirmation/fpml-main-5-12.xsd) | ルート要素定義、取引メッセージ・プロセスメッセージの基本コンテナ定義 |
| [`fpml-shared-5-12.xsd`](../../confirmation/fpml-shared-5-12.xsd) | 金額 (`Money`), 取引当事者 (`Party`), 日付構造 (`AdjustedDate`), 営業日調整 (`BusinessDayAdjustments`) 等の広範な共通型定義 |
| [`fpml-enum-5-12.xsd`](../../confirmation/fpml-enum-5-12.xsd) | ISDA 規定値、通貨コード、支払頻度、営業日調整コンベンション等の列挙型定義 |
| [`fpml-asset-5-12.xsd`](../../confirmation/fpml-asset-5-12.xsd) | 原資産 (Underlyer: 株式, 債券, 指数, 商品等) や手数料・配当関連のデータ構造 |

---

## 2. 主要な共通 Complex Types

### Money 型
金額と通貨コードを表現する基本型。
```xml
<amount>
    <currency>USD</currency>
    <amount>10000000.00</amount>
</amount>
```

### BusinessDayAdjustments 型
ISDA 慣行に基づく営業日調整ルールを定義。
- `businessDayConvention`: `FOLLOWING`（翌営業日）, `MODFOLLOWING`（変形翌営業日 / Modified Following）, `PRECEDING`（前営業日）, `MODPRECEDING`（変形前営業日）, `NONE` 等。
- `financialBusinessCenters`: `USNY` (New York), `GBLO` (London), `JPTO` (Tokyo) 等の休業日都市・営業日センター。

```xml
<dateAdjustments>
    <businessDayConvention>MODFOLLOWING</businessDayConvention>
    <financialBusinessCenters>
        <financialBusinessCenter>GBLO</financialBusinessCenter>
        <financialBusinessCenter>USNY</financialBusinessCenter>
    </financialBusinessCenters>
</dateAdjustments>
```

### Party 型
取引の当事者（金融機関、ファンド、CP / カウンターパーティ等）を表す要素。
```xml
<party id="party1">
    <partyId partyIdScheme="http://www.fpml.org/coding-scheme/external/iso17442">LEI1234567890ABCDEFG</partyId>
    <partyName>Bank A</partyName>
</party>
```

---

## 3. 関連 Wiki ページ
- [Overview](../overview.md)
- [Interest Rate Derivatives](../products/ird.md)
- [Index](../index.md)
