# ADR 0003: Japanese OTC Derivatives Market Standard Terminology

## Status
Accepted

## Context
金融工学および OTC デリバティブの技術文書や LLM による解説において、英語の専門用語を直訳・機械翻訳すると、日本の金融機関・市場参加者の実務現場で用いられる標準的な語彙と乖離し、可読性と実用性が著しく損なわれます。

## Decision
エージェントの思考言語およびすべての成果物・Wiki 記述において、**東京 OTC デリバティブ市場で日常的に定着している日本語の金融実務標準用語**の採用を義務付け、機械翻訳表現を明示的に禁止します。

### 禁止語彙と採用標準語彙
- `Overnight Rate`: ×「一夜物金利」 → ○ **「オーバーナイト金利」「翌日物金利」**
- `Leg` / `Stream`: ×「脚」 → ○ **「レグ」**
- `Novation`: ×「契約改済」 → ○ **「ノベーション」「契約更改」**
- `Confirmation`: ×「コンフィメーション」 → ○ **「コンファーメーション」「約定確認」**
- `Discrepancy`: ×「不一致」 → ○ **「相違 (Discrepancy)」「アンマッチ」**
- `Derivative`: ×「誘導体」 → ○ **「デリバティブ」**

## Consequences
- **Positive**: 日本のフロントオフィス、クオンツ、ミドル・バックオフィス実務者が違和感なく活用できる専門的かつ高水準なナレッジベースが保たれる。
- **Positive**: 機械翻訳による誤訳や概念の混同を防止する。
- **Operational Requirement**: `scripts/wiki_lint.py` 等による NG 用語の静的監査を定期実行する。
