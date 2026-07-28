---
title: FpML Common Foundation & Shared Schemas
tags: [fpml, shared, foundation, types, schemas]
updated: 2026-07-25
---

# FpML 共通基盤 & 共有型 (Shared Foundation)

## 1. 共通スキーマ構成

すべての FpML 5.12 プロダクト構造は、以下の基盤 XSD スキーマに依存しています：

| スキーマファイル | 役割・概要 |
| --- | --- |
| [`fpml-main-5-12.xsd`](../../confirmation/fpml-main-5-12.xsd) | ルート要素定義、取引メッセージ・プロセスメッセージの基本コンテナ定義 |
| [`fpml-shared-5-12.xsd`](../../confirmation/fpml-shared-5-12.xsd) | 金額 (`Money`), 取引当事者 (`Party`), 日付構造 (`AdjustedDate`), 営業日調整 (`BusinessDayAdjustments`) 等の広範な共通型定義 |
| [`fpml-enum-5-12.xsd`](../../confirmation/fpml-enum-5-12.xsd) | ISDA 規定値、通貨コード、支払頻度、営業日調整コンベンション等の列挙型定義 |
| [`fpml-asset-5-12.xsd`](../../confirmation/fpml-asset-5-12.xsd) | 原資産 (Underlyer: 株式, 債券, 指数, 商品等) や手数料・配当関連のデータ構造 |

---

## 2. 主要な共通 Complex Types

### Money 型
金額と通貨コードを表現する基本型。
```xml
<amount>
    <currency>USD</currency>
    <amount>10000000.00</amount>
</amount>
```

### BusinessDayAdjustments 型
ISDA 慣行に基づく営業日調整ルールを定義。
- `businessDayConvention`: `FOLLOWING`（翌営業日）, `MODFOLLOWING`（変形翌営業日 / Modified Following）, `PRECEDING`（前営業日）, `MODPRECEDING`（変形前営業日）, `NONE` 等。
- `financialBusinessCenters`: `USNY` (New York), `GBLO` (London), `JPTO` (Tokyo) 等の休業日都市・営業日センター。

```xml
<dateAdjustments>
    <businessDayConvention>MODFOLLOWING</businessDayConvention>
    <financialBusinessCenters>
        <financialBusinessCenter>GBLO</financialBusinessCenter>
        <financialBusinessCenter>USNY</financialBusinessCenter>
    </financialBusinessCenters>
</dateAdjustments>
```

### Party 型
取引の当事者（金融機関、ファンド、CP / カウンターパーティ等）を表す要素。
```xml
<party id="party1">
    <partyId partyIdScheme="http://www.fpml.org/coding-scheme/external/iso17442">LEI1234567890ABCDEFG</partyId>
    <partyName>Bank A</partyName>
</party>
```

---

## 3. 日数計算コンベンション (Day Count Fractions: `30E/360` vs `30E/360.ISDA`)

FpML コードリスト [`codelist/day-count-fraction-2-3.xml`](../../codelist/day-count-fraction-2-3.xml) で定義されている日分基準のうち、主に欧州債・デリバティブ市場で用いられる **`30E/360`** と **`30E/360.ISDA`** の相違点と算術アルゴリズムの解説です。

基本算式:
$$\text{Fraction} = \frac{360 \times (Y_2 - Y_1) + 30 \times (M_2 - M_1) + (D_2 - D_1)}{360}$$
（開始日 $(Y_1, M_1, D_1)$、終了日 $(Y_2, M_2, D_2)$）

### 3.1 アルゴリズムの比較

| 項目 | `30E/360` (Eurobond Basis) | `30E/360.ISDA` (Eurobond Basis - ISDA Method) |
|---|---|---|
| **コードリスト定義** | [`codelist/day-count-fraction-2-3.xml` L67-L83](../../codelist/day-count-fraction-2-3.xml#L67-L83) | [`codelist/day-count-fraction-2-3.xml` L84-L100](../../codelist/day-count-fraction-2-3.xml#L84-L100) |
| **ISDA 準拠定義** | 2021 ISDA Sec 4.6.1(vii) / 2006 ISDA Sec 4.16(g) | 2021 ISDA Sec 4.6.1(viii) / 2006 ISDA Sec 4.16(h) |
| **開始日 $D_1$ の調整** | $D_1 = 31 \rightarrow D_1 = 30$ | $D_1 = 31$ または **2月末日** $\rightarrow D_1 = 30$ |
| **終了日 $D_2$ の調整** | $D_2 = 31 \rightarrow D_2 = 30$（一律） | $D_2 = 31 \rightarrow D_2 = 30$。<br>**ただし、終了日が計算期間の最終日 (Termination Date) の場合は 30 に変更せず 31 のまま保持する**。 |

### 3.2 具体的計算例の比較（例: 8月31日 〜 12月31日）
- **`30E/360`**:
  - $D_1 = 31 \rightarrow 30$, $D_2 = 31 \rightarrow 30$ (Termination Date でも 30 に変更)
  - 分子日数: $30 \times (12 - 8) + (30 - 30) = 120$ 日
- **`30E/360.ISDA`**:
  - $D_1 = 31 \rightarrow 30$, $D_2 = 31 \rightarrow 31$ (12月31日が Termination Date のため 31 を維持)
  - 分子日数: $30 \times (12 - 8) + (31 - 30) = 121$ 日

---

## 4. 関連 Wiki ページ
- [Overview](../overview.md)
- [Interest Rate Derivatives](../products/ird.md)
- [Index](../index.md)
