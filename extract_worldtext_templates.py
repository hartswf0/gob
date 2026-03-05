#!/usr/bin/env python3
"""Extract unique prompt templates (without shared payload source text) from WORLD-TEXT-DOUBLE.parsed.json.

Outputs:
  - WORLD-TEXT-DOUBLE.templates.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def words(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def compact(text: str) -> str:
    lines = [(ln.rstrip()) for ln in (text or "").strip().splitlines()]
    out: List[str] = []
    blanks = 0
    for line in lines:
        if not line.strip():
            blanks += 1
            if blanks > 1:
                continue
            out.append("")
            continue
        blanks = 0
        out.append(line)
    return "\n".join(out).strip()


def is_template_prompt(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    wc = words(t)
    if wc < 20:
        return False
    first_line = next((ln.strip() for ln in t.splitlines() if ln.strip()), "")
    if first_line:
        first_wc = words(first_line)
        if re.fullmatch(r"[A-Z0-9 _:\\-]+", first_line) and first_wc <= 12:
            return False

    if re.search(r"<prompt\b|<phase\b|<domain\b|<section\b", t, flags=re.IGNORECASE):
        return True
    if re.search(r"^\s*You\s+are\s+", t, flags=re.IGNORECASE):
        return wc >= 30
    # fallback: long-form instruction block
    return wc >= 80


def label_from_template(text: str, fallback_id: str) -> str:
    if not text:
        return fallback_id

    m = re.search(r"<prompt\s+name=\"([^\"]+)\"", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()

    first_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if first_lines:
        first = first_lines[0]
        m2 = re.match(r"You\s+are\s+(?:a|an|the)\s+(.+?)\.?$", first, flags=re.IGNORECASE)
        if m2:
            candidate = m2.group(1).strip()
            candidate = re.sub(r"[^A-Za-z0-9\s_-]+", "", candidate)
            candidate = re.sub(r"\s+", " ", candidate)
            return candidate[:80]
        return first[:80]

    return fallback_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract unique templates from parsed worldtext entries.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("WORLD-TEXT-DOUBLE.parsed.json"),
        help="Input parsed JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("WORLD-TEXT-DOUBLE.templates.json"),
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
    for i, (norm, data) in enumerate(sorted(groups.items(), key=lambda kv: (len(source_map[kv[0]]), len(kv[0])), reverse=True), start=1):
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
