---
title: Equity Derivatives Knowledge
tags: [fpml, equity, equity-option, equity-swap, variance-swap, dividend-swap]
updated: 2026-07-25
---

# 株式デリバティブ (Equity Derivatives)

## 1. 概要と該当スキーマ

株式デリバティブ分野は、個別株・株価指数・ETFを原資産とするオプション、フォワード、エクイティスワップ、配当スワップ (Dividend Swap)、ボラティリティ/バリアンス・スワップ (Variance Swap) などをカバーします。

- **主スキーマ**:
  - [`confirmation/fpml-eqd-5-12.xsd`](../../confirmation/fpml-eqd-5-12.xsd) - Equity Option, Equity Forward
  - [`confirmation/fpml-eq-shared-5-12.xsd`](../../confirmation/fpml-eq-shared-5-12.xsd) - エクイティ共通型 (Equity Swap Leg / Stream 等)
  - [`confirmation/fpml-variance-swaps-5-12.xsd`](../../confirmation/fpml-variance-swaps-5-12.xsd) - Variance Swap
  - [`confirmation/fpml-dividend-swaps-5-12.xsd`](../../confirmation/fpml-dividend-swaps-5-12.xsd) - Dividend Swap
- **サンプル XML**: [`confirmation/products/equity-options/`](../../confirmation/products/equity-options), [`confirmation/products/equity-swaps/`](../../confirmation/products/equity-swaps)

---

## 2. 主要プロダクト構造

### Equity Option (`equityOption`)
株価指数や個別株オプションの定義。権利行使価格 / ストライク (`strike`), プット/コール, スタイル (European/American/Bermudan) を表します。

```xml
<equityOption>
    <buyerPartyReference href="party1"/>
    <sellerPartyReference href="party2"/>
    <optionType>Call</optionType>
    <underlyer>
        <singleUnderlyer>
            <index>
                <instrumentId instrumentIdScheme="http://www.fpml.org/coding-scheme/external/instrument-id-RIC">.SPX</instrumentId>
                <description>S&amp;P 500 Index</description>
            </index>
        </singleUnderlyer>
    </underlyer>
    <equityExercise>
        <equityEuropeanExercise>
            <expirationDate>
                <unadjustedDate>2026-12-18</unadjustedDate>
            </expirationDate>
        </equityEuropeanExercise>
    </equityExercise>
    <strike>
        <strikePrice>5500.00</strikePrice>
    </strike>
</equityOption>
```

---

## 3. エクイティ特有の概念
- **`extraordinaryEvents`**: 特別事象（Extraordinary Events: 組織再編・合併、株式分割、上場廃止 / Delisting 等の契約調整条項）。
- **`dividendConditions`**: 配当条件（`dividendConditions`: 配当再投資 `dividendReinvestment`, 配当支払日 `dividendPaymentDate` 等）。

---

## 4. 関連 Wiki ページ
- [Shared Foundation](../common/shared-foundation.md)
- [Overview](../overview.md)
- [Index](../index.md)
