---
title: FpML 5.12 Confirmation View XML Document Root Elements
tags: [fpml, schema, root-elements, XML, confirmation-view, messaging]
updated: 2026-07-25
---

# FpML 5.12 Confirmation View - XML Document Root Elements 一覧と解説

FpML (Confirmation View 5.12) の XSD スキーマ群に定義されている主要な XML ドキュメントのルートエレメント（最上位要素）の一覧と、それぞれの実務的な用途・役割の解説です。

FpML におけるルートエレメントは、大別して以下の **4つのカテゴリー** に分類されます。

---

## 1. データ・評価保持コンテナ (Data & Valuation Documents)

ビジネス処理のメッセージ伝送ヘッダー（`header`）を持たず、取引データや評価結果の永続化・交換・ストレージ保管に用いられるルートエレメントです。

| ルートエレメント名 | 定義 XSD | 型 (Type) | 概要と実務用途 |
| --- | --- | --- | --- |
| `dataDocument` | [`fpml-main-5-12.xsd`](../../confirmation/fpml-main-5-12.xsd) | `DataDocument` | 取引データ（`trade`）、ポートフォリオ、取引当事者（`party`）等の静的データを格納する標準コンテナ。メッセージングを伴わないポジション保管やデータ連携で使用。 |
| `valuationDocument` | [`fpml-main-5-12.xsd`](../../confirmation/fpml-main-5-12.xsd) | `ValuationDocument` | 取引データに加え、マーケットデータ、時価評価（Valuation）、感応度（Sensitivities / Greeks）などのリスク評価情報を保持・交換するためのルートコンテナ。 |

---

## 2. コンファーメーション & 清算メッセージ (Confirmation & Clearing Messages)

約定後のコンファーメーション（約定照合・確認）および CCP（中央清算機関）への清算申請プロセスで送受信されるルートエレメントです。

| ルートエレメント名 | 定義 XSD | 概要と実務用途 |
| --- | --- | --- |
| `requestConfirmation` | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) | **コンファーメーション請求/送付**: 取引相手（カウンターパーティ）に対し、確定経済条件を含むコンファーメーションの確認・合意を求めるルートメッセージ。 |
| `confirmationAgreed` | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) | **コンファーメーション合意通知**: 提示されたコンファーメーション内容（経済条件・当事者情報）に完全に一致・合意したことを返信するメッセージ。 |
| `confirmationDisputed` / `confirmationRejected` | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) | **コンファーメーション相違・拒絶通知**: 照合（Matching）において条件の相違（アンマッチ）が検出された場合や、取引を拒絶するメッセージ。 |
| `confirmationStatus` | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) | **コンファーメーションステータス通知**: 照合プロセスの進行状況（Mismatched, Matched 等）を報告するメッセージ。 |
| `requestClearing` | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) / [`fpml-clearing-processes-5-12.xsd`](../../confirmation/fpml-clearing-processes-5-12.xsd) | **清算申請**: 取引を CCP（中央清算機関）に持ち込んで清算（Clearing）させるための申請ルートメッセージ。 |
| `clearingConfirmed` | [`fpml-clearing-processes-5-12.xsd`](../../confirmation/fpml-clearing-processes-5-12.xsd) | **清算完了通知**: CCP から当事者に対し、取引の清算・ノベーションが完了したことを通知するメッセージ。 |
| `clearingRefused` | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-clearing-processes-5-12.xsd) / [`fpml-clearing-processes-5-12.xsd`](../../confirmation/fpml-clearing-processes-5-12.xsd) | **清算拒絶通知**: CCP が適格性欠如やリスク制限等により清算申請を拒絶したことを通知するメッセージ。 |
| `clearingStatus` | [`fpml-clearing-processes-5-12.xsd`](../../confirmation/fpml-clearing-processes-5-12.xsd) | **清算ステータス報告**: CCP での清算待ち・審査中のステータスを報告するメッセージ。 |

---

## 3. 取引ライフサイクルイベントメッセージ (Business Event Messages)

約定後の変更、権利行使、中途解約、ノベーションなど、取引のライフサイクルで発生する各種イベントを伝達するルートエレメントです。

| ルートエレメント名                                              | 定義 XSD                                                                                            | 概要と実務用途                                                               |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `executionNotification` / `executionAdvice`            | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) | **約定成立通知**: ブローカーや電子取引プラットフォームから当事者へ取引約定（Execution）を通知するメッセージ。        |
| `tradeChangeAdvice`                                    | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) | **取引変更・訂正通知 (Amendment / Correction)**: 既約定取引の誤記訂正や条件変更を通知・記録するメッセージ。 |
| `requestConsent` / `consentGranted` / `consentRefused` | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) | **承認要求 / 承認 / 拒絶**: 中途解約や条件変更の前に相手方の事前同意（Consent）を求める一連のメッセージ。        |
| `optionExercise` / `optionExerciseNotification`        | [`fpml-business-events-5-12.xsd`](../../confirmation/fpml-business-events-5-12.xsd) 等             | **オプション権利行使**: オプション取引の権利行使（Option Exercise）を通知するメッセージ。               |
| `optionExpiry` / `optionExpiryNotification`            | [`fpml-business-events-5-12.xsd`](../../confirmation/fpml-business-events-5-12.xsd) 等             | **オプション消滅・失効**: オプションが未行使のまま満期を迎えて消滅（Expiry）したことを通知するメッセージ。           |
| `de-clearing` / `de-clearingNotification`              | [`fpml-clearing-processes-5-12.xsd`](../../confirmation/fpml-clearing-processes-5-12.xsd)         | **清算取消（De-clearing）**: CCP 清算対象から取引を除外・取消するイベントメッセージ。                 |
| `maturityNotification`                                 | [`fpml-confirmation-processes-5-12.xsd`](../../confirmation/fpml-confirmation-processes-5-12.xsd) | **満期到来通知**: 取引が最終満期日（Maturity Date）に達したことを通知するメッセージ。                  |

---

## 4. システム & インフラ共通メッセージ (Common Messaging Infrastructure)

メッセージ処理の制御、応答、エラー通知に用いられるルートエレメントです（[`fpml-msg-5-12.xsd`](../../confirmation/fpml-msg-5-12.xsd) などで定義）。

| ルートエレメント名 | 定義 XSD | 概要と実務用途 |
| --- | --- | --- |
| `serviceNotification` | [`fpml-msg-5-12.xsd`](../../confirmation/fpml-msg-5-12.xsd) | **サービスステータス通知**: 電子プラットフォームやミドルウェアの稼働状況・サービス通知。 |
| `requestEventStatus` / `eventStatusResponse` | [`fpml-msg-5-12.xsd`](../../confirmation/fpml-msg-5-12.xsd) | **イベント状態照会 / 応答**: 送信済み非同期メッセージの処理進捗を問い合わせるメッセージ。 |
| `messageRejected` / `eventStatusException` | [`fpml-msg-5-12.xsd`](../../confirmation/fpml-msg-5-12.xsd) | **メッセージ拒絶・例外通知**: スキーマ不整合や構文エラー等によりメッセージが受け入れられなかった場合の例外応答。 |

---

## 5. 関連 Wiki ページ

- [FpML 5.12 Overview](../overview.md)
- [Business Processes](../processes/business-processes.md)
- [Shared Foundation](../common/shared-foundation.md)
- [Index](../index.md)
