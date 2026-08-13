#!/usr/bin/env python3
"""Wiki Linter and Terminology Auditor for FpML LLM Wiki.

Performs static validation of:
1. Relative link integrity (broken links, missing files, invalid anchors, absolute URI misuse)
2. wiki/index.md coverage (unindexed orphan pages and dead index entries)
3. wiki/log.md format validation (## [YYYY-MM-DD] action | summary)
4. Japanese OTC market terminology audit (forbidden machine translations)
5. YAML Frontmatter check (warnings for entity pages)

Standard Library only - Python 3.10+ compatible.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import urllib.parse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

# Forbidden Japanese terminology mappings (Regex Pattern -> Preferred Term)
FORBIDDEN_TERMS: Dict[str, str] = {
    r"一夜物金利": "オーバーナイト金利 / 翌日物金利",
    r"一夜物(?!.*(?:NG|禁止|直訳|誤用|表記))": "翌日物 / オーバーナイト (TONA等)",
    r"(?<![a-zA-Z0-9_])脚(?![a-zA-Z0-9_])": "レグ (固定レグ, 変動レグ, USDレグ等)",
    r"USD脚": "USDレグ",
    r"JPY脚": "JPYレグ",
    r"固定脚": "固定レグ",
    r"変動脚": "変動レグ",
    r"契約改済": "ノベーション / 契約更改",
    r"コンフィメーション": "コンファーメーション / 約定確認",
    r"誘導体": "デリバティブ",
    r"元金交換": "元本交換",
    r"市場評価スワップ": "mtMスワップ / 元本リセット型通貨スワップ",
}

LOG_ENTRY_PATTERN = re.compile(
    r"^##\s+\[(\d{4}-\d{2}-\d{2})\]\s+([a-zA-Z0-9_-]+)\s*\|\s*(.+)$"
)

MARKDOWN_LINK_PATTERN = re.compile(
    r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)"
)


@dataclass
class LintIssue:
    severity: str  # "ERROR", "WARNING"
    category: str  # "LINK", "INDEX", "LOG", "TERMINOLOGY", "FRONTMATTER"
    file: str
    line: Optional[int]
    message: str
    suggestion: Optional[str] = None


class WikiLinter:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.wiki_dir = (self.workspace_root / "wiki").resolve()
        self.issues: List[LintIssue] = []

    def log_issue(
        self,
        severity: str,
        category: str,
        file_path: Path,
        message: str,
        line: Optional[int] = None,
        suggestion: Optional[str] = None,
    ):
        try:
            rel_file = str(file_path.relative_to(self.workspace_root)).replace("\\", "/")
        except ValueError:
            rel_file = str(file_path).replace("\\", "/")
        self.issues.append(
            LintIssue(
                severity=severity,
                category=category,
                file=rel_file,
                line=line,
                message=message,
                suggestion=suggestion,
            )
        )

    def check_terminology(self, file_path: Path, lines: List[str]):
        """Detect forbidden machine translation words in Markdown files."""
        # Skip log.md historical entries (which may mention past corrections)
        if file_path.name == "log.md":
            return

        in_code_block = False
        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue

            # Skip table headers or explicit documentation of forbidden terms
            if any(k in line for k in ["Forbidden Machine Translations", "NG 表現", "× 一夜物金利", "forbidden", "直訳"]):
                continue

            for pattern, preferred in FORBIDDEN_TERMS.items():
                match = re.search(pattern, line)
                if match:
                    # Check if line explicitly mentions NG/Forbidden in context
                    if any(k in line for k in ["NG", "禁止", "直訳", "誤用"]):
                        continue
                    self.log_issue(
                        severity="ERROR",
                        category="TERMINOLOGY",
                        file_path=file_path,
                        line=idx,
                        message=f"Forbidden translation term found: '{match.group(0)}'",
                        suggestion=f"Use standard Japanese market terminology: '{preferred}'",
                    )

    def check_links_and_anchors(self, file_path: Path, content: str, lines: List[str]):
        """Validate all relative markdown links and anchor targets."""
        for idx, line in enumerate(lines, start=1):
            for match in MARKDOWN_LINK_PATTERN.finditer(line):
                link_text, link_target = match.group(1), match.group(2).strip()

                # Ignore external HTTP/HTTPS links, mailto
                if link_target.startswith(("http://", "https://", "mailto:")):
                    continue

                # Flag file:/// absolute links as bad practice (should use relative markdown links)
                if link_target.startswith("file:///"):
                    # Parse local file target
                    file_url_path = link_target[len("file:///"):]
                    # Handle optional line anchor
                    anchor = None
                    if "#" in file_url_path:
                        file_url_path, anchor = file_url_path.split("#", 1)
                    file_url_path = urllib.parse.unquote(file_url_path)
                    
                    target_file = Path(file_url_path).resolve()
                    if not target_file.exists():
                        self.log_issue(
                            severity="ERROR",
                            category="LINK",
                            file_path=file_path,
                            line=idx,
                            message=f"Broken absolute link: '{link_target}' does not exist",
                            suggestion=f"Convert to relative markdown link (e.g. '../../confirmation/...')",
                        )
                    else:
                        self.log_issue(
                            severity="WARNING",
                            category="LINK",
                            file_path=file_path,
                            line=idx,
                            message=f"Avoid absolute 'file:///' link: '{link_target}'",
                            suggestion=f"Use relative link like '../../{target_file.relative_to(self.workspace_root).as_posix()}'",
                        )
                    continue

                # Parse relative path and anchor
                if "#" in link_target:
                    target_path_str, anchor = link_target.split("#", 1)
                else:
                    target_path_str, anchor = link_target, None

                target_path_str = urllib.parse.unquote(target_path_str)

                # If target path is empty, it refers to an anchor in the current file
                if not target_path_str:
                    target_file = file_path
                else:
                    target_file = (file_path.parent / target_path_str).resolve()

                if not target_file.exists():
                    self.log_issue(
                        severity="ERROR",
                        category="LINK",
                        file_path=file_path,
                        line=idx,
                        message=f"Broken link: Target path '{link_target}' does not exist (resolved to '{target_file}')",
                    )
                    continue

                # If anchor is present and target is markdown, verify heading anchor
                if anchor and target_file.suffix.lower() == ".md":
                    self._check_anchor(file_path, idx, target_file, anchor, link_target)

    def _check_anchor(
        self,
        source_file: Path,
        line_num: int,
        target_file: Path,
        anchor: str,
        full_link: str,
    ):
        try:
            target_content = target_file.read_text(encoding="utf-8")
        except Exception:
            return

        # Extract markdown headings (# Heading)
        headings = re.findall(r"^#+\s+(.+)$", target_content, flags=re.MULTILINE)
        slugs = [self._slugify(h) for h in headings]

        if anchor not in slugs:
            self.log_issue(
                severity="WARNING",
                category="LINK",
                file_path=source_file,
                line=line_num,
                message=f"Possible broken anchor '#{anchor}' in link '{full_link}'",
                suggestion=f"Available heading slugs: {', '.join(slugs[:5])}...",
            )

    @staticmethod
    def _slugify(text: str) -> str:
        text = text.strip().lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[\s_]+", "-", text)
        return text

    def check_frontmatter(self, file_path: Path, content: str):
        """Verify YAML frontmatter for structural wiki pages."""
        rel_to_wiki = file_path.relative_to(self.wiki_dir)
        if len(rel_to_wiki.parts) <= 1:
            return  # skip root files like index.md, log.md, overview.md

        if not content.startswith("---"):
            self.log_issue(
                severity="WARNING",
                category="FRONTMATTER",
                file_path=file_path,
                message="Missing YAML frontmatter (--- ... ---)",
                suggestion="Add tags, schemas, and updated date frontmatter block.",
            )
            return

        end_idx = content.find("---", 3)
        if end_idx == -1:
            self.log_issue(
                severity="ERROR",
                category="FRONTMATTER",
                file_path=file_path,
                message="Unclosed YAML frontmatter",
            )

    def check_index_coverage(self, wiki_files: List[Path]):
        """Ensure all wiki pages are registered in wiki/index.md and vice versa."""
        index_path = self.wiki_dir / "index.md"
        if not index_path.exists():
            self.log_issue(
                severity="ERROR",
                category="INDEX",
                file_path=self.wiki_dir,
                message="wiki/index.md is missing!",
            )
            return

        index_content = index_path.read_text(encoding="utf-8")
        indexed_links = set(re.findall(r"\[([^\]]+)\]\(([^)]+)\)", index_content))

        # Resolve indexed files
        indexed_files: Set[Path] = set()
        for _, link in indexed_links:
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            path_part = link.split("#")[0]
            if path_part:
                target = (index_path.parent / path_part).resolve()
                if target.exists() and target.is_file():
                    indexed_files.add(target)

        # Compare with existing markdown files under wiki/
        for wf in wiki_files:
            if wf.name in ("index.md", "log.md"):
                continue
            if wf not in indexed_files:
                self.log_issue(
                    severity="WARNING",
                    category="INDEX",
                    file_path=wf,
                    message="Wiki page is not linked in wiki/index.md (orphan page)",
                    suggestion=f"Add entry in wiki/index.md pointing to ./{wf.relative_to(self.wiki_dir).as_posix()}",
                )

    def check_log_format(self):
        """Validate entries in wiki/log.md."""
        log_path = self.wiki_dir / "log.md"
        if not log_path.exists():
            self.log_issue(
                severity="ERROR",
                category="LOG",
                file_path=self.wiki_dir,
                message="wiki/log.md is missing!",
            )
            return

        lines = log_path.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, start=1):
            if line.startswith("## "):
                match = LOG_ENTRY_PATTERN.match(line)
                if not match:
                    self.log_issue(
                        severity="ERROR",
                        category="LOG",
                        file_path=log_path,
                        line=idx,
                        message=f"Invalid log entry format: '{line}'",
                        suggestion="Format must match: '## [YYYY-MM-DD] <action> | <summary>'",
                    )

    def run(self) -> List[LintIssue]:
        if not self.wiki_dir.exists():
            print(f"Error: Wiki directory not found at {self.wiki_dir}", file=sys.stderr)
            return []

        wiki_files = list(self.wiki_dir.rglob("*.md"))

        # 1. Lint each markdown file
        for md_file in wiki_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                lines = content.splitlines()
            except Exception as e:
                self.log_issue(
                    severity="ERROR",
                    category="FILE",
                    file_path=md_file,
                    message=f"Failed to read file: {e}",
                )
                continue

            self.check_terminology(md_file, lines)
            self.check_links_and_anchors(md_file, content, lines)
            self.check_frontmatter(md_file, content)

        # 2. Check index coverage
        self.check_index_coverage(wiki_files)

        # 3. Check log format
        self.check_log_format()

        return self.issues


def main():
    parser = argparse.ArgumentParser(description="Lint FpML LLM Wiki repository.")
    parser.add_argument(
        "--workspace",
        "-w",
        default=".",
        help="Workspace root path (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output findings in JSON format",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Only display errors, omit warnings",
    )
    args = parser.parse_args()

    workspace_path = Path(args.workspace).resolve()
    linter = WikiLinter(workspace_path)
    issues = linter.run()

    if args.errors_only:
        issues = [i for i in issues if i.severity == "ERROR"]

    if args.json:
        print(json.dumps([asdict(i) for i in issues], indent=2, ensure_ascii=False))
        sys.exit(1 if any(i.severity == "ERROR" for i in issues) else 0)

    errors = [i for i in issues if i.severity == "ERROR"]
    warnings = [i for i in issues if i.severity == "WARNING"]

    print(f"\n{'='*70}")
    print(f"  FpML Wiki Linter & Terminology Audit Report")
    print(f"  Workspace: {workspace_path}")
    print(f"  Issues Found: {len(errors)} Errors, {len(warnings)} Warnings")
    print(f"{'='*70}\n")

    for issue in issues:
        color_tag = "[ERROR]" if issue.severity == "ERROR" else "[WARN]"
        loc = f"{issue.file}:{issue.line}" if issue.line else issue.file
        print(f"{color_tag} [{issue.category}] {loc}")
        print(f"  Message:    {issue.message}")
        if issue.suggestion:
            print(f"  Suggestion: {issue.suggestion}")
        print()

    if errors:
        print(f"FAILED: Found {len(errors)} error(s). Please fix them before committing.")
        sys.exit(1)
    else:
        print(f"SUCCESS: No blocking errors found ({len(warnings)} warning(s)).")
        sys.exit(0)


if __name__ == "__main__":
    main()
