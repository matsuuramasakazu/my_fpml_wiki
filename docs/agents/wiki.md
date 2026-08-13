# LLM Wiki Agent Protocol

This document defines the rules and workflows for operating as an LLM Wiki maintainer within this FpML repository, based on the Karpathy LLM Wiki pattern.

---

## 1. Architecture (Three Layers)

1. **Raw Sources (Immutable)**:
   - `confirmation/` directory (XSD schemas, sample XML files, test cases).
   - `codelist/` directory.
   - `fpml_xsd_catalog.md` (XSD schema index).
   - *Rule*: Never modify raw source files during Wiki maintenance unless explicitly instructed to update schemas/examples.

2. **The Wiki (`wiki/`)**:
   - A persistent, compounding knowledge base written in Markdown.
   - `wiki/index.md`: Content catalog listing every page with links and one-line summaries.
   - `wiki/log.md`: Reverse-chronological event log listing all Ingest, Query compounding, and Lint operations (`## [YYYY-MM-DD] action | summary`).
   - Structural subdirectories: `products/`, `processes/`, `architecture/`, `common/`, etc.

3. **The Schema (This Protocol, `CONTEXT.md`, `docs/adr/`, & `AGENTS.md`)**:
   - Instructions guiding how the LLM maintains cross-references, integrates new information, and keeps the Wiki healthy.

---

## 2. Core Workflows

### Ingest Workflow
When new FpML schemas, sample XMLs, or business documentation are added or requested to be ingested:
1. **Read & Extract**: Inspect source file(s) in `confirmation/` using `python scripts/xsd_query.py` or view tools.
2. **Synthesize & Map**: Identify relevant FpML complex types, ISDA definitions, asset classes, or message flows.
3. **Update Wiki Pages**: Create or edit topic/entity pages under the appropriate `wiki/` directory. Cross-link related pages using Markdown relative links.
4. **Update `wiki/index.md`**: Add new entries or update summaries across relevant sections.
5. **Log Entry**: Append a record to `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD] ingest | Added/updated topic description
   ```
6. **Lint Verification**: Execute `python scripts/wiki_lint.py` to confirm 0 errors.

### Query & Compound Workflow
When answering user queries about FpML structures, calculations, workflows, or architectures:
1. **Consult Wiki First**: Check `wiki/index.md` and relevant `wiki/` pages before re-analyzing raw XSDs from scratch.
2. **Query XSDs Accurately**: Use `python scripts/xsd_query.py` to verify exact schema lines, type definitions, and enumerations.
3. **Answer Query**: Provide a thorough, grounded answer referencing XSD line numbers, XML snippets, and Japanese OTC market practices.
4. **Compound Back (Multi-Page Synthesis)**: If the query yielded valuable analysis, comparison tables, or new syntheses:
   - **Do NOT dump everything into a single file** (e.g., placing all product, process, and architecture insights into one file under `architecture/`).
   - **Distribute knowledge into proper directories** (`products/`, `processes/`, `architecture/`, `common/`) following Section 3 rules.
   - **Establish Cross-Links**: Interlink the generated product, process, and architecture pages.
5. **Update Index & Log**: Update `wiki/index.md` and append a record to `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD] query | Summarized trade workflow for FX options
   ```
6. **Lint Verification**: Execute `python scripts/wiki_lint.py` to confirm 0 errors.

### Lint Workflow
Periodically health-check the Wiki using the automated harness tool:
1. Run `python scripts/wiki_lint.py` (or `/fpml-wiki-lint`).
2. Fix any reported broken relative links, missing files, or orphan pages lacking index entries.
3. Replace any detected forbidden machine translations with standard Japanese OTC derivative market terms.
4. Verify YAML frontmatters.
5. Log the linting pass in `wiki/log.md`:
   ```markdown
   ## [YYYY-MM-DD] lint | Fixed broken links and terminology compliance
   ```

---

## 3. Structural Categorization & Directory Rules

When adding or compounding knowledge, ALWAYS classify and place files according to their domain concern:

| Directory | Concern & Content Standard | Examples |
|---|---|---|
| **`wiki/products/`** | **Product & Contract Data Models**<br>Specific OTC derivative product structures, leg configurations, rate indices, FpML XML representations, and contract parameters. | `ird.md`, `xccy-swap.md`, `fx.md`, `credit.md` |
| **`wiki/processes/`** | **Business Processes & Life Cycle Events**<br>Front-to-back workflows, pricing calculations (NPV=0 Par pricing, margin adjustments), RFQ, trade capture, confirmation matching, rate fixing, clearing, and business events. | `business-processes.md`, `pricing-and-confirmation-flow.md` |
| **`wiki/architecture/`** | **System Architecture & DDD Bounded Contexts**<br>Domain-Driven Design (DDD) Bounded Contexts, microservice responsibilities, event-driven architectures, polyglot technology stack selection, bulkhead patterns, and non-functional requirements. | `pricing-bounded-contexts.md`, `root-elements.md` |
| **`wiki/common/`** | **Common Foundation & Shared Types**<br>Shared foundation schemas, Party definitions, Money, Day Count Fractions, and ISDA business day conventions. | `shared-foundation.md` |

> [!IMPORTANT]
> **Multi-Page Synthesis Rule**: Complex analyses involving a financial product, its business process, and its system architecture MUST produce or update corresponding pages across `products/`, `processes/`, and `architecture/`, interlinked via relative Markdown links.

---

## 4. Financial Practice & Domain Depth Principles

- **Avoid Surface-Level Summaries**:
   - Do not stop at basic dictionary definitions or generic architectural generalities.
   - Always ground explanations in **actual Japanese OTC derivative market practices** and **ISDA standards**.

---

## 5. Formatting & Language Guidelines

- **Relative Links Mandatory**: Use standard Markdown relative links (e.g., `./overview.md`, `../common/shared-foundation.md`, `../../confirmation/fpml-ird-5-12.xsd`) for all inter-file references and raw source file mentions. Do NOT use unlinked text, absolute paths, or `file:///` URLs.
- **Mandatory Live URL Verification**: External URLs (HTTP/HTTPS) presented to users or added to Wiki pages MUST be verified in the same turn via `read_url_content` (or similar fetch tools) to ensure HTTP 200 status and expected content before outputting. Never output unverified or dead 404 links.
- **YAML Frontmatter**: Include frontmatter on entity pages (`tags`, `schemas`, `updated`).
- **Japanese Terminology Standard**: Always use standard Japanese terminology commonly adopted by financial institutions and market participants in Japanese OTC derivative markets. Avoid literal or generic machine translations.
  
  | English Concept | Forbidden Machine Translations (NG) | Standard Japanese Market Terminology (OK) |
  |---|---|---|
  | **Overnight Rate** | × 一夜物金利 | ○ **オーバーナイト金利 / 翌日物金利** (TONA: 無担保コール翌日物) |
  | **Leg** (Stream) | × 脚 (USD脚, JPY脚) | ○ **レグ** (USDレグ, JPYレグ, 固定レグ, 変動レグ) |
  | **Novation** | × 契約改済 | ○ **ノベーション / 契約更改** |
  | **Confirmation** | × コンフィメーション | ○ **コンファーメーション / 約定確認** |
  | **Discrepancy** | × 不一致 | ○ **相違 (Discrepancy) / アンマッチ** |
  | **Derivative** | × 誘導体 | ○ **デリバティブ** |
