#!/usr/bin/env python3
"""Build section-level comparison papers from parsed_master_analyst/index.json.

Outputs (under parsed_master_analyst/papers):
  - non_obvious_insights_paper.md
  - tensions_contradictions_paper.md
  - so_what_paper.md
  - whats_missing_paper.md
  - README.md
  - all_sections.tsv
  - <section>.tsv for each target section
"""

from __future__ import annotations

import csv
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "index.json"
OUT_DIR = BASE_DIR / "papers"

SECTION_CONFIG: Sequence[Tuple[str, str]] = (
    ("NON_OBVIOUS_INSIGHTS", "non_obvious_insights"),
    ("TENSIONS_CONTRADICTIONS", "tensions_contradictions"),
    ("SO_WHAT", "so_what"),
    ("WHATS_MISSING", "whats_missing"),
)

SECTION_SLUG_MAP: Dict[str, str] = dict(SECTION_CONFIG)
SECTION_CODE_MAP: Dict[str, str] = {
    "NON_OBVIOUS_INSIGHTS": "N",
    "TENSIONS_CONTRADICTIONS": "T",
    "SO_WHAT": "S",
    "WHATS_MISSING": "M",
}

SECTION_FIELD_ORDER: Dict[str, Sequence[str]] = {
    "SO_WHAT": ("Core_Implication", "Why_It_Matters"),
    "WHATS_MISSING": ("Missing_Question", "Critical_Assumption", "Next_Inquiry"),
}

SORT_NORMALIZER = re.compile(r"[^a-z0-9]+")
FIELD_INLINE_TAG = re.compile(r'<field\s+name="([^"]+)">\s*(.*?)\s*</field>', flags=re.DOTALL)
ITEM_INLINE_TAG = re.compile(r'<item\s+name="([^"]+)">\s*(.*?)\s*</item>', flags=re.DOTALL)
FIELD_MARKER_TAG = re.compile(r'<field\s+name="([^"]+)"\s*/>')
ITEM_MARKER_TAG = re.compile(r'<item\s+name="([^"]+)"\s*/>')
GENERIC_BLOCK_TAG = re.compile(r"<([A-Za-z_][A-Za-z0-9_]*)>\s*(.*?)\s*</\1>", flags=re.DOTALL)
GENERIC_TAG = re.compile(r"</?[^>]+>")
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]{2,}")
STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "almost",
    "also",
    "among",
    "because",
    "being",
    "between",
    "could",
    "did",
    "does",
    "doing",
    "during",
    "each",
    "every",
    "from",
    "further",
    "have",
    "having",
    "into",
    "just",
    "like",
    "more",
    "most",
    "much",
    "must",
    "over",
    "same",
    "should",
    "some",
    "such",
    "than",
    "that",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "under",
    "very",
    "what",
    "when",
    "where",
    "which",
    "while",
    "with",
    "would",
    "your",
}


@dataclass
class Statement:
    section: str
    index: int
    video_id: str
    source_url: str
    canonical_url: str
    response_file: str
    label: str
    text: str


def humanize(token: str) -> str:
    return token.replace("_", " ").strip()


