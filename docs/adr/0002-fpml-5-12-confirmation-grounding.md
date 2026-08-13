# ADR 0002: FpML 5.12 Confirmation View Scope and Grounding Protocol

## Status
Accepted

## Context
FpML には複数のビュー（Pre-trade, Confirmation, Reporting, Transparency, Recordkeeping）が存在し、それぞれカバーするメッセージやスキーマ構造が異なります。また、LLM が一般的な知識や記憶に基づいてスキーマ構造を回答すると、バージョンの相違やハルシネーションが発生するリスクがあります。

## Decision
1. 本リポジトリの対象スコープを **FpML 5.12 Confirmation View** に固定する。
2. エージェントの回答および Wiki への記述は、すべて `confirmation/` 配下の XSD スキーマおよび XML サンプルの実ファイル検証（Grounding）に基づくことを義務付ける（Mandatory Double-Check Protocol）。
3. 根拠として、必ず参照した XSD ファイル名および具体的な行番号・XML スニペットを明記する。

## Consequences
- **Positive**: バージョン混同やハルシネーションを完全に防止し、極めて信頼性の高い FpML ナレッジベースを維持できる。
- **Positive**: Confirmation View に特化することで、約定確認、ポストトレード処理、清算（Clearing）、ライフサイクルイベントの一貫した分析が可能になる。
- **Negative**: Pre-trade（RFQ等）や Transparency Reporting 固有の要素は対象外（または Confirmation View 内の共通型としてのみ扱う）となる。
