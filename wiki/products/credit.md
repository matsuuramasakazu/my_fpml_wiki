---
title: Credit Derivatives Knowledge
tags: [fpml, credit, cds, credit-default-swap, reference-entity, credit-event]
updated: 2026-07-25
---

# クレジット・デリバティブ (Credit Derivatives)

## 1. 概要と該当スキーマ

クレジット・デリバティブ分野は、単一銘柄の Credit Default Swap (Single Name CDS)、バスケット/インデックス CDS、クレジットイベント通知メッセージなどをカバーします。

- **主スキーマ**:
  - [`confirmation/fpml-cd-5-12.xsd`](../../confirmation/fpml-cd-5-12.xsd) - CDS 取引定義
  - [`confirmation/fpml-credit-event-notification-5-12.xsd`](../../confirmation/fpml-credit-event-notification-5-12.xsd) - クレジットイベント通知メッセージ
- **サンプル XML**: [`confirmation/products/credit-derivatives/`](../../confirmation/products/credit-derivatives)

---

## 2. 主要プロダクト構造

### Credit Default Swap (`creditDefaultSwap`)
プロテクション買い手 (`buyerPartyReference`) と売り手 (`sellerPartyReference`)、参照体 / 参照企業 (`generalTerms/referenceInformation`)、参照債務 (Reference Obligation)、プレミアム / フィー・レグ (Fee Leg)、プロテクション条件・信用事由 (Protection Terms / Credit Events) を定義します。

```xml
<creditDefaultSwap>
    <generalTerms>
        <buyerPartyReference href="party1"/>
        <sellerPartyReference href="party2"/>
        <referenceInformation>
            <referenceEntity id="refEntity">
                <entityName>Example Reference Corporation</entityName>
                <entityId entityIdScheme="http://www.fpml.org/coding-scheme/external/entity-id-RED">RED12345</entityId>
            </referenceEntity>
        </referenceInformation>
    </generalTerms>
    <feeLeg>
        <periodicPayment>
            <fixedAmountCalculation>
                <fixedRate>0.01</fixedRate> <!-- 100 bps -->
            </fixedAmountCalculation>
        </periodicPayment>
    </feeLeg>
    <protectionTerms>
        <creditEvents>
            <bankruptcy>true</bankruptcy>
            <failureToPay>
                <applicable>true</applicable>
            </failureToPay>
            <restructuring>
                <applicable>true</applicable>
            </restructuring>
        </creditEvents>
    </protectionTerms>
</creditDefaultSwap>
```

---

## 3. クレジットイベントと ISDA 定義
- **Credit Events（信用事由）**: `Bankruptcy`（破産）, `Failure to Pay`（支払不履行）, `Restructuring`（リストラ / 債務再編）等。
- **Obligation / Deliverable Obligation**: 対象債務 / 現物決済対象債務要件 (`Bond`, `Loan`, `PariPassu` 等)。

---

## 4. 関連 Wiki ページ
- [Shared Foundation](../common/shared-foundation.md)
- [Overview](../overview.md)
- [Index](../index.md)