def normalize_text(raw: object) -> str:
    text = html.unescape(str(raw))
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.strip()
    if not text:
        return ""
    text = GENERIC_TAG.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_structured_text(raw: str) -> List[Tuple[str, str]]:
    text = html.unescape(raw).strip()
    if not text:
        return []

    # <field name="X">...</field>
    pairs = [(humanize(name), normalize_text(body)) for name, body in FIELD_INLINE_TAG.findall(text)]
    if pairs:
        return [(label, body) for label, body in pairs if body]

    # <item name="X">...</item>
    pairs = [(humanize(name), normalize_text(body)) for name, body in ITEM_INLINE_TAG.findall(text)]
    if pairs:
        return [(label, body) for label, body in pairs if body]

    # <field name="X"/> marker style blocks
    if FIELD_MARKER_TAG.search(text):
        out: List[Tuple[str, str]] = []
        last = 0
        current_label = "Statement"
        for match in FIELD_MARKER_TAG.finditer(text):
            chunk = normalize_text(text[last : match.start()])
            if chunk:
                out.append((current_label, chunk))
            current_label = humanize(match.group(1))
            last = match.end()
        tail = normalize_text(text[last:])
        if tail:
            out.append((current_label, tail))
        return out

    # <item name="X"/> marker style blocks
    if ITEM_MARKER_TAG.search(text):
        out = []
        last = 0
        current_label = "Statement"
        for match in ITEM_MARKER_TAG.finditer(text):
            chunk = normalize_text(text[last : match.start()])
            if chunk:
                out.append((current_label, chunk))
            current_label = humanize(match.group(1))
            last = match.end()
        tail = normalize_text(text[last:])
        if tail:
            out.append((current_label, tail))
        return out

    # Generic <Tag>...</Tag> blocks
    pairs = [(humanize(tag), normalize_text(body)) for tag, body in GENERIC_BLOCK_TAG.findall(text)]
    if pairs:
        return [(label, body) for label, body in pairs if body]

    return []


def normalize_pairs(section: str, value: object) -> List[Tuple[str, str]]:
    if value is None:
        return []

    if isinstance(value, list):
        out: List[Tuple[str, str]] = []
        for i, item in enumerate(value, start=1):
            if isinstance(item, str):
                structured = parse_structured_text(item)
                if structured:
                    for sublabel, subtext in structured:
                        label = sublabel if sublabel.lower() != "statement" else f"Item {i}"
                        if subtext:
                            out.append((label, subtext))
                    continue
            label = f"Item {i}"
            text = normalize_text(item)
            if text:
                out.append((label, text))
        return out

    if isinstance(value, dict):
        out = []
        preferred = list(SECTION_FIELD_ORDER.get(section, ()))
        keys = [key for key in preferred if key in value]
        keys.extend(sorted(key for key in value if key not in preferred))
        for key in keys:
            key_label = humanize(key)
            raw = value[key]
            if isinstance(raw, list):
                for i, item in enumerate(raw, start=1):
                    text = normalize_text(item)
                    if text:
                        out.append((f"{key_label} {i}", text))
                continue
            if isinstance(raw, dict):
                for subkey in sorted(raw):
                    text = normalize_text(raw[subkey])
                    if text:
                        out.append((f"{key_label} | {humanize(subkey)}", text))
                continue
            if isinstance(raw, str):
                structured = parse_structured_text(raw)
                if structured:
                    for sublabel, subtext in structured:
                        if sublabel.lower() == "statement" or sublabel.lower() == key_label.lower():
                            label = key_label
                        else:
                            label = f"{key_label} | {sublabel}"
                        if subtext:
                            out.append((label, subtext))
                    continue
            text = normalize_text(raw)
            if text:
                out.append((key_label, text))
        return out

    if isinstance(value, str):
        structured = parse_structured_text(value)
        if structured:
            return structured
        text = normalize_text(value)
        return [("Statement", text)] if text else []

    text = normalize_text(value)
    return [("Statement", text)] if text else []


def extract_statements(entries: Iterable[dict], section: str) -> List[Statement]:
    out: List[Statement] = []
    for entry in entries:
        section_value = entry.get("response_sections", {}).get(section)
        pairs = normalize_pairs(section, section_value)
        for label, text in pairs:
            out.append(
                Statement(
                    section=section,
                    index=int(entry.get("index", 0)),
                    video_id=(entry.get("video_id") or "N/A"),
                    source_url=(entry.get("source_url") or ""),
                    canonical_url=(entry.get("canonical_url") or ""),
                    response_file=(entry.get("response_file") or ""),
                    label=label,
                    text=text,
                )
            )
    return out


def statement_sort_key(statement: Statement) -> Tuple[str, int, str]:
    normalized = SORT_NORMALIZER.sub(" ", statement.text.lower()).strip()
    return normalized, statement.index, statement.label.lower()


def tokenize_text(text: str) -> List[str]:
    tokens = TOKEN_RE.findall(text.lower())
    return [tok for tok in tokens if tok not in STOPWORDS and not tok.isdigit()]


