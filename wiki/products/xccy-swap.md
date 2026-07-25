---
title: Cross-Currency Swaps (通貨スワップ) Knowledge
tags: [fpml, ird, xccy-swap, sofr, tona, rfr, principal-exchange]
schemas: [fpml-ird-5-12.xsd, fpml-shared-5-12.xsd]
updated: 2026-07-25
---

# 通貨スワップ (Cross-Currency Swap - XCCY IRS)

## 1. 概要と該当スキーマ

通貨スワップ（Cross-Currency Interest Rate Swap）は、異なる2通貨間で元本および金利キャッシュフロー（固定金利または変動金利）を交換するOTCデリバティブ取引です。現在、金融先進国（米国・日本等）の銀行間市場で最も取引量が多い標準的取引は、LIBOR廃止後の **RFR（Risk-Free Rate: SOFR vs TONA）ベースの Cross-Currency Basis Swap** です。

- **主スキーマ**: [`confirmation/fpml-ird-5-12.xsd`](../../confirmation/fpml-ird-5-12.xsd)
- **サンプル XML**: [`confirmation/products/interest-rate-derivatives/ird-ex052-xccy-swap-OIS.xml`](../../confirmation/products/interest-rate-derivatives/ird-ex052-xccy-swap-OIS.xml)

---

## 2. 実務プロダクト構造: USD/JPY SOFR vs TONA Basis Swap

標準的な USD/JPY 通貨ベーススワップの構成要素：

- **Leg 1 (USD Leg)**: USD SOFR（Daily Compounding OIS） + Basis Spread / 想定元本 USD 100M
- **Leg 2 (JPY Leg)**: JPY TONA（Daily Compounding OIS） / 想定元本 JPY 15.5B（約定時点のFXスポットレート換算）
- **Principal Exchange (元本交換)**:
  - **Initial Principal Exchange (期初元本交換)**: 約定日に USD 100M と JPY 15.5B を相互交換。
  - **Final Principal Exchange (期末元本交換)**: 満期日に期初と同額の元本を逆交換（Mark-to-Market 変動なしモデルの場合）。

---

## 3. FpML 5.12 における構造表現

FpML では `swap` 要素内に2つの `swapStream`（USDレグ・JPYレグ）と `principalExchanges`（元本交換スケジュール）を保持します。

```xml
<swap>
    <productType>InterestRate:CrossCurrency:FixedFloat</productType>
    <!-- USD Leg (SOFR Compound + Basis Spread) -->
    <swapStream id="USD-SOFR-Leg">
        <payerPartyReference href="partyA"/>
        <receiverPartyReference href="partyB"/>
        <calculationPeriodDates id="usdCalcDates"> ... </calculationPeriodDates>
        <paymentDates> ... </paymentDates>
        <resetDates> ... </resetDates>
        <calculationPeriodAmount>
            <calculation>
                <notionalSchedule>
                    <notionalStepSchedule>
                        <initialValue>100000000.00</initialValue>
                        <currency>USD</currency>
                    </notionalStepSchedule>
                </notionalSchedule>
                <floatingRateCalculation>
                    <floatingRateIndex>USD-SOFR-OIS Compound</floatingRateIndex>
                    <!-- 通貨スワップの市場対価となるベーススプレッド -->
                    <spread>0.0015</spread> <!-- +15bps -->
                </floatingRateCalculation>
                <dayCountFraction>ACT/360</dayCountFraction>
            </calculation>
        </calculationPeriodAmount>
        <!-- 期初・期末元本交換の定義 -->
        <principalExchanges>
            <initialExchange>true</initialExchange>
            <finalExchange>true</finalExchange>
            <intermediateExchange>false</intermediateExchange>
        </principalExchanges>
    </swapStream>

    <!-- JPY Leg (TONA Compound) -->
    <swapStream id="JPY-TONA-Leg">
        <payerPartyReference href="partyB"/>
        <receiverPartyReference href="partyA"/>
        <calculationPeriodDates id="jpyCalcDates"> ... </calculationPeriodDates>
        <paymentDates> ... </paymentDates>
        <resetDates> ... </resetDates>
        <calculationPeriodAmount>
            <calculation>
                <notionalSchedule>
                    <notionalStepSchedule>
                        <initialValue>15500000000.00</initialValue>
                        <currency>JPY</currency>
                    </notionalStepSchedule>
                </notionalSchedule>
                <floatingRateCalculation>
                    <floatingRateIndex>JPY-TONA-OIS Compound</floatingRateIndex>
                </floatingRateCalculation>
                <dayCountFraction>ACT/365.FIXED</dayCountFraction>
            </calculation>
        </calculationPeriodAmount>
        <principalExchanges>
            <initialExchange>true</initialExchange>
            <finalExchange>true</finalExchange>
            <intermediateExchange>false</intermediateExchange>
        </principalExchanges>
    </swapStream>
</swap>
```

---

## 4. 金利計算および市場特徴の深掘り

1. **RFR (SOFR/TONA) OIS 複利計算**:
   - 従来の 3M LIBOR 等と異なり、日々のオーバーナイト金利（Overnight Rate / 翌日物金利）を計算期間末まで複利（Compounding）で計算します。
   - 実務では支払日直前の金利確定猶予を設けるため、`observationShift`（観測シフト）や `lookback` ルールが適用されます。

2. **Cross-Currency Basis Spread (通貨ベーススプレッド)**:
   - 米ドル資金のグローバルな需給偏置（ドル流動性プレミアム）を反映するため、USDレグまたはJPYレグの金利にベーススプレッド（例: +15 bps）が付加されます。
   - プライシング時には、このベーススプレッドが現在価値（NPV）をゼロにする直接の計算対象となります。

---

## 5. 関連 Wiki ページ
- [Interest Rate Derivatives (IRD)](./ird.md)
- [Front-Office Pricing & Confirmation Business Process Flow](../processes/pricing-and-confirmation-flow.md)
- [Front-Office Pricing & Confirmation Bounded Contexts](../architecture/pricing-bounded-contexts.md)
