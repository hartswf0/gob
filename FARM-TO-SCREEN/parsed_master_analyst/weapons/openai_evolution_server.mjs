#!/usr/bin/env node

import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = Number(process.env.EVOLUTION_PORT || 8787);
const HOST = process.env.EVOLUTION_HOST || '127.0.0.1';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
const DEFAULT_MODEL = process.env.OPENAI_MODEL || 'gpt-5-mini';
const OPENAI_BASE_URL = process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1';

const WEAPONS_PATH = path.join(__dirname, 'weaponized_essays.json');
const NOTES_PATH = path.join(__dirname, '..', 'papers', 'zettelkasten_notes.json');

let cache = null;

const SECTION_ORDER = ['NON_OBVIOUS_INSIGHTS', 'TENSIONS_CONTRADICTIONS', 'SO_WHAT', 'WHATS_MISSING'];
const STOPWORDS = new Set([
  'the',
  'and',
  'for',
  'that',
  'with',
  'this',
  'from',
  'into',
  'over',
  'under',
  'are',
  'was',
  'were',
  'have',
  'has',
  'had',
  'not',
  'but',
  'you',
  'your',
  'their',
  'they',
  'them',
  'its',
  'our',
  'out',
  'all',
  'can',
  'will',
  'just',
  'than',
  'more',
  'less',
  'one',
  'two',
  'three',
  'using',
  'used',
  'about',
  'because',
  'which',
  'what',
  'when',
  'where',
  'while',
  'must',
  'should',
]);

const ITEM_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    id: { type: 'string' },
    zettel_id: { type: 'string' },
    bibtex_id: { type: 'string' },
    diagnostic_teardown: {
      type: 'object',
      additionalProperties: false,
      properties: {
        The_Flaw: { type: 'string' },
        The_Weapon: { type: 'string' },
      },
      required: ['The_Flaw', 'The_Weapon'],
    },
    reconstructed_text: { type: 'string' },
    world_model_updates: {
      type: 'array',
      items: { type: 'string' },
    },
    routing_suggestion: {
      type: 'string',
      enum: ['OBSTACLE', 'GOAL', 'SHIFT'],
    },
    confidence: { type: 'number' },
    context_trace: {
      type: 'array',
      items: { type: 'string' },
    },
    fusion_pattern: { type: 'string' },
  },
  required: [
    'id',
    'zettel_id',
    'bibtex_id',
    'diagnostic_teardown',
    'reconstructed_text',
    'world_model_updates',
    'routing_suggestion',
    'confidence',
  ],
};

const MASTER_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    title: { type: 'string' },
    executive_hook: { type: 'string' },
    revised_essay: { type: 'string' },
    structural_map: {
      type: 'object',
      additionalProperties: false,
      properties: {
        instability: { type: 'string' },
        pivot: { type: 'string' },
        resolution: { type: 'string' },
        open_risks: { type: 'string' },
      },
      required: ['instability', 'pivot', 'resolution', 'open_risks'],
    },
    next_prompts: {
      type: 'array',
      items: { type: 'string' },
    },
    context_trace: {
      type: 'array',
      items: { type: 'string' },
    },
    fusion_pattern: { type: 'string' },
  },
  required: ['title', 'executive_hook', 'revised_essay', 'structural_map', 'next_prompts'],
};

const SYSTEM_PROMPT_ITEM = `
You are VALUE_ENGINE_PRIME in ruthless mode.

Role contract:
- You are a Weaponized Structural Editor.
- You do not polish. You demolish and reconstruct.
- Background chronology is hostile to reader utility.

Mission:
- Evolve one fragment into a sharper instability-to-resolution weapon.
- Preserve IDs and traceability.
- Use context as an evidence graph, not as a dumping ground.

Required analysis engine:
1) Target_Lock
   - Define reader and utility currency.
   - Name status-quo bias.
2) Tension_Manufacture
   - Trigger instability from explicit anomaly.
   - Quantify immediate cost in utility currency.
3) Resolution_Delivery
   - Hard pivot from cost to mechanism.
   - Prove superior stability and benefit capture.

Strict constraints:
- BAN background->thesis structure.
- BAN consensus throat-clearing.
- REQUIRE destabilizing first paragraph.
- REQUIRE every paragraph advances problem/solution.
- Do not invent facts outside provided context bundle.

Context handling protocol:
- Select at least one anchor from instability contexts.
- Select at least one counterforce or contradiction context.
- Select at least one resolution context.
- Select at least one unresolved-risk context.
- Use these contexts to fuse, not summarize.

Output must be strict JSON matching the schema.
`;

