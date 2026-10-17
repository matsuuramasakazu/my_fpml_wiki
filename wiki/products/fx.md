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

### アジアン・オプション（Asian Option: 平均型オプション）とアベレージ・ストライク

東京の OTC 為替デリバティブ市場において、一定期間のスポット相場を平均化して権利行使判定または受渡金額決定を行う**アジアン・オプション（平均型オプション）**は、事業法人の期間損益平滑化や実需ヘッジ目的で広く利用されています。

アジアン・オプションには大きく分けて以下の2つの類型が存在します。

| 類型 | 和名 / 実務呼称 | ペイオフ（Call の例） | ストライク $K$ | 満期参照スポット $S$ | FpML 推奨表現 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Average Rate Option (ARO)** | 平均レート・オプション / 平均相場オプション | $\max(S_{avg} - K, 0)$ | 固定値（約定時に確定） | 期間中の算術平均レート $S_{avg}$ | `<fxOption>` 配下 `<features><asian>` または `<fxAccrualOption>` 配下 `<averageRate>` |
| **Average Strike Option (ASO)** | 平均行使価格オプション / アベレージ・ストライク・オプション | $\max(S_T - K_{avg}, 0)$ | 期間中の算術平均レート $K_{avg}$ | 満期日のスポットレート $S_T$ | **`<fxAccrualOption>` 配下 `<averageStrike>`** |

#### 1. FpML におけるアベレージ・ストライク・オプションのモデリング

##### (A) ネイティブ表現: `<fxAccrualOption>` による `<averageStrike>`
FpML 5.12 Confirmation View において、アベレージ・ストライク・オプション（ASO）を直接的かつネイティブに表現するための標準構造は **`<fxAccrualOption>`**（型: `FxAccrualOption`、[`confirmation/fpml-fx-accruals-5-12.xsd`](../../confirmation/fpml-fx-accruals-5-12.xsd)）です。

スキーマ定義上、`<fxAccrualOption>` では固定行使価格（`strike`）と平均行使価格（`averageStrike`）が `<xsd:choice>` で排他選択となっています：

```xml
<!-- confirmation/fpml-fx-accruals-5-12.xsd より抜粋 -->
<xsd:choice>
    <xsd:sequence>
        <xsd:element name="strike" type="FxOptionStrikePrice"/>
        <xsd:element name="counterCurrencyAmount" type="NonNegativeAmountSchedule" minOccurs="0"/>
    </xsd:sequence>
    <xsd:element name="averageStrike" type="FxAverageStrike"/>
</xsd:choice>
<xsd:element name="averageRate" type="FxAverageRate" minOccurs="0"/>
```

`<averageStrike>`（型: `FxAverageStrike`、基底型: `FxAveragingProcess`）には以下の詳細パラメータがモデル化されます：
- `quotedCurrencyPair`: 平均化対象の通貨ペア（例: USD/JPY）
- `informationSource`: レート参照ソース（ロイター `BTMFIX`、15:00 東京等）
- `fixingSchedule`: 観測スケジュール（開始日・終了日、営業日カレンダー、観測回数等）
- `averagingMethod`: 平均化手法（`Arithmetic`（算術平均）、`Harmonic`（調和平均））
- `precision`: レート丸め精度（小数点以下桁数）
- `strikeAdjustment`: スプレッド調整値（算出された平均ストライクに対する加減算幅）

##### (B) 標準 `<fxOption>`（バニラ枠組み）との比較と制約
- `<fxOption>`（[`confirmation/fpml-fx-5-12.xsd`](../../confirmation/fpml-fx-5-12.xsd)）にも `<features><asian>`（型: `FxAsianFeature`）が定義されています。
- しかし、`<fxOption>` では `<strike>`（型: `FxStrikePrice`、必須 `[1..1]`）がスキーマ制約上**固定レートの指定を必須**としています。
- したがって、`<fxOption>` の `<asian>` フィーチャーは実務上 **Average Rate Option (ARO)**（固定ストライクに対して期間平均レートを観測するオプション）向けに特化しており、約定時点でストライクが未定である Average Strike Option (ASO) をネイティブに表現することはできません。

#### 2. サンプル XML の所在と特徴

| サンプルファイル | プロダクト型 | 主な特徴 |
| :--- | :--- | :--- |
| [`confirmation/products/fx-derivatives/fx-ex55-accrual-option-average-strike.xml`](../../confirmation/products/fx-derivatives/fx-ex55-accrual-option-average-strike.xml) | `<fxAccrualOption>` | **アベレージ・ストライク・オプションの公式サンプル**。GBP Call / JPY Put、USD/JPY 東京15時FIXの算術平均（全20回観測）に -0.44 のスプレッド調整を適用。 |
| [`confirmation/products/fx-derivatives/fx-ex56-accrual-option-average-rate.xml`](../../confirmation/products/fx-derivatives/fx-ex56-accrual-option-average-rate.xml) | `<fxAccrualOption>` | アクルーアル型の平均レート・オプション（固定ストライク + `<averageRate>`）。 |
| [`confirmation/products/fx-derivatives/fx-ex20-avg-rate-option-parametric.xml`](../../confirmation/products/fx-derivatives/fx-ex20-avg-rate-option-parametric.xml) | `<fxOption>` | バニラ枠組みでの平均レート・オプション。パラメトリック（頻度指定）な観測スケジュール。 |
| [`confirmation/products/fx-derivatives/fx-ex21-avg-rate-option-parametric-plus-rate-observation.xml`](../../confirmation/products/fx-derivatives/fx-ex21-avg-rate-option-parametric-plus-rate-observation.xml) | `<fxOption>` | バニラ枠組みでの平均レート・オプション。パラメトリック頻度＋確定済レート観測値の併用。 |
| [`confirmation/products/fx-derivatives/fx-ex22-avg-rate-option-specific.xml`](../../confirmation/products/fx-derivatives/fx-ex22-avg-rate-option-specific.xml) | `<fxOption>` | バニラ枠組みでの平均レート・オプション。個別の日付リストを直接列挙した観測スケジュール。 |

```xml
<!-- fx-ex55-accrual-option-average-strike.xml より抜粋: averageStrike 構造 -->
<averageStrike id="averageStrike">
    <quotedCurrencyPair>
        <currency1>USD</currency1>
        <currency2>JPY</currency2>
        <quoteBasis>Currency2PerCurrency1</quoteBasis>
    </quotedCurrencyPair>
    <informationSource>
        <rateSource>Reuters</rateSource>
        <rateSourcePage>BTMFIX</rateSourcePage>
        <fixingTime>
            <hourMinuteTime>15:00:00</hourMinuteTime>
            <businessCenter>JPTO</businessCenter>
        </fixingTime>
    </informationSource>
    <fixingSchedule>
        <startDate>2005-10-03</startDate>
        <endDate>2005-10-31</endDate>
        <dayType>Business</dayType>
        <businessCenters>
            <businessCenter>JPTO</businessCenter>
        </businessCenters>
    </fixingSchedule>
    <averagingMethod>Arithmetic</averagingMethod>
    <precision>4</precision>
    <strikeAdjustment>-0.44</strikeAdjustment>
</averageStrike>
```

