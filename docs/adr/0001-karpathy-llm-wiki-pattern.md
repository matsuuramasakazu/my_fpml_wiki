# ADR 0001: Adoption of the Karpathy LLM Wiki Pattern

## Status
Accepted

## Context
OTC デリバティブ取引および FpML (Financial Products Markup Language) の仕様は多岐にわたり、XSD スキーマの複雑性やプロダクト・業務フロー間の相互関係が非常に密接です。単発の質問応答で得られたドメイン知識（スキーマ構造、ISDA 定義とのマッピング、実務的な解釈、システム設計等）を会話セッションを越えて永続化し、相互参照可能な知識体系として蓄積していく必要があります。

## Decision
Andrej Karpathy 氏が提唱した「LLM Wiki パターン」を採用し、リポジトリを以下の 3 層構造で運用することを決定しました：

1. **Layer 1: Raw Sources (`confirmation/`, `codelist/`, `fpml_xsd_catalog.md`)**
   - イミュータブルな一次情報ソース（FpML 5.12 XSD スキーマおよび公式 XML サンプル）。
2. **Layer 2: Compounding Wiki (`wiki/`)**
   - LLM エージェントが継続的に保守・拡充する Markdown ナレッジベース。
   - `wiki/index.md`（カタログ）と `wiki/log.md`（履歴）を中核とし、`products/`, `processes/`, `architecture/`, `common/` に知識を構造化して分散配置する。
3. **Layer 3: Protocol & Agent Guidance (`docs/agents/`, `.agents/AGENTS.md`)**
   - エージェントが Wiki を保守・検証・拡充するための行動規範・運用プロトコル。

## Consequences
- **Positive**: 質問応答ごとに知識が Wiki に還元され、以降の回答精度・速度が複利的に向上する。
- **Positive**: 単一ファイルへの知識集中（モノリス化）を避け、関心の分離（プロダクト、プロセス、アーキテクチャ）が保たれる。
- **Negative / Operational Burden**: Wiki の健全性（リンク切れ、インデックス整合性、用語の一貫性）を保つための Linter や検証スクリプトの整備・定期実行が必要となる。
