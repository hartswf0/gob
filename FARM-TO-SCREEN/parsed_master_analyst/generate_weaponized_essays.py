#!/usr/bin/env python3
"""Generate weaponized essays from zettelkasten notes.

Input:
  - parsed_master_analyst/papers/zettelkasten_notes.json

Outputs:
  - parsed_master_analyst/weapons/weaponized_essays.json
  - parsed_master_analyst/weapons/weaponized_essays.md
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "papers" / "zettelkasten_notes.json"
OUT_DIR = BASE_DIR / "weapons"
OUT_JSON = OUT_DIR / "weaponized_essays.json"
OUT_MD = OUT_DIR / "weaponized_essays.md"

SECTION_LABELS: Dict[str, str] = {
    "NON_OBVIOUS_INSIGHTS": "NON_OBVIOUS_INSIGHTS",
    "TENSIONS_CONTRADICTIONS": "TENSIONS_CONTRADICTIONS",
    "SO_WHAT": "SO_WHAT",
    "WHATS_MISSING": "WHATS_MISSING",
}


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()


def first_sentence(value: str) -> str:
    text = normalize_space(value)
    if not text:
        return ""
    text = text.replace("vs.", "versus")
    match = re.match(r"(.{30,300}?[.!?])(?:\s|$)", text)
    if match:
        candidate = match.group(1).strip()
        if len(candidate) >= 30:
            return candidate
    colon_match = re.match(r"(.{30,300}?:)(?:\s|$)", text)
    if colon_match:
        candidate = colon_match.group(1).strip()
        if len(candidate) >= 30:
            return candidate
    return text[:220].rstrip(" ,;:") + ("..." if len(text) > 220 else "")


def contains_any(text: str, terms: List[str]) -> bool:
    return any(term in text for term in terms)


def detect_domain(note_text: str) -> str:
    text = note_text.lower()
    if contains_any(
        text,
        [
            "school",
            "district",
            "teacher",
            "student",
            "university",
            "classroom",
            "assessment",
            "education",
        ],
    ):
        return "education_policy"
    if contains_any(
        text,
        [
            "procurement",
            "contract",
            "board",
            "compliance",
            "audit",
            "superintendent",
            "vendor",
        ],
    ):
        return "public_procurement"
    if contains_any(
        text,
        [
            "llm",
            "transformer",
            "hallucination",
            "context window",
            "benchmark",
            "model collapse",
            "scaling law",
            "inference",
            "token",
            "state-of-the-art",
        ],
    ):
        return "ai_ml_research"
    if contains_any(
        text,
        [
            "architecture",
            "pipeline",
            "latency",
            "throughput",
            "system",
            "stack",
            "infrastructure",
            "api",
            "ontology",
            "deployment",
        ],
    ):
        return "system_architecture_spec"
    if contains_any(
        text,
        [
            "grant",
            "funding",
            "fund",
            "budget",
            "proposal",
            "invest",
            "program",
            "allocation",
            "resource",
        ],
    ):
        return "funding_grant_proposal"
    return "general"


def utility_currency(domain: str) -> str:
    mapping = {
        "ai_ml_research": "model reliability per compute dollar",
        "system_architecture_spec": "latency headroom, uptime, and scaling resilience",
        "funding_grant_proposal": "field-moving output per funded cycle",
        "education_policy": "credential credibility, retention, and compliance risk",
        "public_procurement": "legal exposure, budget continuity, and institutional trust",
        "general": "decision quality under time pressure",
    }
    return mapping.get(domain, mapping["general"])


def target_reader(domain: str) -> str:
    mapping = {
        "ai_ml_research": "AI/ML research lead shipping models under performance pressure",
        "system_architecture_spec": "system architect responsible for production reliability",
        "funding_grant_proposal": "program/funding decision-maker controlling scarce resources",
        "education_policy": "education operator accountable for outcomes and legitimacy",
        "public_procurement": "public-sector technology buyer exposed to audit and legal risk",
        "general": "time-constrained strategic decision-maker",
    }
    return mapping.get(domain, mapping["general"])


def status_quo_bias(section: str, domain: str) -> str:
    if section == "NON_OBVIOUS_INSIGHTS":
        return "Assumes narrative novelty is a proxy for operational truth."
    if section == "TENSIONS_CONTRADICTIONS":
        return "Assumes contradictions can be tolerated indefinitely without structural failure."
    if section == "SO_WHAT":
        return "Assumes existing process still certifies value in a changed environment."
    if section == "WHATS_MISSING":
        return "Assumes unanswered questions are harmless and can be deferred."
    if domain == "ai_ml_research":
        return "Assumes benchmark progress equals robust deployment performance."
    return "Assumes the current model remains valid despite accumulating anomalies."


def diagnostic_flaw(section: str) -> str:
    mapping = {
        "NON_OBVIOUS_INSIGHTS": "The original framing surfaced a hidden pattern but did not force the reader to price the operational damage of ignoring it.",
        "TENSIONS_CONTRADICTIONS": "The draft named contradictions as observations instead of converting them into an explicit failure condition.",
        "SO_WHAT": "The draft pointed toward action but left the urgency under-weaponized for a decision-maker protecting scarce resources.",
        "WHATS_MISSING": "The draft listed missing questions without turning uncertainty into a mandatory precondition for action.",
    }
    return mapping.get(section, "The draft explained more than it compelled.")


def escalation_cost(currency: str) -> str:
    return (
        f"Cost in {currency}: one ignored cycle compounds into three losses: "
        "cleanup workload, trust erosion, and decision latency at exactly the moment speed matters."
    )


def opening_paragraph(domain: str, trigger: str) -> str:
    trigger_line = trigger or "Your current operating model is already failing under pressure."
    if domain == "ai_ml_research":
        return (
            f"Your state-of-the-art posture is already unstable: {trigger_line} "
            "This is not a future risk; it is a present reliability breach hiding behind benchmark comfort."
        )
    if domain == "system_architecture_spec":
        return (
            f"Your architecture is closer to a scaling cliff than your dashboard admits: {trigger_line} "
            "Without redesign, the system breaks exactly where growth is supposed to prove value."
        )
    if domain == "funding_grant_proposal":
        return (
            f"The bottleneck is active now, and deferral is paralysis: {trigger_line} "
            "If this remains unfunded, downstream work stalls while costs continue to accumulate."
        )
    return (
        f"The comfortable model is already breaking: {trigger_line} "
        "Treating this as background information is the failure mode."
    )


def pivot_paragraph(section: str, domain: str) -> str:
    if section == "WHATS_MISSING":
        return (
            "Pivot: convert uncertainty into a gate, not a footnote. "
            "No deployment, contract, or policy move proceeds until the unresolved question is answered with auditable evidence."
        )
    if section == "TENSIONS_CONTRADICTIONS":
        return (
            "Pivot: force the tradeoff into explicit priority order. "
            "Name which objective wins under stress, codify that choice in process, and kill the silent contradiction loop."
        )
    if section == "SO_WHAT":
        return (
            "Pivot: translate implication into operating protocol. "
            "Replace symbolic compliance with measurable behaviors, ownership, and time-bound checkpoints."
        )
    if domain == "system_architecture_spec":
        return (
            "Pivot: rebuild around failure containment first, feature expansion second. "
            "Design for bottleneck visibility, degradation control, and deterministic rollback."
        )
    return (
        "Pivot: stop rewarding appearance and start rewarding verification. "
        "Re-anchor decisions to evidence quality, failure tracing, and accountability ownership."
    )


def benefit_paragraph(currency: str, note_text: str) -> str:
    leverage = first_sentence(note_text)
    return (
        "Result: you get a new stability regime where decisions survive contact with reality. "
        f"You recover {currency} by reducing rework, compressing correction cycles, and preventing preventable escalation. "
        f"The signal you preserve is simple: {leverage}"
    )


def weaponize_note(note: dict) -> dict:
    section = note.get("section", "UNKNOWN")
    note_text = normalize_space(note.get("text", ""))
    trigger = first_sentence(note_text)
    domain = detect_domain(note_text)
    reader = target_reader(domain)
    currency = utility_currency(domain)
    bias = status_quo_bias(section, domain)

    flaw = diagnostic_flaw(section)
    weapon = f"Instability trigger: {trigger} {escalation_cost(currency)}"

    para_1 = opening_paragraph(domain, trigger)
    para_2 = (
        f"Your utility currency is {currency}. "
        f"Each time this instability is normalized, your operating position degrades while the reporting layer stays deceptively calm. "
        f"{escalation_cost(currency)}"
    )
    para_3 = pivot_paragraph(section, domain)
    para_4 = benefit_paragraph(currency, note_text)

    reconstructed = "\n\n".join([para_1, para_2, para_3, para_4]).strip()

    return {
        "id": note.get("id"),
        "zettel_id": note.get("zettel_id"),
        "bibtex_id": note.get("bibtex_id"),
        "section": section,
        "label": note.get("label", ""),
        "source_url": note.get("source_url", ""),
        "canonical_url": note.get("canonical_url", ""),
        "response_file": note.get("response_file", ""),
        "domain_profile": {
            "target_reader": reader,
            "utility_currency": currency,
            "status_quo_bias": bias,
        },
        "diagnostic_teardown": {
            "The_Flaw": flaw,
            "The_Weapon": weapon,
        },
        "reconstructed_text": reconstructed,
    }


def render_markdown(bundle: dict) -> str:
    lines: List[str] = []
    lines.append("# Weaponized Essay Corpus")
    lines.append("")
    lines.append(f"- Generated: {bundle['generated_at']}")
    lines.append(f"- Source: `{bundle['source']}`")
    lines.append(f"- Total Essays: {bundle['total_essays']}")
    lines.append("")

    for item in bundle["essays"]:
        lines.append(f"## {item['zettel_id']} | {item['label']}")
        lines.append("")
        lines.append(f"- note_id: `{item['id']}`")
        lines.append(f"- bibtex_id: `{item['bibtex_id']}`")
        lines.append(f"- section: `{item['section']}`")
        lines.append("")
        lines.append("### DIAGNOSTIC_TEARDOWN")
        lines.append("")
        lines.append(f"- **The_Flaw:** {item['diagnostic_teardown']['The_Flaw']}")
        lines.append(f"- **The_Weapon:** {item['diagnostic_teardown']['The_Weapon']}")
        lines.append("")
        lines.append("### RECONSTRUCTED_TEXT")
        lines.append("")
        lines.append(item["reconstructed_text"])
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    notes = payload.get("notes", [])
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    essays = [weaponize_note(note) for note in notes]

    bundle = {
        "generated_at": generated_at,
        "source": str(INPUT_PATH),
        "total_essays": len(essays),
        "essays": essays,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(bundle), encoding="utf-8")

    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_MD}")
    print(f"Total essays: {len(essays)}")


if __name__ == "__main__":
    main()
