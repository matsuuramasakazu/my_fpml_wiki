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

## 4. キャッシュフロー表現における `FloatingRateDefinition` と複数キャップ/フロアの用途

`cashflows` 表記（`paymentCalculationPeriod` -> `calculationPeriod` -> `floatingRateDefinition`）における `FloatingRateDefinition` 型（[`confirmation/fpml-ird-5-12.xsd`](../../confirmation/fpml-ird-5-12.xsd#L760-L796)）では、`capRate` および `floorRate` 要素が `minOccurs="0" maxOccurs="unbounded"` として定義されています。
また、ストライク要素の `Strike` 型（[`confirmation/fpml-shared-5-12.xsd`](../../confirmation/fpml-shared-5-12.xsd#L4042-L4064)）は `strikeRate` のみならず `buyer` / `seller` を保持します。

*(※注: リポジトリ内のサンプル XML には `capRateSchedule` / `floorRateSchedule` を含む [`ird-ex22-cap.xml`](../../confirmation/products/interest-rate-derivatives/ird-ex22-cap.xml) や [`ird-ex24-collar.xml`](../../confirmation/products/interest-rate-derivatives/ird-ex24-collar.xml)、およびキャッシュフロー表記を含む [`ird-ex26-fxnotional-swap-with-cfs.xml`](../../confirmation/products/interest-rate-derivatives/ird-ex26-fxnotional-swap-with-cfs.xml) が存在しますが、`floatingRateDefinition` 内に複数 `capRate`/`floorRate` が直接記述されたサンプル XML 自体は同梱されていません。以下の用途は XSD スキーマ仕様および実務構造に基づく解説です。)*

単一の計算期間（Calculation Period）内でこれらが複数保持可能となっている実務的用途：
1. **キャップ・スプレッド (Cap Spread) / コリドー・スワップ (Corridor Swap)**:
   単一計算期間に対し、異なるストライクと売買方向のキャップを同居させる取引（例: Strike 3.0% の Long Cap と Strike 5.0% の Short Cap）。同一の `floatingRateDefinition` 内に `buyer` / `seller` が異なった複数の `capRate` 要素を配置します。
2. **フロア・スプレッド (Floor Spread)**:
   金利下限側で高いストライクの Long Floor と低いストライクの Short Floor を組み合わせる場合。同一の `floatingRateDefinition` 内に複数の `floorRate` 要素を配置します。
3. **多段階・複合ストライク構造 (Multi-Strike / Double Cap)**:
   同一計算期間に複数の権利行使条件が段階的・複合的に紐づく構造化スワップの展開後キャッシュフロー表現。

#### 【具体的な FpML XML 記述例 (Cap Spread: Strike 3.0% Long / 5.0% Short)】

`fpml-ird-5-12.xsd` (Line 760-796) および `fpml-shared-5-12.xsd` (Line 4042-4064) に準拠した `floatingRateDefinition` の具体的な記述例です。

```xml
<calculationPeriod>
  <unadjustedStartDate>2026-04-01</unadjustedStartDate>
  <unadjustedEndDate>2026-10-01</unadjustedEndDate>
  <adjustedStartDate>2026-04-01</adjustedStartDate>
  <adjustedEndDate>2026-10-01</adjustedEndDate>
  <calculationPeriodNumberOfDays>183</calculationPeriodNumberOfDays>
  <floatingRateDefinition>
    <!-- 計算期間の最終適用金利 (例: 3.5% = 0.035) -->
    <calculatedRate>0.035</calculatedRate>
    <!-- 金利観測 (Fixing) 情報 -->
    <rateObservation>
      <adjustedFixingDate>2026-03-30</adjustedFixingDate>
      <observedRate>0.035</observedRate>
    </rateObservation>

    <!-- 1. Long Cap: Strike 3.0% (Party A が買い手) -->
    <capRate>
      <strikeRate>0.03</strikeRate>
      <buyer>Payer</buyer>     <!-- Party A (金利支払人) がオプション買い手 -->
      <seller>Receiver</seller> <!-- Party B (金利受取人) がオプション売り手 -->
    </capRate>

    <!-- 2. Short Cap: Strike 5.0% (Party A が売り手) -->
    <capRate>
      <strikeRate>0.05</strikeRate>
      <buyer>Receiver</buyer> <!-- Party B (金利受取人) が買い手 -->
      <seller>Payer</seller>   <!-- Party A (金利支払人) が売り手 -->
    </capRate>
  </floatingRateDefinition>
</calculationPeriod>
```

#### 【FloatingRateDefinition 全体のネット実効支払金利 (Net Effective Rate) ダイアグラム】

`floatingRateDefinition` 全体として、変動金利支払人（Party A: `Payer`）が最終的に負担する **ネット実効支払金利 ($R_{\text{net}}$)** の全体ペイオフ構造です。

```text
  Net Effective
  Rate R_net (%)
         ^
    5.0% |                 /  (傾き +1: R_net = R - 2.0%)
         |                /
    4.0% |               /
         |              /
    3.0% |     +=======+  (R_net = 3.0% 一定)
         |    /|       |
    2.0% |   / |       |
         |  /  |       |
    1.0% | /   |       |
         |/    |       |
    0.0% +-----+-------+-------------> Observed Rate R (%)
        0%    3.0%             5.0%
              (K1)             (K2)
```

##### 【ネット実効支払金利 ($R_{\text{net}}$) の全体算式と動作メカニズム】

1. **全体ネット実効支払金利の算式**:
   $$ \begin{aligned} R_{\text{net}}(R) &= \text{変動金利支払い}(R) - \text{Cap Spread受給額}(R) \\ &= R - \left( \max(0, R - 3.0\%) - \max(0, R - 5.0\%) \right) \end{aligned} $$

2. **観測金利 ($R$) の区間別ネット支払負担**:
   - **$R \le 3.0\%$ (裸の変動金利支払い)**:
     - Cap Spread 受け $= 0.0\%$
     - **ネット支払金利 $R_{\text{net}} = R$** （市場金利をそのまま支払う。例: $R = 1.0\%$ のとき $R_{\text{net}} = 1.0\%$、$R = 0.5\%$ のとき $R_{\text{net}} = 0.5\%$。※金利自体がマイナス金利にならない限りマイナスにはなりません）
   - **$3.0\% < R < 5.0\%$ (キャップ完全発動・固定領域)**:
     - Cap Spread 受け $= R - 3.0\%$
     - **ネット支払金利 $R_{\text{net}} = R - (R - 3.0\%) = \mathbf{3.0\% \text{ （完全一定）}}$**
     - 金利が 3.0% から 5.0% へ上昇しても、実質支払金利は上限 **3.0% に完全固定** されます。
   - **$R \ge 5.0\%$ (ヘッジ上限到達・追随領域)**:
     - Cap Spread 受け $= 5.0\% - 3.0\% = 2.0\%$ (上限値で一定)
     - **ネット支払金利 $R_{\text{net}} = R - 2.0\%$**
     - この式は $R \ge 5.0\%$ の領域のみに適用され、最低でも $5.0\% - 2.0\% = 3.0\%$ となります。
     - 金利が 5.0% を超えると、最大ヘッジ幅 2.0% を控除した金利で再び傾き +1 で追随上昇します（例: $R=6.0\%$ のとき $R_{\text{net}}=4.0\%$）。

---

## 5. 関連 Wiki ページ
- [Shared Foundation](../common/shared-foundation.md)
- [Overview](../overview.md)
- [Cross-Currency Swaps (通貨スワップ)](./xccy-swap.md)
- [Non-Deliverable Swap (NDS) の期中 Fixing 済みキャッシュフロー表現とイベントモデル](./nds-cashflows-and-fixing.md)
- [Business Processes](../processes/business-processes.md)