---

### バリア・オプション、ウィンドウバリア、およびギャップ・オプション

東京の OTC 為替デリバティブ市場において、顧客のヘッジコスト削減（プレミアム低減）や相場観に応じた変則的なペイオフ設計のために、各種バリアおよびギャップ構造が頻繁に組成されます。

| プロダクト | 構造・ペイオフ概要 | FpML 5.12 での表現可否 | FpML モデリング手法 | サンプル XML |
| :--- | :--- | :--- | :--- | :--- |
| **ウィンドウバリア・オプション**<br>(Window Barrier Option) | バリア判定期間が取引全期間ではなく、特定の観測窓（$[T_{start}, T_{end}]$）に限定されたバリアオプション | **表現可能**<br>(Native Support) | `<fxOption>` 配下 `<features><barrier>`（型: `FxBarrierFeature`）の `<observationStartDate>` / `<observationEndDate>` で観測窓を限定 | 専用サンプルなし<br>（[`fx-ex12-fx-barrier-option.xml`](../../confirmation/products/fx-derivatives/fx-ex12-fx-barrier-option.xml) の期間修正で完全対応） |
| **ギャップ・オプション**<br>(Gap Option) | 判定トリガー（Trigger $K_1$）とペイオフ算出ストライク（Strike $K_2$）が乖離（Gap）し、満期でジャンプを伴うオプション | **表現可能**<br>（ネイティブタグなし） | ① 単一 `<fxOption>`: 満期判定の European Knock-in Barrier（Strike=$K_2$, Trigger=$K_1$）<br>② `<strategy>`: バニラコール/プット ＋ デジタルオプション（Touch/Trigger）のクオンツ合成 | 専用サンプルなし |
| **バリアギャップ・オプション**<br>(Barrier Gap Option) | 期間中バリア（レート $H$）のノックイン/アウト判定と、満期のギャップペイオフ（$K_1, K_2$）の複合構造 | **表現可能**<br>（合成戦略） | `<strategy>` によるマルチレグ構造（バリアオプションレグ ＋ バリア付きデジタルオプションレグ） | 専用サンプルなし |
| **ウィンドウバリアギャップ・オプション**<br>(Window Barrier Gap Option) | バリアギャップオプションのバリア判定期間が特定ウィンドウ $[T_{start}, T_{end}]$ に限定された構造 | **表現可能**<br>（合成戦略） | 上記 `<strategy>` の各レグのバリア観測期間を `<observationStartDate>` / `<observationEndDate>` で特定期間に限定 | 専用サンプルなし |

#### 1. ウィンドウバリア・オプションのモデリング

FpML 5.12 Confirmation View では、[`confirmation/fpml-fx-5-12.xsd`](../../confirmation/fpml-fx-5-12.xsd) の `FxBarrierFeature`（L254-L318）において、アメリカンバリアの観測開始・終了日時が厳密に定義されています。

- `<observationStartDate>` (L287) / `<observationStartTime>` (L292): 観測開始日・時刻。省略時は約定日時（Transaction Date/Time）とみなされます。
- `<observationEndDate>` (L299) / `<observationEndTime>` (L304): 観測終了日・時刻。省略時は満期日時（Expiration Date/Time）とみなされます。
- `<observationPoint>` (L311): 離散的観測点（Discrete Observation Schedule）を定義する場合の要素リスト。

約定日（`tradeDate`）より遅い `observationStartDate`、または満期日（`expiryDate`）より早い `observationEndDate` を指定することで、ウィンドウバリアが成立します。

```xml
<!-- ウィンドウバリア・オプション（EUR/USD Up-and-In Window Barrier）の定義例 -->
<fxOption>
    <buyerPartyReference href="party2"/>
    <sellerPartyReference href="party1"/>
    <europeanExercise>
        <expiryDate>2026-12-15</expiryDate>
        <expiryTime>
            <hourMinuteTime>15:00:00</hourMinuteTime>
            <businessCenter>JPTO</businessCenter>
        </expiryTime>
        <valueDate>2026-12-17</valueDate>
    </europeanExercise>
    <putCurrencyAmount>
        <currency>USD</currency>
        <amount>10000000</amount>
    </putCurrencyAmount>
    <callCurrencyAmount>
        <currency>EUR</currency>
        <amount>9090909</amount>
    </callCurrencyAmount>
    <strike>
        <rate>1.1000</rate>
        <strikeQuoteBasis>PutCurrencyPerCallCurrency</strikeQuoteBasis>
    </strike>
    <features>
        <barrier>
            <barrierType>Knockin</barrierType>
            <direction>Up</direction>
            <quotedCurrencyPair>
                <currency1>EUR</currency1>
                <currency2>USD</currency2>
                <quoteBasis>Currency2PerCurrency1</quoteBasis>
            </quotedCurrencyPair>
            <triggerRate>1.1500</triggerRate>
            <informationSource>
                <rateSource>Reuters</rateSource>
                <rateSourcePage>EUR=</rateSourcePage>
            </informationSource>
            <!-- 観測窓（Window）: 満期前の特定3か月間のみバリア判定を有効化 -->
            <observationStartDate>2026-09-15</observationStartDate>
            <observationEndDate>2026-12-15</observationEndDate>
            <observationEndTime>
                <hourMinuteTime>15:00:00</hourMinuteTime>
                <businessCenter>JPTO</businessCenter>
            </observationEndTime>
        </barrier>
    </features>
</fxOption>
```

#### 2. ギャップ・オプションのクオンツ分解と FpML 実装

ギャップコールオプションの満期ペイオフは、原資産レート $S_T$、判定トリガー $K_1$、権利行使価格 $K_2$（$K_1 > K_2$）に対して次式で与えられます：

$$\text{Payoff} = (S_T - K_2) \mathbf{1}_{\{S_T > K_1\}} = \max(S_T - K_1, 0) + (K_1 - K_2) \mathbf{1}_{\{S_T > K_1\}}$$

FpML では `<gapOption>` という単一タグは存在しませんが、以下の2つの実務手法で表現されます：

