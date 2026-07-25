---
title: Non-Deliverable Swap (NDS) の期中 Fixing 済みキャッシュフロー表現とイベントモデル
tags: [fpml, ird, nds, non-deliverable, fixing, cashflows, business-events, trade-change-advice]
schemas: [fpml-ird-5-12.xsd, fpml-business-events-5-12.xsd, fpml-confirmation-processes-5-12.xsd, fpml-doc-5-12.xsd]
updated: 2026-07-25
---

# Non-Deliverable Swap (NDS) の期中 Fixing 済みキャッシュフロー表現とイベントモデル

## 1. 概要と問題意識

Non-Deliverable Swap (NDS) や Non-Deliverable Forward (NDF) などの非決済デリバティブ取引において、期中の Fixing 日を迎えて為替レート（FX Fixing Rate）が確定したものの、実際の決済日（Payment Date）には未到達である「期中 Fixing 済み・支払い未済（Fixed / Unsettled）」状態の取引を表現・管理することが実務上重要となります。

本ドキュメントでは、FpML 5.12 Confirmation View の XSD スキーマ仕様に基づき、NDS の非決済通貨（Reference Currency）から決済通貨（Settlement Currency）への通貨換算における `fixingDate` および `fixingFxRate` の表現方法、並びに時価値洗い（Valuation / MTM）やシステム間連携における 4 つの表現アプローチを解説します。

---

## 2. スキーマ構造分析と標準仕様の限界

