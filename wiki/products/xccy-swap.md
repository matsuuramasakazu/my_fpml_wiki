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

---

## 5. 元本リセット型通貨スワップ（mtM Swap）における期中 Rate Reset / Fixing イベント表現

元本リセットタイプの通貨スワップ（Mark-to-Market Cross-Currency Swap / **mtMスワップ**）において、期中に為替レート（FX Spot Rate）が確定（Fixing / Reset）し、変動レグ側の**想定元本（Notional Amount）**および元本交換差額（Principal Exchange）が再計算・確定した際のイベント情報は、FpML 5.12 Business Events スキーマ ([`confirmation/fpml-business-events-5-12.xsd`](../../confirmation/fpml-business-events-5-12.xsd#L939-L971)) において **`<reset>` 要素（`ResetEvent` 型）** で表現されます。

### 5.1 スキーマ構造と構成要素 (`ResetEvent` / `ResetCalculationDetails`)
- **`<reset>` (`ResetEvent`)** ([`fpml-business-events-5-12.xsd` L939-L971](../../confirmation/fpml-business-events-5-12.xsd#L939-L971)):
  - `<tradeReference>`: 対象となる mtM スワップ取引の参照 (`partyTradeIdentifier`)。
  - `<legIdentifier>`: リセット対象となるスワップのレグ識別子 (`legId`)。
  - `<date>`: レート確定（Reset / Fixing）日。
  - `<resetValue>`: 確定した為替レート（FX Fixing Rate）。
  - `<calculationDetails>` (`ResetCalculationDetails` 型, [L62-L78](../../confirmation/fpml-business-events-5-12.xsd#L62-L78)):
    - `<observation>` / `<observationReference>`: 適用された FX 観測値（レートソース: Bloomberg, Refinitiv 等や観測日時）への参照。
    - `<calculationElements>` (`ResetCalculationElements` 型, [L79-L97](../../confirmation/fpml-business-events-5-12.xsd#L79-L97)): 
      - `<notional>`: リセット後に新たに調整・計算された**新想定元本（Notional Amount）**とその通貨。
      - `<calculatedRate>`: 確定レートや適用されたスプレッド・丸め処理。
      - `<calculationPeriod>`: 対象となる計算期間（Start/End Date, Day Count Fraction 等）。

### 5.2 FpML 5.12 XML 表現例 (`executionAdvice` 内の `<reset>`)
実務プロセスにおける通知メッセージ（`executionAdvice` 等）内での典型的な `<reset>` イベント構造スニペット（参照サンプル: [`confirmation/business-processes/reset/reset_ex01.xml`](../../confirmation/business-processes/reset/reset_ex01.xml#L18-L91)）：

```xml
<executionAdvice xmlns="http://www.fpml.org/FpML-5/confirmation" fpmlVersion="5-12">
  <header>
    <messageId messageIdScheme="http://www.isda.org/coding-scheme/isda/message-id">MSG-RESET-20260728-001</messageId>
    <sentBy>PARTYA_LEI</sentBy>
    <sendTo>PARTYB_LEI</sendTo>
    <creationTimestamp>2026-07-28T10:00:00Z</creationTimestamp>
  </header>
  <isCorrection>false</isCorrection>

  <!-- 観測値 (FX Rate Observation) -->
  <observation>
    <eventIdentifier>
      <partyReference href="party1"/>
      <eventId>obs-fx-001</eventId>
    </eventIdentifier>
    <date>2026-07-28</date>
    <observedValue>155.25</observedValue>
    <source>
      <informationSource>
        <rateSource>WM/Reuters</rateSource>
        <rateSourcePage>USDJPYFIX</rateSourcePage>
      </informationSource>
    </source>
  </observation>

  <!-- 元本リセット (Reset Event) -->
  <reset>
    <eventIdentifier>
      <partyReference href="party1"/>
      <eventId>reset-mtm-001</eventId>
    </eventIdentifier>
    <tradeReference>
      <partyTradeIdentifier>
        <partyReference href="party1"/>
        <tradeId tradeIdScheme="http://www.bank.com/trade-id">MTM-SWAP-9981</tradeId>
      </partyTradeIdentifier>
    </tradeReference>
    <legIdentifier>
      <legId legIdScheme="http://www.bank.com/leg-id">USD-MTM-LEG</legId>
    </legIdentifier>
    <date>2026-07-28</date>
    <resetValue>155.25</resetValue>
    <calculationDetails>
      <observation>
        <observationReference>
          <eventIdentifier>
            <partyReference href="party1"/>
            <eventId>obs-fx-001</eventId>
          </eventIdentifier>
        </observationReference>
      </observation>
      <calculationElements>
        <!-- レート確定に伴いリセットされた新想定元本 -->
        <notional>
          <currency>JPY</currency>
          <amount>15525000000</amount>
        </notional>
        <calculationPeriod>
          <adjustedStartDate>2026-07-28</adjustedStartDate>
          <adjustedEndDate>2026-10-28</adjustedEndDate>
        </calculationPeriod>
      </calculationElements>
    </calculationDetails>
  </reset>
</executionAdvice>
```

### 5.3 実務処理（ライフサイクル通知 vs 約定更新コンファーメーション）
1. **ライフサイクル事績通知 (`ResetNotice` / `executionAdvice`)**:
   - 期中定期の Fixing 通知では、`<reset>` (`ResetEvent`) を用いた通知が標準的です。
2. **取引全般の再確認・約定更新 (`TradeAmendmentContent` / `<amendment>`)**:
   - リセットされた想定元本を取引契約全般の現行ステート（Trade State）として反映し、コンファーメーションを再発行する場合は、`<amendment>` ([`fpml-business-events-5-12.xsd` L1496](../../confirmation/fpml-business-events-5-12.xsd#L1496)) を用いて更新後の `notional` および `principalExchange` を含む新しい `<trade>` を伝達するモデルも採用されます。

### 5.4 現行の約定状態（Trade State）としての `<cashflows>` 表現モデル

過去の事績通知（`<reset>`）に対し、確定した為替レート（FX Spot Rate）やそれに伴う新想定元本・各計算期間の支払額を**取引の現行契約状態（Trade State）**として表現する場合は、`swapStream` 内の **`<cashflows>`（`Cashflows` complexType, [`confirmation/fpml-ird-5-12.xsd` L353-L374](../../confirmation/fpml-ird-5-12.xsd#L353-L374)）** 要素を使用します。

#### `<cashflows>` 内での主な構成要素
- **`paymentCalculationPeriod` / `calculationPeriod`** ([`fpml-ird-5-12.xsd` L100-L163](../../confirmation/fpml-ird-5-12.xsd#L100-L163)):
  - `fxLinkedNotionalAmount`: 確定レート適用後の新想定元本、および Fixing 日 (`adjustedFxSpotFixingDate`)。
  - `notionalAmount`: リセット後に適用される当該計算期間の確定想定元本額（参照サンプル: [`confirmation/products/interest-rate-derivatives/ird-ex26-fxnotional-swap-with-cfs.xml` L101](../../confirmation/products/interest-rate-derivatives/ird-ex26-fxnotional-swap-with-cfs.xml#L101)）。
  - `floatingRateDefinition`: 確定 Fixing 日 (`adjustedFixingDate`)、観測レート (`observedRate`)、および確定金利 (`calculatedRate`)。
  - `forecastAmount`: 確定レートに基づき算出された該当期間の支払見込金額。
- **`principalExchange`** ([`fpml-ird-5-12.xsd` L363](../../confirmation/fpml-ird-5-12.xsd#L363)):
  - 期中リセットに伴い発生する**中間元本交換（Intermediate Principal Exchange）**の発生日と確定金額。

#### XML 表現例 (`swapStream/cashflows`)
確定結果を `swapStream/cashflows` 内に埋め込んだ表現例（参照サンプル: [`ird-ex26-fxnotional-swap-with-cfs.xml` L312-L377](../../confirmation/products/interest-rate-derivatives/ird-ex26-fxnotional-swap-with-cfs.xml#L312-L377)）：

```xml
<swapStream id="JPY-MTM-LEG">
  <payerPartyReference href="partyB"/>
  <receiverPartyReference href="partyA"/>
  <!-- 元本交換スケジュール（中間元本交換含む） -->
  <principalExchanges>
    <initialExchange>true</initialExchange>
    <finalExchange>true</finalExchange>
    <intermediateExchange>true</intermediateExchange>
  </principalExchanges>

  <!-- 期中 Fixing / 確定キャッシュフロー状態表現 -->
  <cashflows>
    <cashflowsMatchParameters>true</cashflowsMatchParameters>
    <paymentCalculationPeriod>
      <adjustedPaymentDate>2026-10-28</adjustedPaymentDate>
      <calculationPeriod>
        <adjustedStartDate>2026-07-28</adjustedStartDate>
        <adjustedEndDate>2026-10-28</adjustedEndDate>
        <fxLinkedNotionalAmount>
          <adjustedFxSpotFixingDate>2026-07-28</adjustedFxSpotFixingDate>
          <notionalAmount>15525000000</notionalAmount>
        </fxLinkedNotionalAmount>
        <floatingRateDefinition>
          <calculatedRate>0.0025</calculatedRate>
          <rateObservation>
            <adjustedFixingDate>2026-07-28</adjustedFixingDate>
            <observedRate>0.0025</observedRate>
          </rateObservation>
        </floatingRateDefinition>
        <forecastAmount>
          <currency>JPY</currency>
          <amount>9814583</amount>
        </forecastAmount>
      </calculationPeriod>
    </paymentCalculationPeriod>
  </cashflows>
</swapStream>
```

---

## 6. 関連 Wiki ページ
- [Interest Rate Derivatives (IRD)](./ird.md)
- [Business Processes (ライフサイクル・イベント)](../processes/business-processes.md)
- [Front-Office Pricing & Confirmation Business Process Flow](../processes/pricing-and-confirmation-flow.md)
- [Front-Office Pricing & Confirmation Bounded Contexts](../architecture/pricing-bounded-contexts.md)