1. **満期判定ヨーロピアン・ノックイン（単一 `<fxOption>`）**:
   - `<strike>` に $K_2$ を指定し、`<barrier>` の `<triggerRate>` に $K_1$ を設定した上で、観測日を満期日（`observationStartDate` = `observationEndDate` = `expiryDate`）に限定します。
   - $S_T > K_1$ の場合のみノックインしてストライク $K_2$ のコール（$S_T - K_2 > 0$）が有効化するため、厳密に同一のペイオフを単一プロダクトで実現できます。
2. **マルチレグ合成（`<strategy>`）**:
   - レグ1: バニラコール `<fxOption>`（Strike = $K_1$）
   - レグ2: デジタルコール `<fxDigitalOption>`（Trigger = $K_1$, Payout = $K_1 - K_2$, [`confirmation/fpml-fx-5-12.xsd:361`](../../confirmation/fpml-fx-5-12.xsd)）
   - フロントのプライシングモデルや Greeks 分解、リスク管理システムの都合上、多くの本邦大手行・外銀東京支店ではこの合成表現が採用されます。

---

### FX デジタル・オプション (`fxDigitalOption`) と受渡ペイアウト (`payout`)

東京の OTC 為替デリバティブ市場において、所定のトリガーレート到達（または満期時のレート水準）に応じて、固定金額（キャッシュ）の受渡しが発生する**デジタル・オプション（バイナリー・オプション、ワンタッチ、ノータッチ等）**は、為替ストラクチャード商品や実需企業のヘッジ・コスト削減手法として広く利用されています。

FpML 5.12 Confirmation View では、独立したプロダクト **`<fxDigitalOption>`**（型: `FxDigitalOption`、[`confirmation/fpml-fx-5-12.xsd:361`](../../confirmation/fpml-fx-5-12.xsd)）としてネイティブにモデル化されており、権利行使／トリガー条件充足時に受け渡される確定金額ペイアウトを **`<payout>` 要素（型: `FxOptionPayout`）** として明示的に定義します。

#### 1. `<payout>` 要素（`FxOptionPayout`）のスキーマ構造

スキーマ定義箇所: [`confirmation/fpml-fx-5-12.xsd:414`](../../confirmation/fpml-fx-5-12.xsd), [`L863-L883`](../../confirmation/fpml-fx-5-12.xsd)  
基底型: `NonNegativeMoney`（[`confirmation/fpml-shared-5-12.xsd:2484`](../../confirmation/fpml-shared-5-12.xsd)）← `MoneyBase`（[`confirmation/fpml-shared-5-12.xsd:2421`](../../confirmation/fpml-shared-5-12.xsd)）

```xml
<!-- FpML 5.12 confirmation/fpml-fx-5-12.xsd より抜粋 -->
<xsd:complexType name="FxOptionPayout">
  <xsd:annotation>
    <xsd:documentation xml:lang="en">A type that contains full details of a predefined fixed payout which may occur (or not) in a Barrier Option or Digital Option when a trigger event occurs (or not).</xsd:documentation>
  </xsd:annotation>
  <xsd:complexContent>
    <xsd:extension base="NonNegativeMoney">
      <xsd:sequence>
        <xsd:element name="payoutStyle" type="PayoutEnum">
          <xsd:annotation>
            <xsd:documentation xml:lang="en">The trigger event and payout may be asynchonous. A payout may become due on the trigger event, or the payout may (by agreeement at initiation) be deferred (for example) to the maturity date.</xsd:documentation>
          </xsd:annotation>
        </xsd:element>
        <xsd:element name="settlementInformation" type="SettlementInformation" minOccurs="0"/>
      </xsd:sequence>
    </xsd:extension>
  </xsd:complexContent>
</xsd:complexType>
```

| 子要素 | 型 | 必須/任意 | 説明・実務的役割 |
| :--- | :--- | :--- | :--- |
| `<currency>` | `Currency` | 必須 [1..1] | ペイアウトの受渡通貨（ISO 4217 コード。例: `USD`, `JPY`, `GBP` 等）。`MoneyBase` より継承。 |
| `<amount>` | `NonNegativeDecimal` | 必須 [1..1] | 権利行使・トリガー充足時に受け渡される確定金額（非負の数値）。`NonNegativeMoney` より継承。 |
| `<payoutStyle>` | `PayoutEnum` | 必須 [1..1] | ペイアウトの支払・受渡タイミング（[`confirmation/fpml-enum-5-12.xsd:3075`](../../confirmation/fpml-enum-5-12.xsd)）。<br>・`Immediate`: トリガー発生日／行使日直後のバリューデートに直ちに受渡。<br>・`Deferred`: アメリカン型等で期中にタッチが発生しても、実際の受渡日は当初満期日（`latestValueDate`）まで据え置く（実務上の Deferred Touch）。 |
| `<settlementInformation>` | `SettlementInformation` | 任意 [0..1] | 受渡資金の決済口座指示（SSI: Standard Settlement Instruction、電信送金指図等）。 |

##### 受払方向（Payer / Receiver）の規定
`<fxDigitalOption>` は抽象型 `Option`（[`confirmation/fpml-option-shared-5-12.xsd:406`](../../confirmation/fpml-option-shared-5-12.xsd)）を継承しているため、ルート直下に `<buyerPartyReference>`（買い手）と `<sellerPartyReference>`（売り手）を保持します。  
ISDA 慣行および FpML アーキテクチャ上、**オプション買い手がプレミアム（`<premium>`）を支払い、行使条件が充足された場合にオプション売り手（Seller）が `<payout>` の金額を買い手（Buyer）へ支払います**。

#### 2. 公式プロダクトサンプル XML（6類型）

ワークスペース内の [`confirmation/products/fx-derivatives/`](../../confirmation/products/fx-derivatives) には、デジタルオプションの各商品類型に対応する **6つの公式サンプル XML** が提供されています。

