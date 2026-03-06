#!/usr/bin/env python3
"""Extract unique prompt templates from ASCLEPIUS-ROD.parsed.json.

Outputs:
  - ASCLEPIUS-ROD.templates.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from extract_worldtext_templates import compact, is_template_prompt, label_from_template, normalize, words


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract unique templates from parsed Asclepius entries.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("ASCLEPIUS-ROD.parsed.json"),
        help="Input parsed JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("ASCLEPIUS-ROD.templates.json"),
        help="Output templates JSON",
    )
    args = parser.parse_args()

    parsed = json.loads(args.input.read_text(encoding="utf-8"))
    entries = parsed.get("entries", [])

    groups: Dict[str, Dict[str, Any]] = {}
    source_map: Dict[str, List[str]] = defaultdict(list)

    for entry in entries:
        prompt = ((entry.get("prompt") or {}).get("payload") or "").strip()
        if not prompt:
            continue
        if prompt.upper() in {"CONTINUE", "NEXT", "FULL PAPER", "NEXT SECTION"}:
            continue
        if not is_template_prompt(prompt):
            continue

        norm = normalize(prompt)
        if not norm:
            continue

        entry_id = entry.get("id")
        source_map[norm].append(entry_id)

        if norm not in groups:
            groups[norm] = {
                "template": compact(prompt),
                "first_entry_id": entry_id,
                "first_title": entry.get("title"),
                "first_link": entry.get("link"),
            }

    templates: List[Dict[str, Any]] = []
    ranked = sorted(groups.items(), key=lambda kv: (len(source_map[kv[0]]), len(kv[0])), reverse=True)
    for i, (norm, data) in enumerate(ranked, start=1):
        template_id = f"T{i:03d}"
        text = data["template"]
        templates.append(
            {
                "template_id": template_id,
                "label": label_from_template(text, template_id),
                "template": text,
                "word_count": words(text),
                "char_count": len(text),
                "occurrences": len(source_map[norm]),
                "source_entry_ids": source_map[norm],
                "first_entry_id": data["first_entry_id"],
                "first_title": data["first_title"],
                "first_link": data["first_link"],
            }
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(args.input),
        "template_count": len(templates),
        "templates": templates,
    }

    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Extracted {len(templates)} templates -> {args.output}")


if __name__ == "__main__":
    main()
