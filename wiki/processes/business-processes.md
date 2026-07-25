---
title: Business Processes & Messaging Knowledge
tags: [fpml, processes, confirmation, clearing, business-events, messaging]
updated: 2026-07-25
---

# 業務プロセス & メッセージング (Business Processes)

## 1. 概要と該当スキーマ

FpML 5.12 Confirmation view は、単なる取引経済条件の定義だけでなく、約定（Trade Execution）からコンファーメーション（Trade Confirmation）、中途解約（Termination）、取引変更（Amendment）、権利行使（Option Exercise）、中央清算（Clearing）に至る取引ライフサイクルイベントを表現するメッセージ構造を提供します。

- **主スキーマ**:
  - [`confirmation/fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) - Confirmation 業務プロセス
  - [`confirmation/fpml-clearing-processes-5-12.xsd`](../../confirmation/fpml-clearing-processes-5-12.xsd) - Clearing (中央清算/CCP) メッセージ
  - [`confirmation/fpml-business-events-5-12.xsd`](../../confirmation/fpml-business-events-5-12.xsd) - 取引ライフサイクルイベント
  - [`confirmation/fpml-msg-5-12.xsd`](../../confirmation/fpml-msg-5-12.xsd) - ヘッダー・メッセージ伝送型
- **サンプル XML ディレクトリ**: [`confirmation/business-processes/`](../../confirmation/business-processes)

---

## 2. 主要なビジネスプロセスモデル

### 1. Trade Confirmation (約定確認 / コンファーメーション)
- `requestConfirmation`: コンファーメーション照会・請求
- `confirmationAgreed`: 約定確認合意
- `confirmationRejected`: アンマッチ・条件相違による拒絶

### 2. Clearing (中央清算機関/CCP への清算申請)
- `requestClearing`: 清算申請
- `clearingConfirmed`: CCP 清算完了通知
- `clearingRefused`: 清算拒絶

### 3. Business Events (取引ライフサイクルイベント)
- `tradeChangeAdvice`: 取引内容の変更・訂正 (Amendment / Correction)
- `optionExercise`: オプション権利行使 (Option Exercise)
- `termination`: 中途解約 (Termination)
- `novation`: ノベーション (Novation / 契約更改)

---

## 3. メッセージヘッダー構造

全メッセージに共通する `header` 要素：

```xml
<header>
    <messageId messageIdScheme="http://www.bank.com/mid">MSG-2026-0725-001</messageId>
    <sentBy>BANKA_LEI</sentBy>
    <sendTo>BANKB_LEI</sendTo>
    <creationTimestamp>2026-07-25T12:00:00Z</creationTimestamp>
</header>
```

---

## 4. 関連 Wiki ページ
- [Overview](../overview.md)
- [Shared Foundation](../common/shared-foundation.md)
- [Index](../index.md)
