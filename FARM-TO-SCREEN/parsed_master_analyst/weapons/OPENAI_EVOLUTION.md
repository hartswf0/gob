# OpenAI Evolution Pipeline (RIPPLES Essay Forge)

## What This Adds

- Secure local proxy for OpenAI calls (API key never exposed to browser).
- Context-engineered fragment evolution endpoint.
- Master essay evolution endpoint.
- Scored context fusion selector:
  - explicit IDs (hard priority)
  - first-hop synthetic links
  - second-hop graph neighbors
  - lexical overlap across corpus
  - section/video diversity shaping
- Fusion packet assembly by lanes:
  - instability
  - contradiction
  - resolution
  - unresolved risk
- UI controls inside `verification-premium-corpus-ripples-essay-forge.html`:
  - `AI Evolve Selected`
  - `AI Evolve Master`
  - `Apply AI Draft`

## Files

- `FARM-TO-SCREEN/parsed_master_analyst/weapons/openai_evolution_server.mjs`
- `FARM-TO-SCREEN/verification-premium-corpus-ripples-essay-forge.html`

## Start Server

```bash
cd /Users/gaia/GEOMETRY OF BIAS
export OPENAI_API_KEY="<YOUR_KEY>"
# Optional
# export OPENAI_MODEL="gpt-5-mini"
# export EVOLUTION_PORT="8787"
node FARM-TO-SCREEN/parsed_master_analyst/weapons/openai_evolution_server.mjs
```

Health check:

```bash
curl http://localhost:8787/api/health
```

## Use In Forge UI

1. Open `FARM-TO-SCREEN/verification-premium-corpus-ripples-essay-forge.html` via HTTP server.
2. Ensure endpoint input is `http://localhost:8787`.
3. Select a fragment, then click `AI Evolve Selected`.
4. Click `Apply AI Draft` to commit evolved text into the corpus state.
5. Build/route as needed, then click `AI Evolve Master` and `Apply AI Draft`.
6. Copy/export from normal buttons.

## API Endpoints

### `POST /api/evolve-item`
Input:

```json
{
  "essay_id": "zk-n-001-01",
  "context_ids": ["zk-t-001-01", "zk-s-001-01"],
  "world_model": {
    "forged_count": 10,
    "coverage": 100,
    "compression": 20,
    "sort_mode": "SECTION"
  },
  "temperature": 0.6,
  "max_output_tokens": 1400
}
```

Response includes:
- `context_used` with score/reasons for each selected context card
- `context_strategy` with section distribution

### `POST /api/evolve-master`
Input:

```json
{
  "essay_text": "# MASTER WEAPON ESSAY ...",
  "selected_ids": ["zk-n-001-01", "zk-t-001-01"],
  "world_model": {
    "forged_count": 120,
    "coverage": 80,
    "compression": 10,
    "sort_mode": "ID"
  },
  "temperature": 0.55,
  "max_output_tokens": 2600
}
```

Response includes:
- `context_used` source cards used for master fusion

## Prompt Discipline (VALUE_ENGINE_PRIME)

Both evolve routes enforce:
- destabilizing first paragraph
- explicit utility currency + cost escalation
- hard pivot mechanics
- benefit capture and new stability proof
- no background-thesis filler
- context IDs preserved for traceability

## Notes

- If you route/add/clear fragments after applying AI master override, the override is invalidated.
- Item-level AI drafts are non-destructive until `Apply AI Draft`.
- Server allows CORS for local browser tooling.