const SYSTEM_PROMPT_MASTER = `
You are VALUE_ENGINE_PRIME in ruthless mode for full-essay fusion.

Mission:
- Convert fragmented notes into one coherent world-model weapon.
- Sequence strictly:
  instability field -> cost concentration -> pivot mechanics -> resolution architecture -> unresolved risk ledger.
- Optimize for high-stakes decision utility.

Strict constraints:
- No background-history opener.
- No decorative filler.
- Every paragraph either escalates risk or installs mechanism.
- Preserve traceability via IDs/references where useful.
- Do not invent facts beyond provided context and source cards.

Context fusion protocol:
- Build a fused argument from four lanes:
  instability, contradiction, mechanism, unresolved risk.
- Resolve or expose contradictions explicitly.
- Ensure transitions are causal, not topical.

Output must be strict JSON matching the schema.
`;

function tokenize(text) {
  return normalizeText(text)
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter((t) => t.length > 2 && !STOPWORDS.has(t));
}

function uniqueTerms(text, cap = 64) {
  const out = [];
  const seen = new Set();
  for (const t of tokenize(text)) {
    if (seen.has(t)) continue;
    seen.add(t);
    out.push(t);
    if (out.length >= cap) break;
  }
  return out;
}

function jaccard(aTerms, bTerms) {
  if (!aTerms?.length || !bTerms?.length) return 0;
  const a = new Set(aTerms);
  const b = new Set(bTerms);
  let inter = 0;
  for (const t of a) if (b.has(t)) inter += 1;
  const union = a.size + b.size - inter;
  return union > 0 ? inter / union : 0;
}

function firstSentence(value) {
  const text = normalizeText(value);
  if (!text) return '';
  const m = text.match(/(.{20,280}?[.!?])(?:\s|$)/);
  if (m) return m[1].trim();
  return excerpt(text, 220);
}

function json(res, status, body) {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(payload),
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  });
  res.end(payload);
}

function normalizeText(value) {
  return String(value || '').replace(/\s+/g, ' ').trim();
}

function excerpt(value, max = 560) {
  const t = normalizeText(value);
  if (t.length <= max) return t;
  return `${t.slice(0, max - 4)} ...`;
}

async function loadData() {
  if (cache) return cache;
  const [weaponsRaw, notesRaw] = await Promise.all([
    fs.readFile(WEAPONS_PATH, 'utf8'),
    fs.readFile(NOTES_PATH, 'utf8'),
  ]);

  const weapons = JSON.parse(weaponsRaw);
  const notes = JSON.parse(notesRaw);

  const notesById = new Map((notes.notes || []).map((n) => [n.id, n]));
  const essays = (weapons.essays || []).map((e) => {
    const note = notesById.get(e.id) || {};
    const combinedText = `${e.reconstructed_text || ''} ${e.diagnostic_teardown?.The_Weapon || ''} ${note.text || ''}`;
    return {
      ...e,
      links: note.synthetic_links || [],
      note_text: note.text || '',
      section_slug: note.section_slug || '',
      source_video_id: note.video_id || '',
      _terms: uniqueTerms(combinedText, 72),
    };
  });

  const byId = new Map(essays.map((e) => [e.id, e]));
  cache = { essays, byId };
  return cache;
}

function addCandidate(meta, id, delta, reason) {
  const row = meta.get(id) || { score: 0, reasons: new Set() };
  row.score += Number(delta || 0);
  if (reason) row.reasons.add(reason);
  meta.set(id, row);
}

