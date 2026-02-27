#!/usr/bin/env python3
"""Parse raw Gemini export for MASTER_ANALYST_PROMPT runs.

Outputs:
  FARM-TO-SCREEN/parsed_master_analyst/
    - index.json
    - index.csv
    - index.md
    - responses/<nnn>-<video_id>.md
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "raw.md"
OUT_DIR = ROOT / "parsed_master_analyst"
RESPONSES_DIR = OUT_DIR / "responses"

TURN_MARKER = re.compile(r"^(You said|Gemini said)\s*$")
URL_RE = re.compile(r"https?://[^\s<>)\]]+", re.IGNORECASE)


@dataclass
class Turn:
    speaker: str
    start_line: int
    end_line: int
    content: str


def normalize_space(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.strip().splitlines())


def extract_urls(text: str) -> List[str]:
    seen = set()
    out: List[str] = []
    for raw in URL_RE.findall(text):
        clean = raw.rstrip(".,;:)]}\"")
        key = clean.lower()
        if key not in seen:
            seen.add(key)
            out.append(clean)
    return out


def extract_video_id(url: str) -> Optional[str]:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")

    if host in {"youtu.be", "www.youtu.be"}:
        return path.split("/")[0] if path else None

    if "youtube.com" in host:
        if path == "watch":
            v = parse_qs(parsed.query).get("v", [])
            return v[0] if v else None
        if path.startswith("live/"):
            return path.split("/", 1)[1] or None
        if path.startswith("shorts/"):
            return path.split("/", 1)[1] or None
        # Sometimes exported links may be /embed/<id>
        if path.startswith("embed/"):
            return path.split("/", 1)[1] or None

    return None


def canonical_watch_url(video_id: Optional[str]) -> Optional[str]:
    if not video_id:
        return None
    return f"https://www.youtube.com/watch?v={video_id}"


def parse_sections(response: str) -> Dict[str, object]:
    sections: Dict[str, object] = {}
    for name, body in re.findall(r'<section\s+name="([^"]+)">\s*(.*?)\s*</section>', response, flags=re.DOTALL):
        items = [normalize_space(x) for x in re.findall(r"<item>\s*(.*?)\s*</item>", body, flags=re.DOTALL)]
        fields = {
            key: normalize_space(val)
            for key, val in re.findall(r'<field\s+name="([^"]+)">\s*(.*?)\s*</field>', body, flags=re.DOTALL)
        }
        if fields:
            sections[name] = fields
        elif items:
            sections[name] = items
        else:
            sections[name] = normalize_space(body)
    return sections


def parse_turns(text: str) -> List[Turn]:
    turns: List[Turn] = []
    current_speaker: Optional[str] = None
    current_start = 0
    buffer: List[str] = []

    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        m = TURN_MARKER.match(line)
        if m:
            if current_speaker is not None:
                turns.append(
                    Turn(
                        speaker=current_speaker,
                        start_line=current_start,
                        end_line=idx - 1,
                        content="\n".join(buffer).strip("\n"),
                    )
                )
            current_speaker = "user" if m.group(1) == "You said" else "gemini"
            current_start = idx + 1
            buffer = []
        else:
            if current_speaker is not None:
                buffer.append(line)

    if current_speaker is not None:
        turns.append(
            Turn(
                speaker=current_speaker,
                start_line=current_start,
                end_line=len(lines),
                content="\n".join(buffer).strip("\n"),
            )
        )

    return turns


def main() -> None:
    text = INPUT.read_text(encoding="utf-8")
    turns = parse_turns(text)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

    entries: List[Dict[str, object]] = []

    for i, turn in enumerate(turns):
        if turn.speaker != "user":
            continue
        if "MASTER_ANALYST_PROMPT" not in turn.content:
            continue

        user_urls = extract_urls(turn.content)
        video_urls = [u for u in user_urls if "youtu.be" in u.lower() or "youtube.com" in u.lower()]
        source_url = video_urls[0] if video_urls else (user_urls[0] if user_urls else None)
        video_id = extract_video_id(source_url) if source_url else None
        canonical = canonical_watch_url(video_id)

        # Next Gemini turn is treated as response for this prompt.
        response_turn = None
        for j in range(i + 1, len(turns)):
            if turns[j].speaker == "gemini":
                response_turn = turns[j]
                break
            if turns[j].speaker == "user":
                break

        response_text = response_turn.content if response_turn else ""
        response_urls = extract_urls(response_text)
        response_sections = parse_sections(response_text)

        idx = len(entries) + 1
        safe_id = video_id or f"no-video-{idx:03d}"
        response_file = f"responses/{idx:03d}-{safe_id}.md"

        response_md = [
            f"# MASTER_ANALYST Response {idx:03d}",
            "",
            f"- Source URL: {source_url or 'N/A'}",
            f"- Video ID: {video_id or 'N/A'}",
            f"- Canonical URL: {canonical or 'N/A'}",
            f"- User Turn Lines: {turn.start_line}-{turn.end_line}",
            f"- Gemini Turn Lines: {response_turn.start_line}-{response_turn.end_line}" if response_turn else "- Gemini Turn Lines: N/A",
            "",
            "## Gemini Response",
            "",
            response_text.strip() or "(No Gemini response found)",
        ]
        (OUT_DIR / response_file).write_text("\n".join(response_md) + "\n", encoding="utf-8")

        entries.append(
            {
                "index": idx,
                "source_url": source_url,
                "video_id": video_id,
                "canonical_url": canonical,
                "user_turn": {"start_line": turn.start_line, "end_line": turn.end_line},
                "gemini_turn": {
                    "start_line": response_turn.start_line,
                    "end_line": response_turn.end_line,
                }
                if response_turn
                else None,
                "response_url_mentions": response_urls,
                "response_sections": response_sections,
                "response_file": response_file,
            }
        )

    (OUT_DIR / "index.json").write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    with (OUT_DIR / "index.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "index",
                "source_url",
                "video_id",
                "canonical_url",
                "user_start_line",
                "user_end_line",
                "gemini_start_line",
                "gemini_end_line",
                "response_file",
                "response_url_mentions",
            ]
        )
        for e in entries:
            writer.writerow(
                [
                    e["index"],
                    e["source_url"] or "",
                    e["video_id"] or "",
                    e["canonical_url"] or "",
                    e["user_turn"]["start_line"],
                    e["user_turn"]["end_line"],
                    (e["gemini_turn"] or {}).get("start_line", ""),
                    (e["gemini_turn"] or {}).get("end_line", ""),
                    e["response_file"],
                    " | ".join(e["response_url_mentions"]),
                ]
            )

    md_lines = [
        "# MASTER_ANALYST_PROMPT Parsed Index",
        "",
        f"- Total parsed runs: {len(entries)}",
        f"- Source file: `{INPUT}`",
        "",
        "| # | Video ID | Source URL | Canonical URL | Response File |",
        "|---:|---|---|---|---|",
    ]
    for e in entries:
        md_lines.append(
            f"| {e['index']} | {e['video_id'] or ''} | {e['source_url'] or ''} | {e['canonical_url'] or ''} | `{e['response_file']}` |"
        )

    (OUT_DIR / "index.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"Parsed {len(entries)} MASTER_ANALYST_PROMPT runs")
    print(f"Wrote: {OUT_DIR / 'index.json'}")
    print(f"Wrote: {OUT_DIR / 'index.csv'}")
    print(f"Wrote: {OUT_DIR / 'index.md'}")
    print(f"Responses dir: {RESPONSES_DIR}")


if __name__ == "__main__":
    main()