### (1) 約定・パラメトリック定義 (`settlementProvision`)
NDS の契約定義（約定時点のパラメトリック表現）では、[`confirmation/fpml-ird-5-12.xsd`](../../confirmation/fpml-ird-5-12.xsd#L1190-L1223) の `SettlementProvision` および `NonDeliverableSettlement` を用いて、決済通貨、非決済基準通貨、Fixing日計算ルール（`fxFixingDate`）、参照ソース（`settlementRateOption`）を定義します。

サンプルコード参照: [`confirmation/products/interest-rate-derivatives/ird-ex31-non-deliverable-settlement-swap.xml`](../../confirmation/products/interest-rate-derivatives/ird-ex31-non-deliverable-settlement-swap.xml#L111-L144)

```xml
<settlementProvision>
  <settlementCurrency>USD</settlementCurrency>
  <nonDeliverableSettlement>
    <referenceCurrency>KRW</referenceCurrency>
    <fxFixingDate>
      <periodMultiplier>2</periodMultiplier>
      <period>D</period>
      <dayType>Business</dayType>
      <businessDayConvention>MODFOLLOWING</businessDayConvention>
      <dateRelativeToPaymentDates>
        <paymentDatesReference href="PaymentDatesID" />
      </dateRelativeToPaymentDates>
    </fxFixingDate>
    <settlementRateOption>KRW.KFTC18/KRW02</settlementRateOption>
  </nonDeliverableSettlement>
</settlementProvision>
```

### (2) キャッシュフロー展開構造 (`cashflows/paymentCalculationPeriod`) の限界
[`confirmation/fpml-ird-5-12.xsd`](../../confirmation/fpml-ird-5-12.xsd#L1348-L1393) に定義されている `PaymentCalculationPeriod` 配下には、金利インデックスの Fixing 情報（`floatingRateDefinition/rateObservation`）を保持する要素はあるものの、**非決済通貨から決済通貨への換算用 FX レート（`fixingFxRate`）および Fixing日（`fixingDate`）を直接格納する標準フィールドは存在しません**。

---

## 3. 期中 Fixing 済みの表現における 4 つのアプローチ

### アプローチ 1: Trade レベルでの最終確定額反映 (`forecastPaymentAmount`)
* **レイヤー**: Trade (Confirmation View) レベル
* **概要**: Fixing 確定後、非決済通貨で計算された利息額に確定 FX レートを乗じた最終決済額（USD 等の Settlement Currency）を [`PaymentCalculationPeriod`](../../confirmation/fpml-ird-5-12.xsd#L1376) の `forecastPaymentAmount` にセットします。
* **適用領域**: ポジション管理 DB やバリュエーションエンジン（時価値洗い）。計算処理のオーバーヘッドが最小。

```xml
<paymentCalculationPeriod>
  <adjustedPaymentDate>2026-08-15</adjustedPaymentDate>
  <calculationPeriod>
    <unadjustedStartDate>2026-05-15</unadjustedStartDate>
    <unadjustedEndDate>2026-08-15</unadjustedEndDate>
    <notionalAmount>26415000000.00</notionalAmount> <!-- KRW -->
    <floatingRateDefinition>
      <calculatedRate>0.02730</calculatedRate>
    </floatingRateDefinition>
  </calculationPeriod>
  <!-- 確定 FX レートで換算済みの最終支払い額 (USD) -->
  <forecastPaymentAmount>
    <currency>USD</currency>
    <amount>195650.25</amount>
  </forecastPaymentAmount>
</paymentCalculationPeriod>
```

### アプローチ 2: Trade レベルでのベンダー/カスタム拡張 (`ext:fxFixing`)
* **レイヤー**: Trade (Confirmation View) 拡張
* **概要**: `paymentCalculationPeriod` に独自拡張要素（`<ext:fxFixing>`）を追加し、`fixingDate` と `fixingFxRate` を同一要素内で直接保持します。
* **適用領域**: Trade XML 単体で全情報を完結させたいアセット管理システム。

### アプローチ 3: Business Events (`observation` / `reset`) によるイベントモデル表現
* **レイヤー**: Business Event レベル (100% FpML 標準)
* **概要**: [`confirmation/fpml-business-events-5-12.xsd`](../../confirmation/fpml-business-events-5-12.xsd) の `observation`（観測日 `date`、レート `observedValue`、情報ソース `source`）および `reset`（`tradeReference`, `legIdentifier`, `calculationDetails`）構造を使用。
* **適用領域**: 期中 Fixing 発生時のシステム間イベント通知、ミドル/バックオフィス間インターフェース。

サンプルコード参照: [`confirmation/business-processes/reset/reset_ex02_reset_with_observations.xml`](../../confirmation/business-processes/reset/reset_ex02_reset_with_observations.xml#L18-L183)

```xml
<executionAdvice xmlns="http://www.fpml.org/FpML-5/confirmation" fpmlVersion="5-12">
  <!-- 1. FX Fixing レートの観測イベント (Observation) -->
  <observation>
    <eventIdentifier>
      <partyReference href="party1" />
      <eventId eventIdScheme="http://www.bank.com/obs-id">OBS-KRW-20260813</eventId>
    </eventIdentifier>
    <date>2026-08-13</date>
    <observedValue>1350.12</observedValue>
    <source>
      <informationSource><rateSource>KFTC18</rateSource></informationSource>
      <underlyer>
        <quotedCurrencyPair>
          <currency1>USD</currency1>
          <currency2>KRW</currency2>
          <quoteBasis>Currency2PerCurrency1</quoteBasis>
        </quotedCurrencyPair>
      </underlyer>
    </source>
  </observation>

  <!-- 2. NDS 取引への Fixing 適用イベント (Reset) -->
  <reset>
    <eventIdentifier>
      <partyReference href="party1" />
      <eventId eventIdScheme="http://www.bank.com/reset-id">RST-NDS-20260813-01</eventId>
    </eventIdentifier>
    <tradeReference>
      <partyTradeIdentifier>
        <partyReference href="party1" />
        <tradeId tradeIdScheme="http://www.bank.com/trade-id">NDS-TRADE-9988</tradeId>
      </partyTradeIdentifier>
    </tradeReference>
    <legIdentifier>
      <legId legIdScheme="http://www.bank.com/leg-id">KRW-Leg-01</legId>
    </legIdentifier>
    <date>2026-08-13</date>
    <resetValue>1350.12</resetValue>
  </reset>
</executionAdvice>
```

### アプローチ 4: `tradeChangeAdvice` (TradeChangeContent) による新旧 Trade とイベントのパッケージ化
* **レイヤー**: Event ＋ Trade レベル
* **概要**: [`confirmation/fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd#L699) の `TradeChangeAdvice` および [`confirmation/fpml-business-events-5-12.xsd`](../../confirmation/fpml-business-events-5-12.xsd#L1019) の `TradeChangeContent` を使用。
* **バインドの仕組み**:
  1. **直接的内包（Structure Containment）**: `TradeChangeContent` (Line 1019) コンテナ内に `<oldTrade>` / `<oldTradeIdentifier>` と Fixing 確定後の新 `<trade>`（および変更事由 `changeEvent`）が直接記述されるため、要素レベルで完全かつ曖昧さなくバインドされます。
  2. **`versionedTradeId`**: [`confirmation/fpml-doc-5-12.xsd`](../../confirmation/fpml-doc-5-12.xsd#L1451) の `tradeHeader` 内の `partyTradeIdentifier/versionedTradeId` (`tradeId` + `version`) により、Fixing 前（Version 1）から Fixing 後（Version 2）への状態遷移が追跡されます。
* **適用領域**: 監査証跡（Audit Trail）や変更履歴（Lifecycle Lineage）の保持が厳格に求められる時価値洗い・ポジション更新処理。

サンプルコード参照: [`confirmation/business-processes/trade-change-advice/msg-ex61-execution-advice-trade-change-F03-00.xml`](../../confirmation/business-processes/trade-change-advice/msg-ex61-execution-advice-trade-change-F03-00.xml#L11-L55)

---

## 4. 比較・決定マトリクス

| アプローチ | コンテクスト | FpML適合度 | `fixingDate` / `fixingFxRate` 表現性 | 主な用途 |
| :--- | :--- | :---: | :--- | :--- |
| **1. `forecastPaymentAmount` 反映** | Trade State | 高 (100%) | 最終確定額 (USD) のみ保持 | MTM/Valuation エンジン、最軽量ポジション管理 |
| **2. ベンダー拡張 (`ext:fxFixing`)** | Trade State (Ext) | 低〜中 | 拡張タグ内に直接記録 | Trade 単体で全情報を完結させたいシステム |
| **3. `business-events` (`reset`/`obs`)** | Business Event | **高 (100%)** | **`observation` 内で完全構造化** | **Fixing 発生時のシステム間通知、EAI 連係** |
| **4. `tradeChangeAdvice`** | Event + Trade | **高 (100%)** | **`TradeChangeContent` 内包＋`versionedTradeId`** | **監査証跡・変更履歴が必要な状態遷移通知** |

---

## 5. 関連 Wiki ページ

- [Interest Rate Derivatives (IRD)](./ird.md)
- [Foreign Exchange (FX)](./fx.md)
- [Business Processes](../processes/business-processes.md)
- [Front-Office Pricing & Confirmation Process Flow](../processes/pricing-and-confirmation-flow.md)