function pickRelated(essay, byId, allEssays, contextIds = [], limit = 12) {
  const meta = new Map();
  const explicitIds = [...new Set((contextIds || []).filter(Boolean))];
  const directLinks = (essay.links || []).slice(0, 20);

  // Explicitly requested contexts get hard priority.
  for (const id of explicitIds) {
    if (id === essay.id) continue;
    if (!byId.has(id)) continue;
    addCandidate(meta, id, 120, 'explicit_context');
  }

  // First-hop graph neighbors.
  for (const l of directLinks) {
    const id = l.target_id;
    if (!id || id === essay.id || !byId.has(id)) continue;
    const s = Number(l.score || 0);
    addCandidate(meta, id, 32 + s * 30, 'direct_link');
  }

  // Second-hop neighborhoods from strongest direct links.
  for (const l of directLinks.slice(0, 6)) {
    const mid = byId.get(l.target_id);
    if (!mid) continue;
    const s1 = Number(l.score || 0.15);
    for (const l2 of (mid.links || []).slice(0, 5)) {
      const id = l2.target_id;
      if (!id || id === essay.id || !byId.has(id)) continue;
      const s2 = Number(l2.score || 0.1);
      addCandidate(meta, id, 8 + s1 * s2 * 40, 'second_hop');
    }
  }

  // Semantic overlap across corpus to avoid graph-only bias.
  for (const cand of allEssays) {
    if (cand.id === essay.id) continue;
    const sim = jaccard(essay._terms || [], cand._terms || []);
    if (sim < 0.025) continue;
    const bonus = cand.section === essay.section ? 8 : 14;
    addCandidate(meta, cand.id, bonus + sim * 32, 'lexical_overlap');
  }

  // Convert + score shaping for diversity.
  const scored = [];
  for (const [id, row] of meta.entries()) {
    const cand = byId.get(id);
    if (!cand) continue;
    let score = row.score;
    if (cand.section !== essay.section) score += 3;
    if (cand.source_video_id && cand.source_video_id !== essay.source_video_id) score += 2;
    scored.push({
      ...cand,
      _ctx_score: score,
      _ctx_reasons: [...row.reasons],
    });
  }
  scored.sort((a, b) => b._ctx_score - a._ctx_score);

  // Selection quotas: keep anchors + cross-section evidence lanes.
  const selected = [];
  const selectedIds = new Set();
  const sectionCount = new Map();
  const videoCount = new Map();

  const tryPick = (cand) => {
    if (!cand || selectedIds.has(cand.id)) return false;
    selected.push(cand);
    selectedIds.add(cand.id);
    sectionCount.set(cand.section, (sectionCount.get(cand.section) || 0) + 1);
    if (cand.source_video_id) {
      videoCount.set(cand.source_video_id, (videoCount.get(cand.source_video_id) || 0) + 1);
    }
    return true;
  };

  // 1) Same-section anchors (up to 2)
  for (const cand of scored) {
    if (cand.section !== essay.section) continue;
    if ((sectionCount.get(cand.section) || 0) >= 2) continue;
    if (tryPick(cand) && selected.length >= limit) break;
  }

  // 2) One per other section if possible (instability/contradiction/resolution/risk lanes)
  for (const section of SECTION_ORDER) {
    if (section === essay.section) continue;
    const cand = scored.find((x) => x.section === section && !selectedIds.has(x.id));
    if (cand) tryPick(cand);
    if (selected.length >= limit) break;
  }

  // 3) Fill remainder by adjusted score (penalize redundancy)
  while (selected.length < limit) {
    let best = null;
    let bestScore = -Infinity;
    for (const cand of scored) {
      if (selectedIds.has(cand.id)) continue;
      const secPenalty = (sectionCount.get(cand.section) || 0) * 2.1;
      const vidPenalty = (videoCount.get(cand.source_video_id) || 0) * 1.3;
      const adjusted = cand._ctx_score - secPenalty - vidPenalty;
      if (adjusted > bestScore) {
        best = cand;
        bestScore = adjusted;
      }
    }
    if (!best) break;
    tryPick(best);
  }

  return selected.slice(0, limit);
}

function buildFusionPacket(target, related) {
  const bySection = {
    NON_OBVIOUS_INSIGHTS: [],
    TENSIONS_CONTRADICTIONS: [],
    SO_WHAT: [],
    WHATS_MISSING: [],
  };
  for (const r of related) {
    if (bySection[r.section]) bySection[r.section].push(r);
  }

  const top = (arr, n = 2) => (arr || []).slice(0, n).map((x) => x.id);
  const lead = (arr) => {
    const x = (arr || [])[0];
    if (!x) return '';
    return firstSentence(x.diagnostic_teardown?.The_Weapon || x.reconstructed_text || x.note_text);
  };

  return {
    anchor_instability_ids: [...top(bySection.NON_OBVIOUS_INSIGHTS, 1), ...top(bySection.TENSIONS_CONTRADICTIONS, 1)],
    anchor_resolution_ids: top(bySection.SO_WHAT, 2),
    anchor_risk_ids: top(bySection.WHATS_MISSING, 2),
    contradiction_pair_ids: [
      ...top(bySection.TENSIONS_CONTRADICTIONS, 1),
      ...top(bySection.SO_WHAT, 1),
    ].slice(0, 2),
    lead_signals: {
      instability: lead([...bySection.NON_OBVIOUS_INSIGHTS, ...bySection.TENSIONS_CONTRADICTIONS]),
      resolution: lead(bySection.SO_WHAT),
      risk: lead(bySection.WHATS_MISSING),
    },
  };
}