| サンプル XML ファイル | 商品類型 | 判定方式・行使構造 | ペイアウト設定（通貨・金額・受渡方式） |
| :--- | :--- | :--- | :--- |
| [`fx-ex14-euro-digital-option.xml`](../../confirmation/products/fx-derivatives/fx-ex14-euro-digital-option.xml) | ヨーロピアン・デジタル（バイナリー） | `<europeanExercise>` + `<trigger>` (AtOrAbove 1.4800) | GBP 750,000 / `Immediate` |
| [`fx-ex15-euro-range-digital-option.xml`](../../confirmation/products/fx-derivatives/fx-ex15-euro-range-digital-option.xml) | ヨーロピアン・レンジ・デジタル | `<europeanExercise>` + 2つの `<trigger>` (AtOrAbove 1.4800 & AtOrBelow 1.5500) | GBP 1,250,000 / `Immediate` |
| [`fx-ex16-one-touch-option.xml`](../../confirmation/products/fx-derivatives/fx-ex16-one-touch-option.xml) | アメリカン・ワンタッチ (One-Touch) | `<americanExercise>` + `<touch>` (Touch AtOrAbove 1.5200) | GBP 2,000,000 / `Deferred`（満期日受渡） |
| [`fx-ex17-no-touch-option.xml`](../../confirmation/products/fx-derivatives/fx-ex17-no-touch-option.xml) | アメリカン・ノータッチ (No-Touch) | `<americanExercise>` + `<touch>` (NoTouch AtOrAbove 1.5200) | GBP 3,000,000 / `Immediate` |
| [`fx-ex18-double-one-touch-option.xml`](../../confirmation/products/fx-derivatives/fx-ex18-double-one-touch-option.xml) | ダブル・ワンタッチ (DOT) | `<americanExercise>` + 2つの `<touch>` (Touch 1.5200 または Touch 1.4600) | GBP 2,000,000 / `Immediate` |
| [`fx-ex19-double-no-touch-option.xml`](../../confirmation/products/fx-derivatives/fx-ex19-double-no-touch-option.xml) | ダブル・ノー・タッチ (DNT) | `<americanExercise>` + 2つの `<touch>` (NoTouch 1.5200 かつ NoTouch 1.4600) | GBP 3,000,000 / `Immediate` |

##### XML スニペット例: ヨーロピアン・デジタル・オプション ([`fx-ex14-euro-digital-option.xml`](../../confirmation/products/fx-derivatives/fx-ex14-euro-digital-option.xml))
```xml
<fxDigitalOption>
    <productType productTypeScheme="http://www.sample.com/coding-scheme/product-type-simple">EuroBinary</productType>
    <buyerPartyReference href="party2"/>
    <sellerPartyReference href="party1"/>
    <europeanExercise>
        <expiryDate>2001-11-26</expiryDate>
        <expiryTime>
            <hourMinuteTime>14:00:00</hourMinuteTime>
            <businessCenter>GBLO</businessCenter>
        </expiryTime>
        <cutName>LondonEveningPgm</cutName>
        <valueDate>2001-11-28</valueDate>
    </europeanExercise>
    <trigger>
        <triggerCondition>AtOrAbove</triggerCondition>
        <quotedCurrencyPair>
            <currency1>GBP</currency1>
            <currency2>USD</currency2>
            <quoteBasis>Currency2PerCurrency1</quoteBasis>
        </quotedCurrencyPair>
        <triggerRate>1.4800</triggerRate>
        <spotRate>1.4800</spotRate>
        <informationSource>
            <rateSource>Reuters</rateSource>
            <rateSourcePage>GBP=</rateSourcePage>
        </informationSource>
    </trigger>
    <!-- 行使後に受け渡される確定金額ペイアウト -->
    <payout>
        <currency>GBP</currency>
        <amount>750000</amount>
        <payoutStyle>Immediate</payoutStyle>
    </payout>
    <premium>
        <payerPartyReference href="party2"/>
        <receiverPartyReference href="party1"/>
        <paymentDate>
            <adjustableDate>
                <unadjustedDate>2001-11-14</unadjustedDate>
                <dateAdjustments>
                    <businessDayConvention>NONE</businessDayConvention>
                </dateAdjustments>
            </adjustableDate>
        </paymentDate>
        <paymentAmount>
            <currency>GBP</currency>
            <amount>53000</amount>
        </paymentAmount>
    </premium>
</fxDigitalOption>
```

#### 3. ポストトレード（権利行使・資金決済イベント）での表現

約定時のコンファーメーション（上記 `<fxDigitalOption>`）で取り決めたペイアウト条件に基づき、満期日やタッチ発生時に**実際に権利行使・キャッシュ決済が執行された際のライフサイクル通知**は、ビジネスイベントメッセージ（`executionNotification` / [`confirmation/fpml-business-events-5-12.xsd:754`](../../confirmation/fpml-business-events-5-12.xsd)）における **`<optionExercise>`** を用いて伝送されます。

- **サンプル XML**: [`confirmation/business-processes/option-exercise-expiry/msg-ex03a-execution-notification-option-exercised-1-cash.xml`](../../confirmation/business-processes/option-exercise-expiry/msg-ex03a-execution-notification-option-exercised-1-cash.xml)

```xml
<optionExercise>
    <tradeIdentifier>
        <partyReference href="SKY"/>
        <tradeId tradeIdScheme="http://www.swift.com/coding-scheme/contract-id">IRS2</tradeId>
    </tradeIdentifier>
    <exerciseDate>2010-09-09</exerciseDate>
    <exerciseTime>12:00:00Z</exerciseTime>
    <settlementType>Cash</settlementType>
    <!-- 権利行使に伴い受渡される実際のキャッシュ決済 -->
    <payment>
        <payerPartyReference href="AMAG"/>
        <receiverPartyReference href="SKY"/>
        <paymentDate>
            <adjustableDate>
                <unadjustedDate>2010-09-09</unadjustedDate>
                <dateAdjustments>
                    <businessDayConvention>NONE</businessDayConvention>
                </dateAdjustments>
            </adjustableDate>
        </paymentDate>
        <paymentAmount>
            <currency>USD</currency>
            <amount>100000</amount>
        </paymentAmount>
    </payment>
</optionExercise>
```

このように、FpML では「約定段階での事前取り決めペイアウト（`<fxDigitalOption>/payout`）」と「権利行使実行時の実受渡キャッシュフロー（`<optionExercise>/payment`）」の双方が完全に体系化されています。

#### 4. `<dataDocument>` による行使後ペイアウト単体の表現可否と `<bulletPayment>`

「行使後に発生する単一のペイアウト（キャッシュフロー）を、業務メッセージヘッダーを伴わない静的データコンテナである `<dataDocument>` 形式で表現・連携したい」という実務要件に対する FpML 5.12 のスキーマ仕様およびアーキテクチャは以下の通りです。

##### (1) XSD スキーマ文法上の制約
[`confirmation/fpml-doc-5-12.xsd:326`](../../confirmation/fpml-doc-5-12.xsd) において、`DataDocument` 型のシーケンス定義は以下のようになっています：
- `<onBehalfOf>` [0..1]
- `<originatingEvent>` [0..1]
- `<trade>` [0..*]
- `<portfolio>` [0..*]
- `<party>` / `<account>`

したがって、**`<dataDocument>` の直下に単体の `<payout>` や `<payment>`、あるいはイベントである `<optionExercise>` を直接置くことはスキーマ違反（Validation Error）**となります。

