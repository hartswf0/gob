# Geometry of Bias OS

A four-stage research operating system for moving from wide discovery to structural interpretation without collapsing into early summary.

## Navigation

- `index.html` - main hub (overview, handoff contracts, guardrails).
- `prompt-workflow-mobile.html` - mobile copyboard for quick execution.
- `01-OS.md` - site enumeration stage.
- `02-OS.md` - dossier excavation stage.
- `03-OS.md` - structural analysis stage.
- `04-OS.md` - interface generation stage.

## Overall Interpretation

This system is intentionally modular. Each prompt enforces one cognitive job:

1. divergence (`01`) to expand possibilities,
2. evidence construction (`02`) to preserve complexity,
3. inference (`03`) to force consequential interpretation,
4. interface operationalization (`04`) to scale exploration.

Core claim: quality comes from strict stage boundaries, not from one large blended prompt.

## File-By-File Overview

| File | Prompt Name | What It Does | Typical Output | Why It Exists |
|---|---|---|---|---|
| `01-OS.md` | `SITE_FORAGER` | Enumerates specific, bounded sites without prioritizing or analyzing. | Long unranked site list with coordinates + brief relevance. | Prevents early tunnel vision. |
| `02-OS.md` | `PRIME_ARCHAEOLOGIST` | Builds a layered dossier with contradictions preserved. | Five-section case dossier with concrete artifacts. | Creates depth substrate for analysis. |
| `03-OS.md` | `MASTER_ANALYST_PROMPT` | Extracts non-obvious structure, tensions, and implications. | Insights, contradictions, core implication, missing inquiry. | Turns evidence into strategic interpretation. |
| `04-OS.md` | `CRATE_DIGGER_INTERFACE` | Generates a standalone research UI for site browsing. | Single-file HTML/CSS/JS interface. | Operationalizes exploration outputs. |

## Handoff Contract

| Step | Required Input | Required Output | Feeds Into |
|---|---|---|---|
| `01` | Domain/question/territory | Unranked site list with coordinates + relevance | `02` (single selected site), `04` (full site list) |
| `02` | One site from `01` | Five-section dossier with contradictions preserved | `03` |
| `03` | Dossier or equivalent document | Insights, tensions, core implication, missing inquiry | Decisions + next investigation cycle |
| `04` | Site list (usually from `01`) | Standalone exploration interface | Ongoing browsing and selection |

## Recommended Sequence

1. Run `01-OS.md` on a domain/question.
2. Select one site from Step 1 and run `02-OS.md`.
3. Run `03-OS.md` on the Step 2 dossier.
4. Use `04-OS.md` when you need a browsable/filterable interface for site collections.

Core analysis chain: `01 -> 02 -> 03`  
Interface layer: `04`

## Fortification Rules

- Do not skip from `01` directly to `03`; `03` expects dossier density.
- Do not summarize in `02`; contradictions are required, not noise.
- Keep stage outputs frozen before handoff; avoid quiet rewrites.
- Record run date, scope, and prompt versions for traceability.
- Treat `04` outputs as tooling infrastructure, not analytical evidence.

## Run Log Template

```text
Run Date:
Topic:
Step 01 Output Ref:
Selected Site For 02:
Step 02 Output Ref:
Step 03 Core Implication:
Step 03 Next Inquiry:
Step 04 Interface File (optional):
Notes / Assumptions:
```

## Start Here

1. Open `index.html`.
2. Launch `prompt-workflow-mobile.html`.
3. Execute the steps in order with the handoff contract above.
