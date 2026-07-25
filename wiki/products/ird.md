---
title: Interest Rate Derivatives (IRD) Knowledge
tags: [fpml, ird, interest-rate, swap, fra, swaption]
updated: 2026-07-25
---

# 金利デリバティブ (Interest Rate Derivatives - IRD)

## 1. 概要と該当スキーマ

金利デリバティブ（IRD）は、金利スワップ（IRS）、FRA（金利先渡取引）、キャップ/フロア（Cap/Floor）、スワップション（Swaption）などを含む FpML の中核プロダクト分野です。

- **主スキーマ**: [`confirmation/fpml-ird-5-12.xsd`](../../confirmation/fpml-ird-5-12.xsd)
- **サンプル XML**: [`confirmation/products/interest-rate-derivatives/`](../../confirmation/products/interest-rate-derivatives)

---

## 2. 主要プロダクト構造

### 金利スワップ (`swap`)
固定金利と変動金利、あるいは変動金利同士（ベーシス・スワップ）のキャッシュフロー交換を定義します。2つの `swapStream` (固定レグ・変動レグ) から構成されます。

```xml
<swap>
    <!-- 固定レグ (Fixed Stream) -->
    <swapStream>
        <payerPartyReference href="party1"/>
        <receiverPartyReference href="party2"/>
        <calculationPeriodDates id="fixedCalcDates"> ... </calculationPeriodDates>
        <paymentDates> ... </paymentDates>
        <calculationPeriodAmount>
            <calculation>
                <notionalSchedule>
                    <notionalStepSchedule>
                        <initialValue>10000000.00</initialValue>
                        <currency>USD</currency>
                    </notionalStepSchedule>
                </notionalSchedule>
                <fixedRateSchedule>
                    <initialValue>0.025</initialValue>
                </fixedRateSchedule>
                <dayCountFraction>30/360</dayCountFraction>
            </calculation>
        </calculationPeriodAmount>
    </swapStream>
    <!-- 変動レグ (Floating Stream) -->
    <swapStream>
        <payerPartyReference href="party2"/>
        <receiverPartyReference href="party1"/>
        <calculationPeriodDates id="floatingCalcDates"> ... </calculationPeriodDates>
        <paymentDates> ... </paymentDates>
        <resetDates> ... </resetDates>
        <calculationPeriodAmount>
            <calculation>
                <notionalSchedule> ... </notionalSchedule>
                <floatingRateCalculation>
                    <floatingRateIndex>USD-SOFR-OIS Compound</floatingRateIndex>
                    <indexTenor>
                        <periodMultiplier>1</periodMultiplier>
                        <period>D</period>
                    </indexTenor>
                </floatingRateCalculation>
                <dayCountFraction>ACT/360</dayCountFraction>
            </calculation>
        </calculationPeriodAmount>
    </swapStream>
</swap>
```

---

## 3. 金利計算要素のポイント

- **`floatingRateIndex`**: SOFR, EURIBOR, TONA, TORF などの参照金利指標（Floating Rate Index）。
- **`dayCountFraction`**: 日数計算慣行・デイカウント・コンベンション (`ACT/360`, `ACT/365.FIXED`, `30/360`, `ACT/ACT.ISDA` 等)。
- **`compoundingMethod`**: コンパウンディング / 複利計算ルール (`Flat`, `Straight`, `SpreadExclusive` 等)。
- **`stubCalculationPeriod`**: スタブ期（変則計算期間）の金利補間計算 (`linearInterpolation`) ルール。

---

## 4. 関連 Wiki ページ
- [Shared Foundation](../common/shared-foundation.md)
- [Overview](../overview.md)
- [Cross-Currency Swaps (通貨スワップ)](./xccy-swap.md)
- [Non-Deliverable Swap (NDS) の期中 Fixing 済みキャッシュフロー表現とイベントモデル](./nds-cashflows-and-fixing.md)
- [Business Processes](../processes/business-processes.md)
