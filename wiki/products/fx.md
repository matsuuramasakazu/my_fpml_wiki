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
        <valueDate>2026-10-27</valueDate>
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

#### 権利行使スタイル（Exercise Style）の相違
- **ヨーロピアン (`europeanExercise`)**: 権利行使期日が特定日（`expiryDate`）のみ。受渡日（`valueDate`）も確定日となります。受渡期間に幅を持たせる「期間渡し」構造は不可。
  - サンプル: [`confirmation/products/fx-derivatives/fx-ex09-euro-opt.xml`](../../confirmation/products/fx-derivatives/fx-ex09-euro-opt.xml)
- **アメリカン (`americanExercise`)**: 行使開始日（`commencementDate`）から満期日（`expiryDate`）までの期間中、いつでも権利行使が可能。最終受渡日（`latestValueDate`）および複数回行使（`multipleExercise`）の設定も可能。
  - サンプル: [`confirmation/products/fx-derivatives/fx-ex10-amer-opt.xml`](../../confirmation/products/fx-derivatives/fx-ex10-amer-opt.xml)

#### ヨーロピアン・オプションの期間渡し（Option on a Flexible Forward）の FpML 表現と制約
為替実務において「権利行使判定は特定日（ヨーロピアン行使）だが、行使された場合の資金決済が単一期日ではなく期間渡し（Flexible Forward / Delivery Option）となる取引」に対する FpML 表現の可否と実務的扱いは以下の通りです。

1. **標準 `<fxOption>` スキーマ制約（約定段階での直接表現は不可）**:
   - [`confirmation/fpml-fx-5-12.xsd`](../../confirmation/fpml-fx-5-12.xsd) の `FxEuropeanExercise` では、受渡日は `<valueDate>`（型: `xsd:date`）という**単一の固定日**として厳格に型定義されています。受渡期間（`executionPeriodDates` や `startDate`〜`endDate`）を指定する要素や、原資産として別のプロダクト（`fxFlexibleForward`）を内包する構造はスキーマ上に存在しません。
   - したがって、「FpMLで表現できるがサンプルファイルが無いだけ」ではなく、**「FpML 5.12 Confirmation ビューの標準 `<fxOption>` スキーマの文法上、ヨーロピアン行使かつ受渡を期間渡しにする構造自体が存在しない（定義不可）」**というのが正確なアーキテクチャ上の事実です。
2. **ライフサイクル・イベント（権利行使時）による表現**:
   - オプション行使通知メッセージ（`executionNotification` / [`confirmation/fpml-business-events-5-12.xsd`](../../confirmation/fpml-business-events-5-12.xsd)）における `PhysicalSettlement` 構造では、行使結果の現物受渡取引として任意の `<product>`（置換グループ）を指定可能です。
   - 通常行使では `<fxSingleLeg>` が格納されますが（例: [`confirmation/business-processes/option-exercise-expiry/msg-exX-exercise-notification-fx-option.xml`](../../confirmation/business-processes/option-exercise-expiry/msg-exX-exercise-notification-fx-option.xml)）、ここに `<fxFlexibleForward>` を配置することで「行使結果として期間渡し為替予約が派生・生成された」というイベントを表現することは可能です（ただし約定時点の単一プロダクトコンファーメーションではありません）。
3. **約定コンファーメーション時の実務解法**:
   - **`<genericProduct>` の採用**: 標準 `<fxOption>` の枠外として [`confirmation/fpml-generic-5-12.xsd`](../../confirmation/fpml-generic-5-12.xsd) を用い、ヨーロピアン判定と期間渡し受渡特性をカスタム記述する。
   - **プライベート拡張（Proprietary Extension）**: 金融機関・ベンダー固有のスキーマ拡張により、`<fxOption>` 配下に独自受渡期間エレメントを付与する。

---

### 期間渡し為替予約 / フレキシブル・フォワード (`fxFlexibleForward`)

日本の為替実務（店頭取引）において**「期間渡し為替予約」「デリバリー・オプション（Delivery Option Forward / Window Forward）」**と呼ばれる取引です。顧客が受渡期日を選択できる権利（オプション性）を有するため「オプション」と通称されることが多いですが、金融商品としては**為替予約（Forward）の一種**としてモデル化されています。

FpML 5.12 では独立したプロダクト `<fxFlexibleForward>`（型: `FxFlexibleForward`、[`confirmation/fpml-fx-5-12.xsd`](../../confirmation/fpml-fx-5-12.xsd)）として定義されています。

- **主要構成要素**:
  - `executionPeriodDates`: 受渡実行可能期間（`startDate` 〜 `expiryDate`）。
  - `minimumExecutionAmount`: 分割受渡が可能な場合の最小実行金額単位。
  - `settlementDateOffset`: 実行通知から実際の資金受渡までの営業日数オフセット（通常 T+2）。
  - `forwardRate`: 約定先物為替相場。
- **代表サンプル XML**:
  - [`confirmation/products/fx-derivatives/fx-ex27-flexible-term-forward.xml`](../../confirmation/products/fx-derivatives/fx-ex27-flexible-term-forward.xml)

```xml
<fxFlexibleForward>
    <buyerPartyReference href="partyB"/>
    <sellerPartyReference href="partyA"/>
    <putCurrency>USD</putCurrency>
    <callCurrency>EUR</callCurrency>
    <notionalAmount>
        <currency>EUR</currency>
        <amount>10000000</amount>
    </notionalAmount>
    <minimumExecutionAmount>
        <currency>EUR</currency>
        <amount>500000</amount>
    </minimumExecutionAmount>
    <executionPeriodDates id="purchasePeriod">
        <startDate>2011-09-30</startDate>
        <expiryDate>2012-12-30</expiryDate>
        <businessCenters>
            <businessCenter>EUTA</businessCenter>
        </businessCenters>
    </executionPeriodDates>
    <settlementDateOffset>
        <periodMultiplier>2</periodMultiplier>
        <period>D</period>
        <dayType>Business</dayType>
        <businessDayConvention>FOLLOWING</businessDayConvention>
        <businessCenters>
            <businessCenter>EUTA</businessCenter>
            <businessCenter>USNY</businessCenter>
        </businessCenters>
        <dateRelativeTo href="purchasePeriod"/>
    </settlementDateOffset>
    <forwardRate>
        <currency1>USD</currency1>
        <currency2>EUR</currency2>
        <quoteBasis>Currency1PerCurrency2</quoteBasis>
        <rate>1.375</rate>
    </forwardRate>
</fxFlexibleForward>
```

---

## 3. 関連 Wiki ページ
- [Shared Foundation](../common/shared-foundation.md)
- [Overview](../overview.md)
- [Index](../index.md)
