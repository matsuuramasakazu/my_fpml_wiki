---
title: Foreign Exchange (FX) Knowledge
tags: [fpml, fx, spot, forward, option, fx-swap, accruals, targets]
updated: 2026-07-25
---

# 外国為替取引 (Foreign Exchange - FX)

## 1. 概要と該当スキーマ

FX（外国為替デリバティブ）プロダクトは、FXスポット・直物（Spot）、FXフォワード・先物（Forward）、FXスワップ、FXオプション、バリア・オプション、アクルーアル商品（Accruals）、TARF（Target Redemption Forward）など多様な取引形態をカバーします。

- **主スキーマ**:
  - [`confirmation/fpml-fx-5-12.xsd`](../../confirmation/fpml-fx-5-12.xsd) - FX Spot, Forward, Option, Digital Option, Barrier Option
  - [`confirmation/fpml-fx-accruals-5-12.xsd`](../../confirmation/fpml-fx-accruals-5-12.xsd) - FX アクルーアル (Accrual) 構造
  - [`confirmation/fpml-fx-targets-5-12.xsd`](../../confirmation/fpml-fx-targets-5-12.xsd) - TARF (Target Redemption Forward)
- **サンプル XML**: [`confirmation/products/fx-derivatives/`](../../confirmation/products/fx-derivatives)

---

## 2. 主要プロダクト構造

### FX 単一レグ (`fxSingleLeg`: Spot / Forward)
2通貨間の受渡金額、適用約定レート (Exchange Rate)、受渡日 / 決済日 (Value Date) を定義します。

```xml
<fxSingleLeg>
    <exchangedCurrency1>
        <payerPartyReference href="party1"/>
        <receiverPartyReference href="party2"/>
        <paymentAmount>
            <currency>USD</currency>
            <amount>1000000.00</amount>
        </paymentAmount>
    </exchangedCurrency1>
    <exchangedCurrency2>
        <payerPartyReference href="party2"/>
        <receiverPartyReference href="party1"/>
        <paymentAmount>
            <currency>JPY</currency>
            <amount>155000000.00</amount>
        </paymentAmount>
    </exchangedCurrency2>
    <valueDate>2026-07-27</valueDate>
    <exchangeRate>
        <quotedCurrencyPair>
            <currency1>USD</currency1>
            <currency2>JPY</currency2>
            <quoteBasis>Currency2PerCurrency1</quoteBasis>
        </quotedCurrencyPair>
        <rate>155.00</rate>
    </exchangeRate>
</fxSingleLeg>
```

### FX オプション (`fxOption`)
Call/Put 権利、ストライクレート、権利行使スタイル（European/American）、バリア（Knock-in/Knock-out）を表現します。

```xml
<fxOption>
    <buyerPartyReference href="party1"/>
    <sellerPartyReference href="party2"/>
    <effectiveDate>
        <unadjustedDate>2026-07-25</unadjustedDate>
    </effectiveDate>
    <europeanExercise>
        <expiryDate>2026-10-25</expiryDate>
        <expiryTime>
            <hourMinuteTime>15:00:00</hourMinuteTime>
            <businessCenter>JPTO</businessCenter>
        </expiryTime>
    </europeanExercise>
    <putCurrencyAmount>
        <currency>USD</currency>
        <amount>1000000.00</amount>
    </putCurrencyAmount>
    <callCurrencyAmount>
        <currency>JPY</currency>
        <amount>155000000.00</amount>
    </callCurrencyAmount>
    <strike>
        <rate>155.00</rate>
    </strike>
</fxOption>
```

---

## 3. 関連 Wiki ページ
- [Shared Foundation](../common/shared-foundation.md)
- [Overview](../overview.md)
- [Index](../index.md)