##### (2) 標準的な実務解法: `<bulletPayment>` プロダクトの採用
`<dataDocument>` を最上位コンテナとして行使後の単一キャッシュ受渡（片道の確定資金移動）をデータ保持・伝送する場合、FpML 5.12 では **`<bulletPayment>`**（型: `BulletPayment`、[`confirmation/fpml-ird-5-12.xsd:31, 1856`](../../confirmation/fpml-ird-5-12.xsd)）を `<trade>` 配下のプロダクトとして格納します。

`<bulletPayment>` は XSD 上「*A product to represent a single cashflow*（単一のキャッシュフローを表現するプロダクト）」と定義されており、まさにデジタルオプション行使後の片道キャッシュ決済（Cash-or-Nothing Payout）の静的データモデリングに完全に合致します。

- **公式サンプル XML**: [`confirmation/products/interest-rate-derivatives/ird-ex28-bullet-payments.xml`](../../confirmation/products/interest-rate-derivatives/ird-ex28-bullet-payments.xml)
- **`<dataDocument>` 内での XML 構造例**:

```xml
<dataDocument xmlns="http://www.fpml.org/FpML-5/confirmation" fpmlVersion="5-12">
    <originatingEvent>Exercise</originatingEvent>
    <trade>
        <tradeHeader>
            <partyTradeIdentifier>
                <partyReference href="party1"/>
                <tradeId tradeIdScheme="http://www.partyA.com/trade-id">PAYOUT-12345</tradeId>
                <!-- 元となったデジタルオプションの取引IDを紐付け -->
                <linkId linkIdScheme="http://www.partyA.com/link-id">FX-OPT-99999</linkId>
            </partyTradeIdentifier>
            <tradeDate>2026-10-14</tradeDate>
        </tradeHeader>
        <!-- 行使後ペイアウト単体を単一キャッシュフロー取引として表現 -->
        <bulletPayment>
            <payment>
                <payerPartyReference href="party1"/>   <!-- オプション売り手 -->
                <receiverPartyReference href="party2"/><!-- オプション買い手 -->
                <paymentAmount>
                    <currency>USD</currency>
                    <amount>1000000.00</amount>
                </paymentAmount>
                <paymentDate>
                    <unadjustedDate>2026-10-16</unadjustedDate>
                    <dateAdjustments>
                        <businessDayConvention>MODFOLLOWING</businessDayConvention>
                        <businessCenters>
                            <businessCenter>USNY</businessCenter>
                        </businessCenters>
                    </dateAdjustments>
                </paymentDate>
            </payment>
        </bulletPayment>
    </trade>
    <party id="party1">
        <partyId partyIdScheme="http://www.fpml.org/coding-scheme/dummy-party-id">Party A (Seller)</partyId>
    </party>
    <party id="party2">
        <partyId partyIdScheme="http://www.fpml.org/coding-scheme/dummy-party-id">Party B (Buyer)</partyId>
    </party>
</dataDocument>
```

##### (3) アーキテクチャ上の使い分け（DataDocument vs Business Process）
- **`<dataDocument>` + `<bulletPayment>`**: EODポジション保持、元帳・会計システム、受渡決済システム（決済エンジン）等へ「受渡すべきキャッシュ債権債務」として静的データ連携を行う場合に適しています。
- **`<executionNotification>` + `<optionExercise>`**: 対カウンターパーティやブローカー・決済機関との間で「権利行使イベントが発生したこと」そのものを通知・合意するワークフローメッセージに適しています。

---

### FX オプション・ストラテジー（ストラドル等の複合戦略）と構成レグ識別子 (`strategyComponentIdentifier`)

東京の OTC 為替デリバティブ市場において、ボラティリティ取引や顧客の複雑なヘッジ・投資ニーズに応えるため、複数のバニラオプションや為替先物をパッケージ化した**ストラテジー取引（ストラドル、ストラングル、リバーサル、ブル／ベアスプレッド等）**が日常的に執行されます。

FpML 5.12 Confirmation View では、これらを単一の取引（`trade`）として包括する汎用コンテナ **`<strategy>`**（型: `Strategy`、[`confirmation/fpml-doc-5-12.xsd:1389`](../../confirmation/fpml-doc-5-12.xsd)）を提供しています。

さらに、ドッド・フランク法（CFTC SDR 報告）や EMIR、本邦の金融商品取引法に基づく取引情報蓄積機関（Trade Repository: TR）への規制報告において、**「パッケージ取引全体としての識別」に加えて「構成レグ（コンポーネント）ごとの固有識別子（USI: Unique Swap Identifier / UTI: Unique Transaction Identifier）の採番と紐付け」**が強く求められます。これを実現するのが **`<strategyComponentIdentifier>`** 要素です。

#### 1. 公式サンプル XML と取引構造の解剖 ([`fx-ex25-option-strategyComponentIdentifier.xml`](../../confirmation/products/fx-derivatives/fx-ex25-option-strategyComponentIdentifier.xml))

本サンプルは、豪ドル／米ドル（AUD/USD）を原資産とする**ロング・ストラドル（Long Straddle）**の約定コンファーメーション（`requestConfirmation`）です。

```
                    【ロング・ストラドル (Long Straddle) の構造】
                             行使価格 Strike = 0.5200
                         満期 Expiry = 2001-12-20 14:00 NY Cut
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
     【Leg 1: Option1】                              【Leg 2: Option2】
     AUD Put / USD Call                              AUD Call / USD Put
     買手: party1 / 売手: party2                     買手: party1 / 売手: party2
     想定元本: AUD 50M / USD 26M                     想定元本: AUD 50M / USD 26M
     プレミアム: USD 26,000 (0.10%)                  プレミアム: USD 26,000 (0.10%)
     ─────────────────────────────                   ─────────────────────────────
     USI: ...913 / UTI: ...913                       USI: ...914 / UTI: ...914
```

- **取引当事者**:
  - 買手 (Buyer): `party1` (PARTYA, LEI: `549300VBWWV6BYQOWM67`)
  - 売手 (Seller): `party2` (ABN Amro, LEI: `BFXS5XCH7N0Y05NIXW11`)
- **金融工学・クオンツ特性**:
  - 同一満期（2001-12-20 14:00:00 USNY）、同一ストライク（0.5200 USD/AUD）のアット・ザ・マネー（ATM）コールとプットを同数量購入。
  - 合計支払プレミアム: USD 52,000（USD 26,000 × 2）。
  - 方向性リスク（デルタ）を中立（デルタニュートラル）近辺に抑えつつ、インプライド・ボラティリティ（IV）の上昇（Vegaロング）および相場の急変動（ガンマロング）から収益を追求する典型的なボラティリティ買いポジション。
  - 損益分岐点（Breakeven）:
    $$\text{Upper} = 0.5200 + \frac{52,000}{50,000,000} = 0.52104 \quad (\text{USD/AUD})$$
    $$\text{Lower} = 0.5200 - \frac{52,000}{50,000,000} = 0.51896 \quad (\text{USD/AUD})$$

