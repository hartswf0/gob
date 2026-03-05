#!/usr/bin/env python3
"""Parse WORLD-TEXT-DOUBLE.MD chat export into normalized prompt/response entries.

Outputs:
  - WORLD-TEXT-DOUBLE.parsed.json
  - WORLD-TEXT-DOUBLE.canonical-source.md
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


START_RE = re.compile(
    r"\{+\s*#\s*From\s+Imagetext\s+to\s+Worldtext:\s+Generative\s+AI\s+as\s+Operative\s+Ekphrasis",
    re.IGNORECASE,
)
END_RE = re.compile(r"STANDING\s+RESERVE\s*}*", re.IGNORECASE)
PROMPT_ROLE = "Prompt"
RESPONSE_ROLE = "Response"


@dataclass
class ExtractedPrompt:
    original: str
    base_block: Optional[str]
    base_norm: Optional[str]
    payload: str


@dataclass
class Pair:
    conv_index: int
    pair_index: int
    global_index: int
    prompt_msg_index: Optional[int]
    response_msg_index: Optional[int]
    prompt_text: str
    response_text: str
    metadata: Dict[str, Any]


def split_json_stream(raw: str) -> List[str]:
    """Split concatenated top-level JSON objects from a plain text stream."""
    chunks: List[str] = []
    start: Optional[int] = None
    depth = 0
    in_string = False
    escape = False

    for i, ch in enumerate(raw):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue

        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
            continue

        if ch == "}":
            if depth == 0:
                continue
            depth -= 1
            if depth == 0 and start is not None:
                chunks.append(raw[start : i + 1])
                start = None

    return chunks


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).lower()


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text or ""))


def response_thought_seconds(text: str) -> Optional[int]:
    m = re.match(r"\s*Thought\s+for\s+(\d+)s", text or "", flags=re.IGNORECASE)
    if not m:
        return None
    return int(m.group(1))


def extract_prompt_parts(prompt: str) -> ExtractedPrompt:
    prompt = prompt or ""
    start_match = START_RE.search(prompt)
    if not start_match:
        return ExtractedPrompt(
            original=prompt,
            base_block=None,
            base_norm=None,
            payload=prompt.strip(),
        )

    start = start_match.start()
    tail = prompt[start:]
    end_match = END_RE.search(tail)

    if end_match:
        end = start + end_match.end()
    else:
        # Fallback if terminator is missing in any entry.
        marker = re.search(r"\n\s{0,8}You\s+are\b", tail, flags=re.IGNORECASE)
        if marker:
            end = start + marker.start()
        else:
            end = len(prompt)

    base_block = prompt[start:end].strip()
    payload = (prompt[:start] + prompt[end:]).strip()

    return ExtractedPrompt(
        original=prompt,
        base_block=base_block,
        base_norm=normalize_text(base_block) if base_block else None,
        payload=payload,
    )


def pair_messages(messages: List[Dict[str, Any]]) -> Iterable[Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[int], Optional[int]]]:
    pending_prompt: Optional[Tuple[Dict[str, Any], int]] = None

    for idx, msg in enumerate(messages):
        role = msg.get("role")
        if role == PROMPT_ROLE:
            if pending_prompt is not None:
                prev_prompt, prev_idx = pending_prompt
                yield prev_prompt, None, prev_idx, None
            pending_prompt = (msg, idx)
            continue

        if role == RESPONSE_ROLE:
            if pending_prompt is None:
                yield None, msg, None, idx
            else:
                prompt_msg, pidx = pending_prompt
                yield prompt_msg, msg, pidx, idx
                pending_prompt = None

    if pending_prompt is not None:
        prompt_msg, pidx = pending_prompt
        yield prompt_msg, None, pidx, None


def parse_stream(raw: str) -> Dict[str, Any]:
    chunk_strings = split_json_stream(raw)
    conversations: List[Dict[str, Any]] = []
    pairs: List[Pair] = []

    for conv_i, chunk in enumerate(chunk_strings, start=1):
        try:
            obj = json.loads(chunk)
        except json.JSONDecodeError:
            continue

        metadata = obj.get("metadata", {}) if isinstance(obj, dict) else {}
        messages = obj.get("messages", []) if isinstance(obj, dict) else []
        if not isinstance(messages, list):
            messages = []

        prompt_count = sum(1 for m in messages if isinstance(m, dict) and m.get("role") == PROMPT_ROLE)
        response_count = sum(1 for m in messages if isinstance(m, dict) and m.get("role") == RESPONSE_ROLE)

        conversations.append(
            {
                "conversation_index": conv_i,
                "title": metadata.get("title"),
                "link": metadata.get("link"),
                "created": (metadata.get("dates") or {}).get("created"),
                "updated": (metadata.get("dates") or {}).get("updated"),
                "exported": (metadata.get("dates") or {}).get("exported"),
                "message_count": len(messages),
                "prompt_count": prompt_count,
                "response_count": response_count,
            }
        )

        pair_i = 0
        for prompt_msg, response_msg, prompt_idx, response_idx in pair_messages(messages):
            pair_i += 1
            pairs.append(
                Pair(
                    conv_index=conv_i,
                    pair_index=pair_i,
                    global_index=len(pairs) + 1,
                    prompt_msg_index=prompt_idx,
                    response_msg_index=response_idx,
                    prompt_text=(prompt_msg or {}).get("say", "") if isinstance(prompt_msg, dict) else "",
                    response_text=(response_msg or {}).get("say", "") if isinstance(response_msg, dict) else "",
                    metadata=metadata,
                )
            )

    extracted_prompts: List[ExtractedPrompt] = [extract_prompt_parts(p.prompt_text) for p in pairs]
    base_norm_counter = Counter(
        ep.base_norm
        for ep in extracted_prompts
        if ep.base_norm and len(ep.base_norm) > 200
    )

    canonical_norm: Optional[str] = None
    canonical_count = 0
    if base_norm_counter:
        canonical_norm, canonical_count = max(
            base_norm_counter.items(),
            key=lambda item: (item[1], len(item[0])),
        )

    canonical_text = ""
    if canonical_norm:
        for ep in extracted_prompts:
            if ep.base_norm == canonical_norm and ep.base_block:
                canonical_text = ep.base_block
                break

    entries: List[Dict[str, Any]] = []

    for pair, ep in zip(pairs, extracted_prompts):
        has_base = bool(ep.base_block)
        base_kind = "none"
        if has_base and ep.base_norm == canonical_norm:
            base_kind = "canonical"
        elif has_base:
            base_kind = "variant"

        response_text = pair.response_text or ""
        prompt_payload = ep.payload.strip() if ep.payload else ""

        entry = {
            "id": f"{pair.global_index:03d}",
            "global_index": pair.global_index,
            "conversation_index": pair.conv_index,
            "pair_index": pair.pair_index,
            "title": pair.metadata.get("title"),
            "link": pair.metadata.get("link"),
            "dates": pair.metadata.get("dates", {}),
            "prompt_message_index": pair.prompt_msg_index,
            "response_message_index": pair.response_msg_index,
            "prompt": {
                "raw": pair.prompt_text,
                "payload": prompt_payload,
                "base_kind": base_kind,
                "base_block": ep.base_block,
                "word_count_raw": word_count(pair.prompt_text),
                "word_count_payload": word_count(prompt_payload),
                "is_followup": has_base is False,
            },
            "response": {
                "raw": response_text,
                "word_count": word_count(response_text),
                "thought_seconds": response_thought_seconds(response_text),
                "preview": response_text[:280].strip(),
            },
        }
        entries.append(entry)

    stats = {
        "conversation_count": len(conversations),
        "entry_count": len(entries),
        "canonical_base_occurrences": canonical_count,
        "entries_with_any_base": sum(1 for e in entries if e["prompt"]["base_kind"] in {"canonical", "variant"}),
        "followup_only_entries": sum(1 for e in entries if e["prompt"]["is_followup"]),
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "conversations": conversations,
        "canonical_base": {
            "norm": canonical_norm,
            "occurrences": canonical_count,
            "text": canonical_text,
            "word_count": word_count(canonical_text),
        },
        "stats": stats,
        "entries": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse WORLD-TEXT-DOUBLE.MD into normalized JSON entries.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("WORLD-TEXT-DOUBLE.MD"),
        help="Input raw file (default: WORLD-TEXT-DOUBLE.MD)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("WORLD-TEXT-DOUBLE.parsed.json"),
        help="Output parsed JSON file",
    )
    parser.add_argument(
        "--canonical-output",
        type=Path,
        default=Path("WORLD-TEXT-DOUBLE.canonical-source.md"),
        help="Output canonical source markdown",
    )

    args = parser.parse_args()

    raw = args.input.read_text(encoding="utf-8")
    parsed = parse_stream(raw)

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
        f"{stats.get('conversation_count', 0)} conversations, "
        f"{stats.get('entry_count', 0)} entries, "
        f"{stats.get('canonical_base_occurrences', 0)} canonical-base matches."
    )


if __name__ == "__main__":
    main()
