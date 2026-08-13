#!/usr/bin/env python3
"""FpML 5.12 XSD Schema Query & Inspection CLI Tool.

Enables instant, accurate navigation and inspection of FpML Confirmation View schemas:
1. Search & inspect complexType / simpleType definitions and inheritance (extension base)
2. Locate element definitions, substitutionGroups, and product types
3. Query enumeration values (e.g. FloatingRateIndex, DayCountFraction, BusinessDayConvention)
4. Find all members of a substitutionGroup (e.g. substitutionGroup="product")
5. Full-text search across documentation and type names

Standard Library only - Python 3.10+ compatible.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

XSD_NS = {"xsd": "http://www.w3.org/2001/XMLSchema"}


@dataclass
class ElementInfo:
    name: str
    type: Optional[str]
    substitution_group: Optional[str]
    file: str
    line: Optional[int]
    documentation: Optional[str] = None


@dataclass
class TypeInfo:
    name: str
    kind: str  # "complexType" or "simpleType"
    base_type: Optional[str]
    file: str
    line: Optional[int]
    documentation: Optional[str]
    elements: List[Dict[str, Any]]
    attributes: List[Dict[str, Any]]
    enums: List[str]


class XSDIndex:
    def __init__(self, confirmation_dir: Path):
        self.confirmation_dir = confirmation_dir.resolve()
        self.elements: Dict[str, List[ElementInfo]] = {}
        self.types: Dict[str, List[TypeInfo]] = {}
        self.substitution_groups: Dict[str, List[ElementInfo]] = {}
        self._parsed = False

    def build_index(self):
        if self._parsed:
            return

        xsd_files = list(self.confirmation_dir.glob("*.xsd"))
        if not xsd_files:
            print(f"Warning: No XSD files found in {self.confirmation_dir}", file=sys.stderr)
            return

        for xsd_file in xsd_files:
            self._parse_file(xsd_file)

        self._parsed = True

    def _parse_file(self, file_path: Path):
        rel_file = file_path.name
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except Exception as e:
            print(f"Error parsing {rel_file}: {e}", file=sys.stderr)
            return

        # Map line numbers by scanning text lines
        lines = file_path.read_text(encoding="utf-8").splitlines()

        def find_line_num(tag_name: str, attr_name: str, value: str) -> Optional[int]:
            pattern = re.compile(rf'<{tag_name}[^>]*\b{attr_name}\s*=\s*["\']{re.escape(value)}["\']')
            for idx, line in enumerate(lines, start=1):
                if pattern.search(line):
                    return idx
            return None

        # 1. Parse top-level elements
        for elem in root.findall("xsd:element", XSD_NS):
            name = elem.get("name")
            if not name:
                continue
            elem_type = elem.get("type")
            sub_group = elem.get("substitutionGroup")
            doc = self._extract_doc(elem)
            line = find_line_num("xsd:element", "name", name)

            info = ElementInfo(
                name=name,
                type=elem_type,
                substitution_group=sub_group,
                file=rel_file,
                line=line,
                documentation=doc,
            )
            self.elements.setdefault(name.lower(), []).append(info)

            if sub_group:
                sub_clean = sub_group.split(":")[-1]
                self.substitution_groups.setdefault(sub_clean.lower(), []).append(info)

        # 2. Parse complexTypes
        for ct in root.findall("xsd:complexType", XSD_NS):
            name = ct.get("name")
            if not name:
                continue
            doc = self._extract_doc(ct)
            line = find_line_num("xsd:complexType", "name", name)

            # Check extension base
            base_type = None
            ext = ct.find(".//xsd:extension", XSD_NS)
            if ext is not None:
                base_type = ext.get("base")

            # Extract direct child elements
            child_elems = []
            for child in ct.findall(".//xsd:element", XSD_NS):
                c_name = child.get("name") or child.get("ref")
                c_type = child.get("type")
                c_min = child.get("minOccurs", "1")
                c_max = child.get("maxOccurs", "1")
                if c_name:
                    child_elems.append({
                        "name": c_name,
                        "type": c_type,
                        "minOccurs": c_min,
                        "maxOccurs": c_max,
                        "is_ref": bool(child.get("ref")),
                    })

            # Extract attributes
            attributes = []
            for attr in ct.findall(".//xsd:attribute", XSD_NS):
                a_name = attr.get("name") or attr.get("ref")
                a_type = attr.get("type")
                a_use = attr.get("use", "optional")
                if a_name:
                    attributes.append({
                        "name": a_name,
                        "type": a_type,
                        "use": a_use,
                    })

            t_info = TypeInfo(
                name=name,
                kind="complexType",
                base_type=base_type,
                file=rel_file,
                line=line,
                documentation=doc,
                elements=child_elems,
                attributes=attributes,
                enums=[],
            )
            self.types.setdefault(name.lower(), []).append(t_info)

        # 3. Parse simpleTypes (Enums)
        for st in root.findall("xsd:simpleType", XSD_NS):
            name = st.get("name")
            if not name:
                continue
            doc = self._extract_doc(st)
            line = find_line_num("xsd:simpleType", "name", name)

            base_type = None
            rest = st.find("xsd:restriction", XSD_NS)
            enums = []
            if rest is not None:
                base_type = rest.get("base")
                for enum_elem in rest.findall("xsd:enumeration", XSD_NS):
                    val = enum_elem.get("value")
                    if val:
                        enums.append(val)

            t_info = TypeInfo(
                name=name,
                kind="simpleType",
                base_type=base_type,
                file=rel_file,
                line=line,
                documentation=doc,
                elements=[],
                attributes=[],
                enums=enums,
            )
            self.types.setdefault(name.lower(), []).append(t_info)

    @staticmethod
    def _extract_doc(node: ET.Element) -> Optional[str]:
        doc_elem = node.find(".//xsd:annotation/xsd:documentation", XSD_NS)
        if doc_elem is not None and doc_elem.text:
            return re.sub(r"\s+", " ", doc_elem.text).strip()
        return None

    def query_element(self, name: str) -> List[ElementInfo]:
        self.build_index()
        return self.elements.get(name.lower(), [])

    def query_type(self, name: str) -> List[TypeInfo]:
        self.build_index()
        results = self.types.get(name.lower(), [])
        if not results and not name.lower().endswith("enum"):
            results = self.types.get((name + "enum").lower(), [])
        return results

    def query_substitution_group(self, group_name: str) -> List[ElementInfo]:
        self.build_index()
        clean = group_name.split(":")[-1].lower()
        return self.substitution_groups.get(clean, [])

    def search(self, pattern: str) -> Dict[str, Any]:
        self.build_index()
        regex = re.compile(pattern, re.IGNORECASE)
        matching_elements = []
        for elems in self.elements.values():
            for e in elems:
                if regex.search(e.name) or (e.documentation and regex.search(e.documentation)):
                    matching_elements.append(e)

        matching_types = []
        for t_list in self.types.values():
            for t in t_list:
                if regex.search(t.name) or (t.documentation and regex.search(t.documentation)):
                    matching_types.append(t)

        return {
            "elements": matching_elements,
            "types": matching_types,
        }


def print_element_info(elems: List[ElementInfo]):
    if not elems:
        print("No matching element definition found.")
        return
    for e in elems:
        loc = f"{e.file}:{e.line}" if e.line else e.file
        print(f"Element: <{e.name}>")
        print(f"  Defined in:         confirmation/{loc}")
        print(f"  Type:               {e.type or '(anonymous / inline)'}")
        if e.substitution_group:
            print(f"  Substitution Group: {e.substitution_group}")
        if e.documentation:
            print(f"  Documentation:      {e.documentation}")
        print()


def print_type_info(types: List[TypeInfo]):
    if not types:
        print("No matching type definition found.")
        return
    for t in types:
        loc = f"{t.file}:{t.line}" if t.line else t.file
        print(f"{t.kind}: {t.name}")
        print(f"  Defined in:    confirmation/{loc}")
        if t.base_type:
            print(f"  Extends Base:  {t.base_type}")
        if t.documentation:
            print(f"  Documentation: {t.documentation}")

        if t.enums:
            print(f"  Enumeration Values ({len(t.enums)} total):")
            for enum_val in t.enums[:30]:
                print(f"    - {enum_val}")
            if len(t.enums) > 30:
                print(f"    ... and {len(t.enums) - 30} more (use --json for full list)")

        if t.elements:
            print(f"  Child Elements ({len(t.elements)}):")
            for elem in t.elements:
                ref_mark = " (ref)" if elem["is_ref"] else ""
                cardinality = f"[{elem['minOccurs']}..{elem['maxOccurs']}]"
                elem_type = f": {elem['type']}" if elem["type"] else ""
                print(f"    - <{elem['name']}>{elem_type} {cardinality}{ref_mark}")

        if t.attributes:
            print(f"  Attributes ({len(t.attributes)}):")
            for attr in t.attributes:
                print(f"    - @{attr['name']} ({attr['type'] or 'string'}, {attr['use']})")
        print()


def main():
    parser = argparse.ArgumentParser(description="Query FpML 5.12 XSD schemas.")
    parser.add_argument(
        "--confirmation-dir",
        "-d",
        default="confirmation",
        help="Path to confirmation directory containing XSDs",
    )
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to execute")

    # Command: element <name>
    p_elem = subparsers.add_parser("element", help="Inspect an XSD element definition")
    p_elem.add_argument("name", help="Name of the element (e.g. swap, trade, requestConfirmation)")

    # Command: type <name>
    p_type = subparsers.add_parser("type", help="Inspect an XSD complexType or simpleType")
    p_type.add_argument("name", help="Name of the type (e.g. Swap, InterestRateStream, Party)")

    # Command: enum <name>
    p_enum = subparsers.add_parser("enum", help="List enumeration values for a simpleType")
    p_enum.add_argument("name", help="Name of the enum type (e.g. FloatingRateIndex, BusinessDayConvention)")

    # Command: sub <group_name>
    p_sub = subparsers.add_parser("sub", help="List all elements in a substitutionGroup")
    p_sub.add_argument("group_name", help="Name of substitutionGroup (e.g. product, event)")

    # Command: search <pattern>
    p_search = subparsers.add_parser("search", help="Search types and elements by regex pattern")
    p_search.add_argument("pattern", help="Search regex pattern")

    args = parser.parse_args()

    conf_path = Path(args.confirmation_dir).resolve()
    idx = XSDIndex(conf_path)

    if args.command == "element":
        results = idx.query_element(args.name)
        if args.json:
            print(json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False))
        else:
            print_element_info(results)

    elif args.command == "type":
        results = idx.query_type(args.name)
        if args.json:
            print(json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False))
        else:
            print_type_info(results)

    elif args.command == "enum":
        results = idx.query_type(args.name)
        enum_types = [t for t in results if t.enums]
        if args.json:
            print(json.dumps([asdict(r) for r in enum_types], indent=2, ensure_ascii=False))
        else:
            if not enum_types:
                print(f"No enumeration found for type '{args.name}'")
            else:
                print_type_info(enum_types)

    elif args.command == "sub":
        results = idx.query_substitution_group(args.group_name)
        if args.json:
            print(json.dumps([asdict(r) for r in results], indent=2, ensure_ascii=False))
        else:
            print(f"Elements in substitutionGroup='{args.group_name}' ({len(results)} found):")
            for e in results:
                loc = f"{e.file}:{e.line}" if e.line else e.file
                print(f"  - <{e.name}> (type={e.type or 'inline'}, defined in confirmation/{loc})")

    elif args.command == "search":
        results = idx.search(args.pattern)
        if args.json:
            print(json.dumps({
                "elements": [asdict(e) for e in results["elements"]],
                "types": [asdict(t) for t in results["types"]],
            }, indent=2, ensure_ascii=False))
        else:
            print(f"Search Results for '{args.pattern}':")
            print(f"\n--- Matching Elements ({len(results['elements'])}) ---")
            for e in results["elements"][:20]:
                print(f"  <{e.name}> -> confirmation/{e.file}:{e.line}")
            print(f"\n--- Matching Types ({len(results['types'])}) ---")
            for t in results["types"][:20]:
                print(f"  {t.kind} {t.name} (base={t.base_type or 'None'}) -> confirmation/{t.file}:{t.line}")


if __name__ == "__main__":
    main()
