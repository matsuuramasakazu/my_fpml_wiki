---
tags: [process, reset-event, fixing, nds, cashflows]
schemas: [fpml-business-events-5-12.xsd, fpml-confirmation-processes-5-12.xsd, fpml-ird-5-12.xsd, fpml-doc-5-12.xsd]
updated: 2026-08-14
---

# Reset Event & NDS Fixing Knowledge

## 概要
Non-Deliverable Swap (NDS) や金利スワップ等の店頭デリバティブ取引において、決定された為替レートや参照金利（Fixing）のデータ展開・通知を行うにあたり、FpML 5.12 では `fpml-business-events-5-12.xsd` の `ResetEvent` (要素名 `<reset>`) を使用する。

本ドキュメントでは、`ResetEvent` を包含する最上位ルートエレメント（Root Element）の選択肢および構造上の評価をまとめる。

---

## ResetEvent の構造
- **定義 XSD**: [`fpml-business-events-5-12.xsd`](../../confirmation/fpml-business-events-5-12.xsd#L939) (`complexType ResetEvent`)
- **要素名**: `<reset>` ([`fpml-business-events-5-12.xsd:L1511`](../../confirmation/fpml-business-events-5-12.xsd#L1511))
- **所属グループ**: `PostTradeEventsBase.model` ([Line 1491](../../confirmation/fpml-business-events-5-12.xsd#L1491))
- **主要構成要素**:
  - `tradeReference` (対象取引識別子)
  - `legIdentifier` (対象レグ識別子、任意)
  - `date` (Fixing日/リセット日)
  - `resetValue` (確定値/Fixingレート)
  - `calculationDetails` (レート算出詳細・観測値 `observationReference` リンク等)

---

## ルートエレメント（Root Element）の選択肢と評価

### 1. `<executionAdvice>` (推奨 / ISDA FpML 標準)
- **定義 XSD**: [`fpml-confirmation-processes-5-12.xsd:L305`](../../confirmation/fpml-confirmation-processes-5-12.xsd#L305) / [Line 799](../../confirmation/fpml-confirmation-processes-5-12.xsd#L799)
- **公式サンプル実績**:
  - [`reset_ex01.xml`](../../confirmation/business-processes/reset/reset_ex01.xml#L10)
  - [`reset_ex02_reset_with_observations.xml`](../../confirmation/business-processes/reset/reset_ex02_reset_with_observations.xml#L10)
- **評価**:
  - **メリット**: ポストトレードライフサイクルイベント（Reset, Novation, Amendment等）を対外システムやカウンターパーティに通知・伝達する ISDA 公式の標準ルートメッセージ構造。複数回の Fixing 履歴（`<reset>` の配列）を包括可能。
  - **デメリット**: メッセージングヘッダー (`<header>`) を必須とするため、メッセージ送信のコンテキストが必要。

### 2. `<responseData>` / `<eventNotification>` (Confirmation ワークフロー)
- **定義 XSD**: [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) / [`fpml-msg-5-12.xsd`](../../confirmation/fpml-msg-5-12.xsd)
- **評価**:
  - **メリット**: 取引照合・マッチングサービスに対する応答や非同期イベント通知ワークフローに適合。
  - **デメリット**: リクエスト・レスポンス等のステートフルな対話メッセージ構造を前提とするため、単なる静的データ連携にはオーバーヘッドが大きい。

### 3. `<tradeChangeAdvice>` (取引内容変更通知)
- **定義 XSD**: [`fpml-confirmation-processes-5-12.xsd:L699`](../../confirmation/fpml-confirmation-processes-5-12.xsd#L699)
- **評価**:
  - **メリット**: Fixing 確定に伴って契約自体（`Trade`）を変更・再定義する場合に適用可能。
  - **デメリット**: `TradeChangeContent` ([`fpml-business-events-5-12.xsd:L1019`](../../confirmation/fpml-business-events-5-12.xsd#L1019)) による取引差し替えを目的とするため、定常的な Fixing/Reset 通知としては過剰。

### 4. `<dataDocument>` (【不適合】XSD 違反)
- **定義 XSD**: [`fpml-doc-5-12.xsd:L326`](../../confirmation/fpml-doc-5-12.xsd#L326)
- **評価**:
  - **注意**: 静的文書コンテナである `<dataDocument>` の直下に `<reset>` や `<event>` を直接置くことは、XSD 仕様上不可能（`<trade>` または `<portfolio>` のみが許可されている）。

---

## 代替アプローチ（取引定義 `<trade>` 内部でのキャッシュフロー展開保持）

### 1. XSD スキーマによる正当性検証結果
`ResetEvent` などの独立したイベントメッセージではなく、取引契約定義 (`<trade>`) 内部で過去〜現在の確定済み為替 Fixing レートや金利 Fixing レートを展開保持する設計は、**XSD スキーマ上完全に完全な文脈として標準規定された正当（Valid）な表現手法**です。

- **定義 XSD**: [`fpml-ird-5-12.xsd`](../../confirmation/fpml-ird-5-12.xsd)
- **スキーマ階層**:
  `trade` / `swap` / `swapStream` / `cashflows` ([Line 353](../../confirmation/fpml-ird-5-12.xsd#L353))
  └── `paymentCalculationPeriod` ([Line 1348](../../confirmation/fpml-ird-5-12.xsd#L1348))
      └── `calculationPeriod` ([Line 100](../../confirmation/fpml-ird-5-12.xsd#L100))
          ├── `fxLinkedNotionalAmount` ([Line 896](../../confirmation/fpml-ird-5-12.xsd#L896))
          │   ├── `resetDate` (リセット日)
          │   ├── `adjustedFxSpotFixingDate` (調整済 FX Fixing 日)
          │   ├── `observedFxSpotRate` (決定済 FX Fixing レート)
          │   └── `notionalAmount` (Fixing 適用後の換算想定元本額)
          └── `floatingRateDefinition` ([Line 760](../../confirmation/fpml-ird-5-12.xsd#L760))
              ├── `calculatedRate` (最終算定適用レート)
              └── `rateObservation` (`adjustedFixingDate`, `observedRate` 等)

### 2. XML スニペット例 (`<swapStream>` 配下)
```xml
<swapStream>
  <!-- レグの基本定義・計算期間設定略 -->
  <cashflows>
    <cashflowsMatchParameters>true</cashflowsMatchParameters>
    <paymentCalculationPeriod>
      <adjustedPaymentDate>2026-07-15</adjustedPaymentDate>
      <calculationPeriod>
        <adjustedStartDate>2026-01-15</adjustedStartDate>
        <adjustedEndDate>2026-07-15</adjustedEndDate>
        <!-- 確定済み為替 Fixing (NDS / FX Notional Reset) 情報 -->
        <fxLinkedNotionalAmount>
          <resetDate>2026-07-13</resetDate>
          <adjustedFxSpotFixingDate>2026-07-13</adjustedFxSpotFixingDate>
          <observedFxSpotRate>1350.50</observedFxSpotRate> <!-- 決定為替レート -->
          <notionalAmount>10000000.00</notionalAmount>
        </fxLinkedNotionalAmount>
        <!-- 確定済み参照金利 (Floating Rate Reset) 情報 -->
        <floatingRateDefinition>
          <calculatedRate>0.0085</calculatedRate>
          <rateObservation>
            <adjustedFixingDate>2026-01-13</adjustedFixingDate>
            <observedRate>0.0085</observedRate>
          </rateObservation>
        </floatingRateDefinition>
      </calculationPeriod>
    </paymentCalculationPeriod>
  </cashflows>
</swapStream>
```

### 3. メリット・デメリット比較
- **メリット**:
  - 静的ドキュメントである `<dataDocument>` の直下に配置可能。
  - 取引の現在状態（Current State）と確定済みキャッシュフローを 1 つの `<trade>` 内で完結して表現可能。
- **デメリット**:
  - イベント単位の監査トレース（「誰がいつどのレートを決定・入力したか」等の差分通知）としては機能しづらい（差分通知には `<executionAdvice>` + `<reset>` を利用する）。