def section_rank(section: str) -> int:
    order = [name for name, _slug in SECTION_CONFIG]
    try:
        return order.index(section)
    except ValueError:
        return len(order)


def bibtex_token(value: str, fallback: str = "na", max_len: int = 28) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "", (value or "").lower())
    if not cleaned:
        cleaned = fallback
    return cleaned[:max_len]


def bibtex_escape(value: str) -> str:
    text = (value or "").replace("\\", "\\\\")
    text = text.replace("{", "(").replace("}", ")")
    return text


def build_bibtex_entry(
    bibtex_id: str,
    section: str,
    label: str,
    zettel_id: str,
    year: str,
    url: str,
    note_meta: str,
) -> str:
    lines = [
        f"@misc{{{bibtex_id},",
        "  author = {Geometry of Bias},",
        f"  title = {{{bibtex_escape(section)} | {bibtex_escape(label)} | {bibtex_escape(zettel_id)}}},",
        f"  year = {{{year}}},",
        "  howpublished = {Verification Premium Corpus Zettelkasten Note},",
    ]
    if url:
        lines.append(f"  url = {{{bibtex_escape(url)}}},")
    lines.append(f"  note = {{{bibtex_escape(note_meta)}}}")
    lines.append("}")
    return "\n".join(lines)


def build_zettelkasten_notes(statements: Sequence[Statement], generated_at: str) -> Dict[str, object]:
    ordered = sorted(
        statements,
        key=lambda s: (
            s.index,
            section_rank(s.section),
            s.label.lower(),
            statement_sort_key(s),
        ),
    )

    per_entry_counter: Dict[Tuple[str, int], int] = defaultdict(int)
    notes: List[Dict[str, object]] = []
    year = generated_at[:4] if generated_at[:4].isdigit() else "2026"

    for statement in ordered:
        key = (statement.section, statement.index)
        per_entry_counter[key] += 1
        ordinal = per_entry_counter[key]
        section_code = SECTION_CODE_MAP.get(statement.section, "X")
        section_slug = SECTION_SLUG_MAP.get(statement.section, statement.section.lower())
        zettel_id = f"{section_code}.{statement.index:03d}.{ordinal:02d}"
        note_id = f"zk-{section_code.lower()}-{statement.index:03d}-{ordinal:02d}"
        video_token = bibtex_token(statement.video_id or "na")
        bibtex_id = f"bias{year}_{video_token}_{section_code.lower()}{statement.index:03d}{ordinal:02d}"
        primary_url = statement.canonical_url or statement.source_url
        note_meta = (
            f"note_id={note_id}; video_id={statement.video_id}; "
            f"entry={statement.index:03d}; response_file={statement.response_file}"
        )
        bibtex_entry = build_bibtex_entry(
            bibtex_id=bibtex_id,
            section=statement.section,
            label=statement.label,
            zettel_id=zettel_id,
            year=year,
            url=primary_url,
            note_meta=note_meta,
        )

        tokens = tokenize_text(statement.text)
        note = {
            "id": note_id,
            "zettel_id": zettel_id,
            "bibtex_id": bibtex_id,
            "bibtex_entry": bibtex_entry,
            "section": statement.section,
            "section_slug": section_slug,
            "section_code": section_code,
            "entry_index": statement.index,
            "video_id": statement.video_id,
            "label": statement.label,
            "text": statement.text,
            "source_url": statement.source_url,
            "canonical_url": statement.canonical_url,
            "response_file": statement.response_file,
            "_tokens": tokens,
            "keywords": [],
            "synthetic_links": [],
        }
        notes.append(note)

    token_freq: Counter = Counter()
    token_sets: List[set] = []
    for note in notes:
        token_set = set(note["_tokens"])
        token_sets.append(token_set)
        token_freq.update(token_set)

    # Keywords: prioritize lower-frequency tokens (more specific) and longer terms.
    for note in notes:
        ranked = sorted(
            set(note["_tokens"]),
            key=lambda tok: (token_freq[tok], -len(tok), tok),
        )
        note["keywords"] = ranked[:8]

    # Synthetic links: lexical overlap + structural boosts.
    for i, note in enumerate(notes):
        scores: List[Tuple[float, int, List[str]]] = []
        a_tokens = token_sets[i]
        for j, other in enumerate(notes):
            if i == j:
                continue
            b_tokens = token_sets[j]
            overlap = a_tokens & b_tokens
            same_entry = note["entry_index"] == other["entry_index"]
            if len(overlap) < 2 and not same_entry:
                continue

            union = a_tokens | b_tokens
            base = (len(overlap) / len(union)) if union else 0.0
            if note["section"] == other["section"]:
                base += 0.05
            if same_entry:
                base += 0.10
            if base < 0.10:
                continue

            shared_terms = sorted(
                overlap,
                key=lambda tok: (token_freq[tok], -len(tok), tok),
            )[:5]
            scores.append((base, j, shared_terms))

        if not scores:
            # Always provide local navigation fallback inside the same entry.
            for j, other in enumerate(notes):
                if i == j:
                    continue
                if note["entry_index"] == other["entry_index"]:
                    scores.append((0.05, j, []))

        scores.sort(
            key=lambda item: (
                -item[0],
                notes[item[1]]["entry_index"],
                notes[item[1]]["zettel_id"],
            )
        )

        top = scores[:8]
        note["synthetic_links"] = [
            {
                "target_id": notes[idx]["id"],
                "target_zettel_id": notes[idx]["zettel_id"],
                "score": round(score, 4),
                "shared_terms": terms,
            }
            for score, idx, terms in top
        ]

    section_counts = {
        section: sum(1 for note in notes if note["section"] == section)
        for section, _slug in SECTION_CONFIG
    }

    for note in notes:
        note.pop("_tokens", None)

    return {
        "generated_at": generated_at,
        "source_index_json": str(INDEX_PATH),
        "total_notes": len(notes),
        "section_counts": section_counts,
        "notes": notes,
    }