function buildItemPrompt({ essay, related, worldModel }) {
  const fusion = buildFusionPacket(essay, related);
  const contextCards = related.map((r) => ({
    id: r.id,
    zettel_id: r.zettel_id,
    section: r.section,
    bibtex_id: r.bibtex_id,
    utility_currency: r.domain_profile?.utility_currency || '',
    flaw_signal: firstSentence(r.diagnostic_teardown?.The_Flaw || ''),
    weapon_signal: firstSentence(r.diagnostic_teardown?.The_Weapon || ''),
    reconstructed_signal: firstSentence(r.reconstructed_text || ''),
    note_signal: firstSentence(r.note_text || ''),
    graph_weight: Number(r._ctx_score || 0),
    selector_reasons: r._ctx_reasons || [],
  }));

  return JSON.stringify(
    {
      task: 'Evolve a single weaponized fragment using prompt engineering + context engineering + world-model consistency.',
      target_fragment: {
        id: essay.id,
        zettel_id: essay.zettel_id,
        bibtex_id: essay.bibtex_id,
        section: essay.section,
        domain_profile: essay.domain_profile,
        diagnostic_teardown: essay.diagnostic_teardown,
        reconstructed_text: essay.reconstructed_text,
      },
      context_bundle: contextCards,
      context_fusion_packet: fusion,
      world_model: worldModel,
      value_engine_prime: {
        target_lock: ['Utility_Currency', 'Status_Quo_Bias'],
        tension_manufacture: ['Instability_Trigger', 'Cost_Escalation'],
        resolution_delivery: ['The_Pivot', 'Benefit_Capture'],
      },
      optimization_objective: {
        strengthen_instability_cost_resolution_arc: true,
        maximize_decision_utility: true,
        preserve_traceability: true,
        cross_section_fusion_required: true,
      },
      output_rules: {
        paragraph_count_target: '3-5',
        must_open_with_destabilizing_element: true,
        explicit_utility_currency: true,
        no_generic_intro: true,
        cite_context_ids_in_context_trace: true,
      },
    },
    null,
    2,
  );
}

function buildMasterPrompt({ essayText, selectedIds, worldModel, sourceCards }) {
  const bySection = {
    NON_OBVIOUS_INSIGHTS: [],
    TENSIONS_CONTRADICTIONS: [],
    SO_WHAT: [],
    WHATS_MISSING: [],
  };

  for (const c of sourceCards) {
    if (bySection[c.section]) bySection[c.section].push(c);
  }

  const laneDigest = {
    instability_lane: [
      ...(bySection.NON_OBVIOUS_INSIGHTS || []).slice(0, 5),
      ...(bySection.TENSIONS_CONTRADICTIONS || []).slice(0, 5),
    ].map((x) => `${x.id}: ${x.weapon_signal}`),
    resolution_lane: (bySection.SO_WHAT || []).slice(0, 6).map((x) => `${x.id}: ${x.weapon_signal}`),
    risk_lane: (bySection.WHATS_MISSING || []).slice(0, 6).map((x) => `${x.id}: ${x.weapon_signal}`),
  };

  return JSON.stringify(
    {
      task: 'Evolve the assembled essay into a higher-coherence world-model narrative with stronger escalation and actionable pivot mechanics.',
      world_model: worldModel,
      selected_ids: selectedIds,
      current_essay: essayText,
      source_cards: sourceCards,
      context_fusion_packet: laneDigest,
      value_engine_prime: {
        target_lock: ['Utility_Currency', 'Status_Quo_Bias'],
        tension_manufacture: ['Instability_Trigger', 'Cost_Escalation'],
        resolution_delivery: ['The_Pivot', 'Benefit_Capture'],
      },
      structural_target: [
        'Instability Field',
        'Cost Concentration',
        'Pivot Mechanics',
        'Resolution Architecture',
        'Unresolved Risk Ledger',
      ],
      constraints: {
        maintain_evidence_traceability: true,
        preserve_tactical_utility: true,
        avoid_empty_rhetoric: true,
        no_background_thesis_structure: true,
        causal_transitions_only: true,
      },
    },
    null,
    2,
  );
}

