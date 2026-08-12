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

### 4.2 `ecore:reference` (Eclipse Modeling Framework メタデータ) の詳細構造と情報ソース引用

#### 4.2.1 概要と情報ソースの具体的場所
`ecore:reference` は、FpML スキーマをベースに Eclipse Modeling Framework (EMF) やクラス自動生成エンジン（Java, C#, C++ 等）がドメインモデルをビルドする際、IDREF ポインタを強型付け（Strongly Typed）されたオブジェクト参照へマッピングするための拡張メタデータ属性です。

- **ローカルスキーマでの定義場所 ([`confirmation/fpml-shared-5-12.xsd` L7, L2845](../../confirmation/fpml-shared-5-12.xsd#L7)):**
  - ヘッダー宣言 ([L7](../../confirmation/fpml-shared-5-12.xsd#L7)):
    ```xml
    <xsd:schema xmlns:ecore="http://www.eclipse.org/emf/2002/Ecore"
                targetNamespace="http://www.fpml.org/FpML-5/confirmation"
                ecore:documentRoot="FpML"
                ecore:nsPrefix="conf"
                ecore:package="org.fpml.confirmation" ...>
    ```
    `xmlns:ecore="http://www.eclipse.org/emf/2002/Ecore"` をインポートし、Ecore マッピング用のパッケージ名 (`org.fpml.confirmation`) やドキュメントルート (`FpML`) を指定しています。
  - 属性定義 ([L2845](../../confirmation/fpml-shared-5-12.xsd#L2845)):
    ```xml
    <xsd:complexType name="PartyReference">
      <xsd:complexContent>
        <xsd:extension base="Reference">
          <xsd:attribute name="href" type="xsd:IDREF" use="required" ecore:reference="Party" />
        </xsd:extension>
      </xsd:complexContent>
    </xsd:complexType>
    ```
- **EMF API メタデータ仕様のソースコード ([`org.eclipse.emf.ecore.util.ExtendedMetaData.java`](https://raw.githubusercontent.com/eclipse-emf/org.eclipse.emf/master/plugins/org.eclipse.emf.ecore/src/org/eclipse/emf/ecore/util/ExtendedMetaData.java)):**
  - Javadoc 仕様定義より引用:
    > *"Interface for accessing and setting extended metadata on Ecore model elements. Such metadata is primarily used to support structures defined in XML schema and to retain additional information that a resource requires to produce conforming serializations."*
  - `ExtendedMetaData` インターフェースにより、XSD スキーマ上の追加アノテーション（`ANNOTATION_URI = "http:///org/eclipse/emf/ecore/util/ExtendedMetaData"`）が Ecore モデル上の `EReference` や `EClass` に動的バインドされます。

#### 4.2.2 技術的メカニズムと強型付けオブジェクトモデルの比較

1. **W3C XSD 1.0 の限界と `ecore:reference` の補完**
   W3C XML Schema 1.0 の `type="xsd:IDREF"` 仕様 ([W3C XML Schema Part 2 Sec 3.3.9](https://www.w3.org/TR/xmlschema-2/#IDREF)) は、参照先の `id` が同文書内に存在するかという参照整合性のみを検証し、**「その参照先がどの Complex Type（`Party` なのか `Account` なのか）であるか」というターゲット型制約 (Target Type Constraint) をスキーマ単体で指定できません**。

2. **Containment（包摂）と Non-Containment Reference（非包含参照）の対比**
   EMF の Ecore メタモデルにおけるオブジェクト間の関係定義：
   - **Containment (`containment=true`):** 親要素が子要素を直接所有する包含関係（例: `Trade` が `TradeHeader` や Swap レグ要素を直下に含む構造）。
   - **Non-Containment Cross-Reference (`containment=false`):** ドキュメント内の異なる場所にある独立した要素をポインタ参照する関係。
   `ecore:reference="Party"` アノテーションは、EMF Importer に対し「この `href` 属性は `containment=false` かつ参照先型 `eType=Party` である `EReference` としてモデル化せよ」と直接指示します。

3. **ドメインコード自動生成（Code Generation）における差異**
   - **アノテーションなし（標準 XSD のみからクラス生成した場合）:**
     ```java
     // href は単なる汎用 ID 文字列として展開されてしまう
     public class PartyReference {
         private String href;
         public String getHref() { return href; }
     }
     ```
   - **`ecore:reference="Party"` アノテーションあり（FpML / EMF モデルバインディング時）:**
     ```java
     // Party オブジェクトへの強型付け参照ポインタとして展開される
     public class PartyReference extends Reference {
         private Party party; // ecore:reference="Party" により直感的な型バインドを実現
         public Party getParty() { return party; }
         public void setParty(Party value) { this.party = value; }
     }
     ```
   これにより、フロントオフィスの開発者やクオンツ・アナリストは、文字列 ID のパースや手動検索コードを書くことなく、`partyReference.getParty().getPartyName()` のように直感的にドメインモデルのオブジェクトグラフを走査することが可能になります。

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