def write_tsv(path: Path, rows: Sequence[Statement], include_section: bool) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        base_header = [
            "index",
            "video_id",
            "label",
            "text",
            "source_url",
            "canonical_url",
            "response_file",
        ]
        if include_section:
            writer.writerow(["section", *base_header])
        else:
            writer.writerow(base_header)

        for row in rows:
            base_data = [
                f"{row.index:03d}",
                row.video_id,
                row.label,
                row.text,
                row.source_url,
                row.canonical_url,
                row.response_file,
            ]
            if include_section:
                writer.writerow([row.section, *base_data])
            else:
                writer.writerow(base_data)


def render_section_paper(
    section: str,
    slug: str,
    entries: Sequence[dict],
    statements: Sequence[Statement],
    generated_at: str,
) -> str:
    title = humanize(section).upper()
    lines: List[str] = []
    lines.append(f"# {title} Paper")
    lines.append("")
    lines.append(f"- Generated: {generated_at}")
    lines.append(f"- Source: `{INDEX_PATH.name}`")
    lines.append(f"- Entries covered: {len(entries)}")
    lines.append(f"- Statements extracted: {len(statements)}")
    lines.append("")
    lines.append("## Quick Compare Table")
    lines.append("")
    lines.append("| Index | Video ID | Statements |")
    lines.append("|---:|---|---:|")

    by_index: Dict[int, List[Statement]] = defaultdict(list)
    for statement in statements:
        by_index[statement.index].append(statement)

    for entry in entries:
        idx = int(entry.get("index", 0))
        lines.append(f"| {idx:03d} | {entry.get('video_id') or 'N/A'} | {len(by_index[idx])} |")

    lines.append("")
    lines.append("## Chronological View (By Entry)")
    lines.append("")
    for entry in entries:
        idx = int(entry.get("index", 0))
        vid = entry.get("video_id") or "N/A"
        lines.append(f"### {idx:03d} | {vid}")
        lines.append("")
        lines.append(f"- Source: {entry.get('source_url') or ''}")
        lines.append(f"- Canonical: {entry.get('canonical_url') or ''}")
        lines.append(f"- Response File: `{entry.get('response_file') or ''}`")
        lines.append("")
        grouped = by_index[idx]
        if not grouped:
            lines.append("- (No statements found)")
            lines.append("")
            continue
        for i, statement in enumerate(grouped, start=1):
            lines.append(f"{i}. **{statement.label}:** {statement.text}")
        lines.append("")

    lines.append("## Sorted Statement Bank (A-Z)")
    lines.append("")
    for i, statement in enumerate(sorted(statements, key=statement_sort_key), start=1):
        lines.append(f"{i}. {statement.text}")
        lines.append(
            f"   Ref: #{statement.index:03d} | `{statement.video_id}` | {statement.label} | `{statement.response_file}`"
        )
    lines.append("")
    lines.append(f"_TSV export: `{slug}.tsv`_")
    lines.append("")
    return "\n".join(lines)