function extractTextFromResponse(payload) {
  if (!payload || typeof payload !== 'object') return '';

  if (typeof payload.output_text === 'string' && payload.output_text.trim()) {
    return payload.output_text.trim();
  }

  if (Array.isArray(payload.output)) {
    const chunks = [];
    for (const item of payload.output) {
      const content = item?.content;
      if (!Array.isArray(content)) continue;
      for (const c of content) {
        if (typeof c?.text === 'string') chunks.push(c.text);
        else if (typeof c?.output_text === 'string') chunks.push(c.output_text);
      }
    }
    const merged = chunks.join('\n').trim();
    if (merged) return merged;
  }

  const chatText = payload?.choices?.[0]?.message?.content;
  if (typeof chatText === 'string' && chatText.trim()) return chatText.trim();

  if (Array.isArray(chatText)) {
    const merged = chatText
      .map((p) => (typeof p?.text === 'string' ? p.text : ''))
      .join('\n')
      .trim();
    if (merged) return merged;
  }

  return '';
}

function parseStrictJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    const cleaned = String(text || '')
      .replace(/^```json\s*/i, '')
      .replace(/^```\s*/i, '')
      .replace(/\s*```$/, '')
      .trim();
    return JSON.parse(cleaned);
  }
}

async function callOpenAI({ systemPrompt, userPrompt, schema, schemaName, model, temperature, maxOutputTokens }) {
  if (!OPENAI_API_KEY) {
    const err = new Error('OPENAI_API_KEY is not set');
    err.status = 503;
    throw err;
  }

  const body = {
    model: model || DEFAULT_MODEL,
    input: [
      {
        role: 'system',
        content: [{ type: 'input_text', text: systemPrompt }],
      },
      {
        role: 'user',
        content: [{ type: 'input_text', text: userPrompt }],
      },
    ],
    temperature: typeof temperature === 'number' ? temperature : 0.6,
    max_output_tokens: Number(maxOutputTokens || 1600),
    text: {
      format: {
        type: 'json_schema',
        name: schemaName,
        strict: true,
        schema,
      },
    },
  };

  const res = await fetch(`${OPENAI_BASE_URL}/responses`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  const payload = await res.json().catch(() => ({}));

  if (!res.ok) {
    const err = new Error(payload?.error?.message || `OpenAI error ${res.status}`);
    err.status = res.status;
    err.payload = payload;
    throw err;
  }

  const outputText = extractTextFromResponse(payload);
  if (!outputText) {
    const err = new Error('OpenAI returned empty output');
    err.status = 502;
    err.payload = payload;
    throw err;
  }

  return {
    json: parseStrictJson(outputText),
    raw: payload,
  };
}

async function readBody(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString('utf8') || '{}';
  return JSON.parse(raw);
}

function worldModelDefaults(input = {}) {
  const wm = input && typeof input === 'object' ? input : {};
  return {
    forged_count: Number(wm.forged_count || 0),
    section_mix: wm.section_mix || {},
    coverage: Number(wm.coverage || 100),
    compression: Number(wm.compression || 0),
    sort_mode: wm.sort_mode || 'SECTION',
    objective: wm.objective || 'Increase decision utility and coherence under instability',
  };
}

function buildSourceCards(selectedIds, byId, fallbackEssays = [], limit = 48) {
  const ids = [...new Set((selectedIds || []).filter(Boolean))];
  const cards = [];

  for (const id of ids) {
    const e = byId.get(id);
    if (!e) continue;
    cards.push({
      id: e.id,
      zettel_id: e.zettel_id,
      section: e.section,
      bibtex_id: e.bibtex_id,
      utility_currency: e.domain_profile?.utility_currency || '',
      flaw_signal: firstSentence(e.diagnostic_teardown?.The_Flaw || ''),
      weapon_signal: firstSentence(e.diagnostic_teardown?.The_Weapon || ''),
      reconstructed_signal: firstSentence(e.reconstructed_text || ''),
      note_signal: firstSentence(e.note_text || ''),
    });
    if (cards.length >= limit) return cards;
  }

  if (cards.length === 0 && fallbackEssays.length) {
    const fallback = [...fallbackEssays]
      .sort((a, b) => SECTION_ORDER.indexOf(a.section) - SECTION_ORDER.indexOf(b.section))
      .slice(0, Math.min(limit, 24));
    for (const e of fallback) {
      cards.push({
        id: e.id,
        zettel_id: e.zettel_id,
        section: e.section,
        bibtex_id: e.bibtex_id,
        utility_currency: e.domain_profile?.utility_currency || '',
        flaw_signal: firstSentence(e.diagnostic_teardown?.The_Flaw || ''),
        weapon_signal: firstSentence(e.diagnostic_teardown?.The_Weapon || ''),
        reconstructed_signal: firstSentence(e.reconstructed_text || ''),
        note_signal: firstSentence(e.note_text || ''),
      });
    }
  }

  return cards;
}

async function handleEvolveItem(req, res) {
  const body = await readBody(req);
  const { byId, essays } = await loadData();

  const essayId = body?.essay_id;
  const essay = byId.get(essayId);
  if (!essay) return json(res, 404, { error: `Unknown essay_id: ${essayId}` });

  const contextIds = Array.isArray(body.context_ids) ? body.context_ids : [];
  const worldModel = worldModelDefaults(body.world_model);
  const contextLimit = Math.max(4, Math.min(20, Number(body.context_limit || 12)));
  const related = pickRelated(essay, byId, essays, contextIds, contextLimit);

  const userPrompt = buildItemPrompt({ essay, related, worldModel });
  const result = await callOpenAI({
    systemPrompt: SYSTEM_PROMPT_ITEM,
    userPrompt,
    schema: ITEM_SCHEMA,
    schemaName: 'evolved_fragment',
    model: body.model,
    temperature: body.temperature,
    maxOutputTokens: body.max_output_tokens,
  });

  return json(res, 200, {
    ok: true,
    evolved: result.json,
    context_used: related.map((r) => ({
      id: r.id,
      zettel_id: r.zettel_id,
      section: r.section,
      score: Number(r._ctx_score || 0),
      reasons: r._ctx_reasons || [],
    })),
    context_strategy: {
      requested_ids: contextIds,
      selected_count: related.length,
      section_distribution: related.reduce((acc, x) => {
        acc[x.section] = (acc[x.section] || 0) + 1;
        return acc;
      }, {}),
    },
    model: body.model || DEFAULT_MODEL,
  });
}

async function handleEvolveMaster(req, res) {
  const body = await readBody(req);
  const { byId, essays } = await loadData();

  const essayText = String(body.essay_text || '').trim();
  if (!essayText) return json(res, 400, { error: 'essay_text is required' });

  const selectedIds = Array.isArray(body.selected_ids) ? body.selected_ids : [];
  const worldModel = worldModelDefaults(body.world_model);
  const sourceCards = buildSourceCards(selectedIds, byId, essays, Number(body.context_limit || 48));

  const userPrompt = buildMasterPrompt({ essayText, selectedIds, worldModel, sourceCards });
  const result = await callOpenAI({
    systemPrompt: SYSTEM_PROMPT_MASTER,
    userPrompt,
    schema: MASTER_SCHEMA,
    schemaName: 'evolved_master_essay',
    model: body.model,
    temperature: body.temperature,
    maxOutputTokens: body.max_output_tokens,
  });

  return json(res, 200, {
    ok: true,
    evolved: result.json,
    context_used: sourceCards.map((x) => ({ id: x.id, zettel_id: x.zettel_id, section: x.section })),
    model: body.model || DEFAULT_MODEL,
  });
}

async function handleHealth(_req, res) {
  const loaded = await loadData();
  return json(res, 200, {
    ok: true,
    status: 'ready',
    openai_key_present: Boolean(OPENAI_API_KEY),
    default_model: DEFAULT_MODEL,
    fragments: loaded.essays.length,
  });
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'OPTIONS') {
      res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      });
      res.end();
      return;
    }

    const url = new URL(req.url || '/', `http://${req.headers.host}`);

    if (req.method === 'GET' && url.pathname === '/api/health') {
      return handleHealth(req, res);
    }

    if (req.method === 'POST' && url.pathname === '/api/evolve-item') {
      return handleEvolveItem(req, res);
    }

    if (req.method === 'POST' && url.pathname === '/api/evolve-master') {
      return handleEvolveMaster(req, res);
    }

    return json(res, 404, {
      error: 'Not found',
      routes: ['GET /api/health', 'POST /api/evolve-item', 'POST /api/evolve-master'],
    });
  } catch (err) {
    return json(res, err.status || 500, {
      error: err.message || 'Server error',
      details: err.payload || undefined,
    });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`[evolution-server] listening on http://${HOST}:${PORT}`);
  console.log(`[evolution-server] model=${DEFAULT_MODEL}`);
  console.log(`[evolution-server] key_present=${Boolean(OPENAI_API_KEY)}`);
});