#### 2. `<strategyComponentIdentifier>` によるレグ単位の規制識別子マッピング

スキーマ定義箇所: [`confirmation/fpml-doc-5-12.xsd:1411`](../../confirmation/fpml-doc-5-12.xsd) (`StrategyComponentIdentification`)

```xml
<!-- confirmation/fpml-doc-5-12.xsd より抜粋 -->
<xsd:complexType name="StrategyComponentIdentification">
  <xsd:annotation>
    <xsd:documentation xml:lang="en">Associates trade identifiers with components of a strategy.</xsd:documentation>
  </xsd:annotation>
  <xsd:sequence>
    <xsd:element name="tradeIdentifierReference" type="PartyTradeIdentifierReference" maxOccurs="unbounded">
      <xsd:annotation>
        <xsd:documentation xml:lang="en">A reference to a party trade ID. If there are multiple trade IDs for a single component (e.g. USI, UTI, party-specific identifier), create a single "strategyComponentIdentifier" with a reference to the component, and multiple tradeIdentifierReferences, one referencing each applicable identifier.</xsd:documentation>
      </xsd:annotation>
    </xsd:element>
    <xsd:element name="componentReference" type="ProductReference">
      <xsd:annotation>
        <xsd:documentation xml:lang="en">A reference to a component of the strategy (typically a product).</xsd:documentation>
      </xsd:annotation>
    </xsd:element>
  </xsd:sequence>
</xsd:complexType>
```

##### サンプルにおける XML 実装構造

`tradeHeader` で宣言された各 `partyTradeIdentifier`（`Trade1-USI`, `Trade1-UTI`, `Trade2-USI`, `Trade2-UTI`）と、各オプションレグ（`Option1`, `Option2`）が、以下の通り厳密に結び付けられています。

```xml
<trade>
  <tradeHeader>
    <!-- Leg 1 用の USI / UTI -->
    <partyTradeIdentifier id="Trade1-USI">
      <issuer issuerIdScheme="http://www.fpml.org/coding-scheme/external/cftc/issuer-identifier">1037777777</issuer>
      <tradeId tradeIdScheme="http://www.fpml.org/coding-scheme/external/unique-transaction-identifier">01234567890123456789012345678913</tradeId>
    </partyTradeIdentifier>
    <partyTradeIdentifier id="Trade1-UTI">
      <issuer issuerIdScheme="http://www.fpml.org/coding-scheme/external/issuer-identifier">1037777777</issuer>
      <tradeId tradeIdScheme="http://www.fpml.org/coding-scheme/external/unique-transaction-identifier">01234567890123456789012345678913</tradeId>
    </partyTradeIdentifier>
    <!-- Leg 2 用の USI / UTI -->
    <partyTradeIdentifier id="Trade2-USI">
      <issuer issuerIdScheme="http://www.fpml.org/coding-scheme/external/cftc/issuer-identifier">1037777777</issuer>
      <tradeId tradeIdScheme="http://www.fpml.org/coding-scheme/external/unique-transaction-identifier">01234567890123456789012345678914</tradeId>
    </partyTradeIdentifier>
    <partyTradeIdentifier id="Trade2-UTI">
      <issuer issuerIdScheme="http://www.fpml.org/coding-scheme/external/issuer-identifier">1037777777</issuer>
      <tradeId tradeIdScheme="http://www.fpml.org/coding-scheme/external/unique-transaction-identifier">01234567890123456789012345678914</tradeId>
    </partyTradeIdentifier>
    <!-- 取引全体の親識別子 (Reuters Trade ID) -->
    <partyTradeIdentifier>
      <partyReference href="party1" />
      <tradeId tradeIdScheme="http://www.markets.Reuters.com/rss/spec/2001/trade-id-3-0">123456789</tradeId>
    </partyTradeIdentifier>
    <tradeDate>2001-11-20</tradeDate>
  </tradeHeader>

  <strategy>
    <productType productTypeScheme="http://www.sample.com/coding-scheme/product-type-simple">Straddle</productType>
    
    <!-- Option1 への識別子マッピング -->
    <strategyComponentIdentifier>
      <tradeIdentifierReference href="Trade1-USI" />
      <tradeIdentifierReference href="Trade1-UTI" />
      <componentReference href="Option1" />
    </strategyComponentIdentifier>
    
    <!-- Option2 への識別子マッピング -->
    <strategyComponentIdentifier>
      <tradeIdentifierReference href="Trade2-USI" />
      <tradeIdentifierReference href="Trade2-UTI" />
      <componentReference href="Option2" />
    </strategyComponentIdentifier>

    <!-- Leg 1: AUD Put / USD Call -->
    <fxOption id="Option1">
      <buyerPartyReference href="party1" />
      <sellerPartyReference href="party2" />
      <europeanExercise>
        <expiryDate>2001-12-20</expiryDate>
        <expiryTime>
          <hourMinuteTime>14:00:00</hourMinuteTime>
          <businessCenter>USNY</businessCenter>
        </expiryTime>
        <valueDate>2001-12-24</valueDate>
      </europeanExercise>
      <putCurrencyAmount>
        <currency>AUD</currency>
        <amount>50000000</amount>
      </putCurrencyAmount>
      <callCurrencyAmount>
        <currency>USD</currency>
        <amount>26000000</amount>
      </callCurrencyAmount>
      <strike>
        <rate>0.5200</rate>
        <strikeQuoteBasis>CallCurrencyPerPutCurrency</strikeQuoteBasis>
      </strike>
      <premium>
        <payerPartyReference href="party1" />
        <receiverPartyReference href="party2" />
        <paymentDate>
          <adjustableDate>
            <unadjustedDate>2001-11-23</unadjustedDate>
            <dateAdjustments>
              <businessDayConvention>NONE</businessDayConvention>
            </dateAdjustments>
          </adjustableDate>
        </paymentDate>
        <paymentAmount>
          <currency>USD</currency>
          <amount>26000</amount>
        </paymentAmount>
        <quote>
          <value>0.001</value>
          <quoteBasis>PercentageOfCallCurrencyAmount</quoteBasis>
        </quote>
      </premium>
    </fxOption>

    <!-- Leg 2: AUD Call / USD Put -->
    <fxOption id="Option2">
      <buyerPartyReference href="party1" />
      <sellerPartyReference href="party2" />
      <europeanExercise>
        <expiryDate>2001-12-20</expiryDate>
        <expiryTime>
          <hourMinuteTime>14:00:00</hourMinuteTime>
          <businessCenter>USNY</businessCenter>
        </expiryTime>
        <cutName>NewYork</cutName>
        <valueDate>2001-12-24</valueDate>
      </europeanExercise>
      <putCurrencyAmount>
        <currency>USD</currency>
        <amount>26000000</amount>
      </putCurrencyAmount>
      <callCurrencyAmount>
        <currency>AUD</currency>
        <amount>50000000</amount>
      </callCurrencyAmount>
      <strike>
        <rate>0.5200</rate>
        <strikeQuoteBasis>PutCurrencyPerCallCurrency</strikeQuoteBasis>
      </strike>
      <premium>
        <payerPartyReference href="party1" />
        <receiverPartyReference href="party2" />
        <paymentDate>
          <adjustableDate>
            <unadjustedDate>2001-11-23</unadjustedDate>
            <dateAdjustments>
              <businessDayConvention>NONE</businessDayConvention>
            </dateAdjustments>
          </adjustableDate>
        </paymentDate>
        <paymentAmount>
          <currency>USD</currency>
          <amount>26000</amount>
        </paymentAmount>
        <quote>
          <value>0.001</value>
          <quoteBasis>PercentageOfPutCurrencyAmount</quoteBasis>
        </quote>
      </premium>
    </fxOption>
  </strategy>
</trade>
```