def render_readme(generated_at: str, totals: Dict[str, int], all_count: int) -> str:
    lines = [
        "# Section Papers",
        "",
        f"- Generated: {generated_at}",
        f"- Source: `{INDEX_PATH}`",
        f"- Total statements across all sections: {all_count}",
        "",
        "## Papers",
        "",
        "- `non_obvious_insights_paper.md`",
        "- `tensions_contradictions_paper.md`",
        "- `so_what_paper.md`",
        "- `whats_missing_paper.md`",
        "",
        "## Zettelkasten JSON",
        "",
        "- `zettelkasten_notes.json`",
        "- ID format: `zk-<section>-<entry>-<ordinal>` (example: `zk-n-001-01`)",
        "- Includes: `bibtex_id` + `bibtex_entry` + `keywords` + `synthetic_links` for navigation",
        "",
        "## Regenerate",
        "",
        "```bash",
        "python3 build_section_papers.py",
        "```",
        "",
        "## TSV Exports",
        "",
        "- `all_sections.tsv`",
        "- `non_obvious_insights.tsv`",
        "- `tensions_contradictions.tsv`",
        "- `so_what.tsv`",
        "- `whats_missing.tsv`",
        "",
        "## Statement Counts",
        "",
        "| Section | Statements |",
        "|---|---:|",
        f"| NON_OBVIOUS_INSIGHTS | {totals['NON_OBVIOUS_INSIGHTS']} |",
        f"| TENSIONS_CONTRADICTIONS | {totals['TENSIONS_CONTRADICTIONS']} |",
        f"| SO_WHAT | {totals['SO_WHAT']} |",
        f"| WHATS_MISSING | {totals['WHATS_MISSING']} |",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    entries = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    entries = sorted(entries, key=lambda item: int(item.get("index", 0)))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    totals: Dict[str, int] = {}
    all_statements: List[Statement] = []

    for section, slug in SECTION_CONFIG:
        statements = extract_statements(entries, section)
        totals[section] = len(statements)
        all_statements.extend(statements)

        paper_path = OUT_DIR / f"{slug}_paper.md"
        paper_text = render_section_paper(section, slug, entries, statements, generated_at)
        paper_path.write_text(paper_text + "\n", encoding="utf-8")

        tsv_path = OUT_DIR / f"{slug}.tsv"
        write_tsv(tsv_path, statements, include_section=False)

    write_tsv(OUT_DIR / "all_sections.tsv", all_statements, include_section=True)
    zettelkasten = build_zettelkasten_notes(all_statements, generated_at)
    (OUT_DIR / "zettelkasten_notes.json").write_text(
        json.dumps(zettelkasten, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    readme = render_readme(generated_at, totals, len(all_statements))
    (OUT_DIR / "README.md").write_text(readme + "\n", encoding="utf-8")

    print(f"Wrote outputs to {OUT_DIR}")
    for section, slug in SECTION_CONFIG:
        print(f"- {slug}_paper.md ({totals[section]} statements)")
    print(f"- all_sections.tsv ({len(all_statements)} statements)")
    print(f"- zettelkasten_notes.json ({zettelkasten['total_notes']} notes)")


if __name__ == "__main__":
    main()
