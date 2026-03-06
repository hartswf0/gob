#!/usr/bin/env python3
"""Parse ASCLEPIUS-ROD.md into normalized prompt/response entries.

Outputs:
  - ASCLEPIUS-ROD.parsed.json
  - ASCLEPIUS-ROD.canonical-source.md
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from parse_world_text_double import parse_stream


MESSAGE_RE = re.compile(
    r'\{\s*"role"\s*:\s*"(?P<role>Prompt|Response)"\s*,\s*"say"\s*:\s*"(?P<say>(?:\\.|[^"\\])*)"\s*\}',
    re.DOTALL,
)


def _rx(raw: str, pattern: str) -> str:
    m = re.search(pattern, raw, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _decode_jsonish_string(value: str) -> str:
    if value is None:
        return ""
    try:
        return json.loads(f'"{value}"')
    except Exception:
        pass

    # Some exports include literal newlines inside quoted strings.
    fixed_newlines = value.replace("\r", "\\r").replace("\n", "\\n")
    try:
        return json.loads(f'"{fixed_newlines}"')
    except Exception:
        pass

    return (
        value.replace('\\"', '"')
        .replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t")
    )


def parse_loose_export(raw: str) -> dict:
    messages = []
    for m in MESSAGE_RE.finditer(raw):
        role = m.group("role")
        say = _decode_jsonish_string(m.group("say"))
        messages.append({"role": role, "say": say})

    if not messages:
        return {}

    metadata = {
        "title": _decode_jsonish_string(_rx(raw, r'"title"\s*:\s*"([^"]*)"')),
        "link": _decode_jsonish_string(_rx(raw, r'"link"\s*:\s*"([^"]*)"')),
        "dates": {
            "created": _decode_jsonish_string(_rx(raw, r'"created"\s*:\s*"([^"]*)"')),
            "updated": _decode_jsonish_string(_rx(raw, r'"updated"\s*:\s*"([^"]*)"')),
            "exported": _decode_jsonish_string(_rx(raw, r'"exported"\s*:\s*"([^"]*)"')),
        },
    }
    return {"metadata": metadata, "messages": messages}


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse ASCLEPIUS-ROD.MD into normalized JSON entries.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("ASCLEPIUS-ROD.md"),
        help="Input raw file (default: ASCLEPIUS-ROD.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ASCLEPIUS-ROD.parsed.json"),
        help="Output parsed JSON file",
    )
    parser.add_argument(
        "--canonical-output",
        type=Path,
        default=Path("ASCLEPIUS-ROD.canonical-source.md"),
        help="Output canonical source markdown",
    )
    parser.add_argument(
        "--fallback-input",
        type=Path,
        default=Path("ASCLEPIUS.MD"),
        help="Fallback input if --input is empty (default: ASCLEPIUS.MD)",
    )
    args = parser.parse_args()

    raw = args.input.read_text(encoding="utf-8")
    source_used = args.input
    if not raw.strip() and args.fallback_input.exists():
        alt = args.fallback_input.read_text(encoding="utf-8")
        if alt.strip():
            raw = alt
            source_used = args.fallback_input
    parsed = parse_stream(raw)

    # Fallback for exporter variants that are JSON-like but not strict JSON.
    if (parsed.get("stats") or {}).get("entry_count", 0) == 0:
        loose_obj = parse_loose_export(raw)
        if loose_obj:
            parsed = parse_stream(json.dumps(loose_obj, ensure_ascii=False))

    args.output.write_text(json.dumps(parsed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    canonical_text = parsed.get("canonical_base", {}).get("text", "")
    canonical_doc = "\n".join(
        [
            "# Canonical Source Block",
            "",
            f"- Generated: {parsed.get('generated_at')}",
            f"- Occurrences: {parsed.get('canonical_base', {}).get('occurrences', 0)}",
            "",
            canonical_text.strip(),
            "",
        ]
    )
    args.canonical_output.write_text(canonical_doc, encoding="utf-8")

    stats = parsed.get("stats", {})
    print(
        "Parsed "
        f"from {source_used}, "
        f"{stats.get('conversation_count', 0)} conversations, "
        f"{stats.get('entry_count', 0)} entries, "
        f"{stats.get('canonical_base_occurrences', 0)} canonical-base matches."
    )


if __name__ == "__main__":
    main()