#### 3. ペイオフダイアグラムと満期損益構造（クオンツ分析）

豪ドル／米ドル（AUD/USD）ロング・ストラドルの満期時（$T = \text{2001-12-20}$）における純損益（Net P&L）は、満期スポット相場 $S_T$（USD per AUD）、行使価格 $K = 0.5200$、豪ドル想定元本 $N = 50,000,000$ AUD、合計支払プレミアム $P_{\text{total}} = 52,000$ USD に対して次式で決定されます。

$$\begin{aligned}
\text{Net P\&L}(S_T) &= \text{Leg 1 Payoff}(S_T) + \text{Leg 2 Payoff}(S_T) - P_{\text{total}} \\
&= \max(K - S_T, 0) \times N + \max(S_T - K, 0) \times N - 52,000 \\
&= |S_T - 0.5200| \times 50,000,000 - 52,000 \quad (\text{USD})
\end{aligned}$$

##### 【ペイオフダイアグラム（満期損益 V字チャート）】

```text
 満期純損益 Net P&L (USD)
      ▲
      │
+100k ┤  ＼                                                             ／
      │    ＼                                                         ／
 +52k ┤      ＼    Leg 1: AUD Put 損益                              ／    Leg 2: AUD Call 損益
      │        ＼  - - - - - - - - - -                             ／  - - - - - - - - - -
    0 ┼──────────●─────────────────────────────────────────●────────────────► 満期スポット相場 S_T
      │          ／＼                                         ／＼               (AUD/USD)
      │        ／    ＼                                     ／    ＼
      │      ／        ＼                                 ／        ＼
      │    ／            ＼                             ／            ＼
 -26k ┼──● - - - - - - - - ＼ - - - - - - - - - - - - ／ - - - - - - - - ●  (各レグ単体 -$26k)
      │  ：                 ＼                     ／                 ：
      │  ：                   ＼                 ／                   ：
      │  ：                     ＼             ／                     ：
 -52k ┼─：───────────────────────＼─────────／───────────────────────：  (最大損失: -$52,000)
      │  ：                         ＼     ／                         ：
      │  ：                            ▼                              ：
      │  ：                        K = 0.5200                         ：
      │  ：                       (Strike ATM)                        ：
      │  ：                                                           ：
      └──┴──────────────────────────────┴─────────────────────────────┴─────►
        下限損益分岐点 (Lower BEP)    ストライク (ATM)             上限損益分岐点 (Upper BEP)
          0.51896 USD/AUD              0.5200 USD/AUD               0.52104 USD/AUD
```

##### 【満期スポット相場 $S_T$ の水準別損益シナリオ】

| 満期スポット相場 $S_T$ | Leg 1: AUD Put (USD) | Leg 2: AUD Call (USD) | 合計プレミアム支払 (USD) | 純損益 Net P&L (USD) | 状態・解説 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$S_T \le 0.51896$**<br>(大幅下落) | $(0.5200 - S_T) \times 50\text{M}$<br>(In-the-Money) | 0<br>(Out-of-the-Money) | $-52,000$ | **プラス（利益無制限）**<br>下落幅に応じて利益拡大 |
| **$S_T = 0.51896$** | $+52,000$ | 0 | $-52,000$ | **$0$（下限損益分岐点）** | プレミアム回収完了 |
| **$0.51896 < S_T < 0.5200$** | $(0.5200 - S_T) \times 50\text{M}$ | 0 | $-52,000$ | マイナス（損失幅: $0 \sim -52,000$） | Put行使もプレミアム未満 |
| **$S_T = 0.5200$**<br>(完全膠着・無風) | 0 | 0 | $-52,000$ | **$-52,000$（最大損失）** | 両オプションとも無価値失効 |
| **$0.5200 < S_T < 0.52104$** | 0 | $(S_T - 0.5200) \times 50\text{M}$ | $-52,000$ | マイナス（損失幅: $-52,000 \sim 0$） | Call行使もプレミアム未満 |
| **$S_T = 0.52104$** | 0 | $+52,000$ | $-52,000$ | **$0$（上限損益分岐点）** | プレミアム回収完了 |
| **$S_T \ge 0.52104$**<br>(大幅上昇) | 0<br>(Out-of-the-Money) | $(S_T - 0.5200) \times 50\text{M}$<br>(In-the-Money) | $-52,000$ | **プラス（利益無制限）**<br>上昇幅に応じて利益拡大 |

#### 4. 市場実務・システム設計における意義

1. **パッケージ取引の整合性と個別レグ規制報告の両立**:
   - フロントオフィスおよびミドルオフィスの取引管理システム（例: Murex, Calypso, Wallstreet Suite）では、ストラドル等の戦略を「1つの複合取引」として管理し、マージン・プライシングやパッケージ全体の相殺プレミアム決済を行います。
   - 一方で、SDR/TR 規制報告や清算機関（CCP）との照合（Matching）では、レグごとにユニークな USI/UTI を提出する必要があります。
   - `strategyComponentIdentifier` は、この「親取引としての完全性」と「子レグとしての個別規制識別性」を FpML 標準構文として矛盾なく両立させるための不可欠な設計パターンです。
2. **複数の規制体系（USI と UTI）の同居対応**:
   - `StrategyComponentIdentification` は `<tradeIdentifierReference>` を `maxOccurs="unbounded"` で許容しているため、同一レグに対して CFTC 向けの USI と グローバル/EMIR/金商法向けの UTI の双方が同時に紐付け可能となっています。

