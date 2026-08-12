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

## 4. ドキュメント内参照メカニズム (`xsd:IDREF` と `ecore:reference`)

FpML では、同一 XML ドキュメント内でデータ重複を防ぎ構造を関係付けするために、参照（Intra-Document Pointer）パターンが多用されます（例: [`PartyReference`](../../confirmation/fpml-shared-5-12.xsd#L2839-L2848)）。

```xml
<xsd:complexType name="PartyReference">
  <xsd:complexContent>
    <xsd:extension base="Reference">
      <xsd:attribute name="href" type="xsd:IDREF" use="required" ecore:reference="Party" />
    </xsd:extension>
  </xsd:complexContent>
</xsd:complexType>
```

### 4.1 `xsd:IDREF` (W3C XML Schema 組込み型)
- **概要**: `xmlns:xsd="http://www.w3.org/2001/XMLSchema"` 名前空間で規定されている W3C 標準の組み込み単純型。
- **役割**: XML ドキュメント内の別の要素が持つ `xsd:ID` 型属性（例: `<party id="party1">`）の値とリンクし、参照整合性（参照先の ID が文書内に実在するか）を XML バリデータレベルで保証する。

### 4.2 `ecore:reference` (Eclipse Modeling Framework メタデータ)
- **概要**: [`fpml-shared-5-12.xsd` L7](../../confirmation/fpml-shared-5-12.xsd#L7) で定義されている名前空間 `xmlns:ecore="http://www.eclipse.org/emf/2002/Ecore"` による拡張アノテーション属性。
- **役割**: `xsd:IDREF` 自体は単なる汎用ポインタ（型情報を持たない参照）であるため、コードジェネレータ（EMF や Java/C# クラス生成ツール）に対して「この参照属性 (`href`) の指し示す具体的ドメイン型は `Party` である」というメタ情報を提示し、強型付けされたオブジェクトモデル（例: `Party party` メンバー変数）を自動生成させるために用いられる。

### 4.3 一次情報ソース (Official Documentation & Standards - Verified Live)
- **`xsd:IDREF` 仕様 (W3C)**:
  - [W3C XML Schema Part 2: Datatypes Second Edition (Section 3.3.9 IDREF)](https://www.w3.org/TR/xmlschema-2/#IDREF)
  - [W3C XML Schema Definition Language (XSD) 1.1 Part 2: Datatypes (Section 3.3.9 IDREF)](https://www.w3.org/TR/xmlschema11-2/#IDREF)
- **`ecore` / EMF 仕様 (Eclipse Foundation & FpML)**:
  - [Eclipse Modeling Framework (EMF) Official Project Page](https://eclipse.dev/modeling/emf/)
  - [Eclipse EMF ExtendedMetaData Official GitHub Source & Javadoc](https://raw.githubusercontent.com/eclipse-emf/org.eclipse.emf/master/plugins/org.eclipse.emf.ecore/src/org/eclipse/emf/ecore/util/ExtendedMetaData.java)
  - [FpML Official Portal](https://www.fpml.org/)

---

## 5. 関連 Wiki ページ
- [Overview](../overview.md)
- [Interest Rate Derivatives](../products/ird.md)
- [Index](../index.md)