---

### シンセティックフォワード (Synthetic Forward) の表現とサンプルXMLの有無

東京の OTC 為替デリバティブ市場において、**シンセティックフォワード（Synthetic Forward / 合成為替予約）**は、プット・コール・パリティ（Put-Call Parity）に基づき、同一満期・同一ストライクの「Call 買い ＋ Put 売り」（または「Put 買い ＋ Call 売り」）を組み合わせることで、実質的に通常の為替先渡取引（Forward）と完全に同一の線形損益を複製する取引戦略です。

顧客の信用枠（クレジットライン）制約、特定通貨の先物規制・資本規制の回避、あるいはオプションブックとの統合ヘッジ・裁定取引等で頻繁に利用されます。

#### 1. 公式サンプル XML の所在状況

ワークスペース内の [`confirmation/products/fx-derivatives/`](../../confirmation/products/fx-derivatives) 配下全 68 ファイルを精査した結果：

- **ファイル名として `synthetic-forward` という名称を持つ単独の公式サンプル XML は存在しません**。
- しかし、FpML 5.12 Confirmation View では、前述のロング・ストラドル公式サンプル（[`fx-ex23-straddle.xml`](../../confirmation/products/fx-derivatives/fx-ex23-straddle.xml)、[`fx-ex25-option-strategyComponentIdentifier.xml`](../../confirmation/products/fx-derivatives/fx-ex25-option-strategyComponentIdentifier.xml)）と**全く同一の `<strategy>` コンテナ（型: `Strategy`、[`confirmation/fpml-doc-5-12.xsd:1389`](../../confirmation/fpml-doc-5-12.xsd)）**を用いて完全にモデル化されます。
- また、最も近い派生ストラクチャード・フォワードの公式サンプルとして、`<strategy>` 配下で「Call 買い」と「アクルーアル Put 売り」を合成した **[`fx-ex48-accrual-option-strategy-fading-extra.xml`](../../confirmation/products/fx-derivatives/fx-ex48-accrual-option-strategy-fading-extra.xml)**（`FadingForwardStrategy`）が提供されています。

#### 2. 金融工学・クオンツ数理（プット・コール・パリティ）

満期 $T$ における為替スポットレートを $S_T$、行使価格を $K$ とすると、**シンセティック・ロング・フォワード（買い）**の満期ペイオフは次のように線形化されます：

$$\begin{aligned}
\text{Payoff}_{\text{Synthetic Long Forward}} &= \text{Call 買い} + \text{Put 売り} \\
&= \max(S_T - K, 0) - \max(K - S_T, 0) \\
&= S_T - K \quad (\text{通常の為替先渡の買いと完全一致})
\end{aligned}$$

- $S_T \ge K$ の場合: Call が行使されて $(S_T - K)$、Put は無価値（0） $\implies S_T - K$
- $S_T < K$ の場合: Call は無価値（0）、Put が被行使となり $-(K - S_T) = S_T - K$ $\implies S_T - K$

約定時の行使価格 $K$ をフォワード相場 $F = S_0 e^{(r_{\text{quote}} - r_{\text{base}})T}$（ATM Forward）に設定した場合、Call と Put の理論プレミアムは完全に均衡し、**ネット支払プレミアムはゼロ（Zero Cost Forward）**となります。

#### 3. FpML 5.12 での実装構造（XML スニペット）

ストラドルが「2つのオプションの買手・売手が同一方向」であるのに対し、シンセティックフォワードは**「2つのオプションの買手・売手（`buyerPartyReference` / `sellerPartyReference`）が互い違い（反転）に設定される」**点がアーキテクチャ上の決定的な差異です。

以下は、EUR/USD 1.1000 のシンセティック・ロング・フォワード（EUR 10,000,000 買い / USD 11,000,000 売り）を FpML 5.12 Confirmation View で表現した完全な XML 構文例です。

```xml
<trade>
  <tradeHeader>
    <partyTradeIdentifier>
      <partyReference href="party1" />
      <tradeId tradeIdScheme="http://www.bb.com/trade-id">SYNTH-FWD-001</tradeId>
    </partyTradeIdentifier>
    <tradeDate>2026-10-17</tradeDate>
  </tradeHeader>
  
  <strategy>
    <!-- 戦略タイプ: SyntheticForward -->
    <productType productTypeScheme="http://www.fpml.org/coding-scheme/product-type-simple">SyntheticForward</productType>
    
    <!-- Leg 1: Long EUR Call / Short USD Put (party1 が購入) -->
    <fxOption id="CallLeg">
      <buyerPartyReference href="party1" />
      <sellerPartyReference href="party2" />
      <europeanExercise>
        <expiryDate>2026-12-17</expiryDate>
        <expiryTime>
          <hourMinuteTime>15:00:00</hourMinuteTime>
          <businessCenter>JPTO</businessCenter>
        </expiryTime>
        <valueDate>2026-12-21</valueDate>
      </europeanExercise>
      <putCurrencyAmount>
        <currency>USD</currency>
        <amount>11000000.00</amount>
      </putCurrencyAmount>
      <callCurrencyAmount>
        <currency>EUR</currency>
        <amount>10000000.00</amount>
      </callCurrencyAmount>
      <strike>
        <rate>1.1000</rate>
        <strikeQuoteBasis>PutCurrencyPerCallCurrency</strikeQuoteBasis>
      </strike>
    </fxOption>

    <!-- Leg 2: Short EUR Put / Long USD Call (party1 が売却 -> buyer は party2) -->
    <fxOption id="PutLeg">
      <buyerPartyReference href="party2" />
      <sellerPartyReference href="party1" />
      <europeanExercise>
        <expiryDate>2026-12-17</expiryDate>
        <expiryTime>
          <hourMinuteTime>15:00:00</hourMinuteTime>
          <businessCenter>JPTO</businessCenter>
        </expiryTime>
        <valueDate>2026-12-21</valueDate>
      </europeanExercise>
      <putCurrencyAmount>
        <currency>EUR</currency>
        <amount>10000000.00</amount>
      </putCurrencyAmount>
      <callCurrencyAmount>
        <currency>USD</currency>
        <amount>11000000.00</amount>
      </callCurrencyAmount>
      <strike>
        <rate>1.1000</rate>
        <strikeQuoteBasis>CallCurrencyPerPutCurrency</strikeQuoteBasis>
      </strike>
    </fxOption>
  </strategy>
</trade>
```

---

## 3. 関連 Wiki ページ
- [Shared Foundation](../common/shared-foundation.md)
- [Overview](../overview.md)
- [Index](../index.md)



