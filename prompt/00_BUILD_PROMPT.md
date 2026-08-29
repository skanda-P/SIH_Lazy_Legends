# Build Prompt — IP-SAKTI Sahayak

Paste this whole document into an AI coding agent (Claude Code, etc.) as the mission brief, or
use it as your own team's build checklist. It assumes the reference documents below are also
available to whoever/whatever is building.

## Read these first, in this order

1. `docs/PRD.md` — what the product must do and why (jurisdiction separation, citation
   grounding, abstention, escalation are hard requirements, not nice-to-haves).
2. `docs/DATA_ORGANIZATION.md` — the five-layer corpus, sources per layer, manifest schema,
   chunk metadata schema, KG ontology.
3. `docs/TRD.md` — exact model/infra choices and why (embeddings, reranker, vector store,
   knowledge graph, generation LLM).
4. `docs/DESIGN.md` — architecture diagrams, the classification flow, the hybrid retrieval
   pipeline, and — most importantly — the citation-validator hard-veto design in `DESIGN.md` #6.
   **Do not skip or simplify away the citation validator.** It is the feature that makes this
   product different from "a chatbot with some PDFs attached to it."

## Mission

Build IP-SAKTI Sahayak: a citation-grounded, jurisdiction-aware IP and regulatory research
assistant for Ayurveda products, scoped to the Stage 1 MVP defined in `PRD.md` §8 unless told
otherwise. Every answer must be traceable to a cited, dated, retrieved source, must never mix
India and International rules in one answer, and must abstain explicitly rather than guess when
evidence is insufficient.

## Repo skeleton (already scaffolded alongside this prompt)

```
ip-sakti-sahayak/
├── docs/
│   ├── PRD.md
│   ├── TRD.md
│   ├── DESIGN.md
│   ├── DATA_ORGANIZATION.md
│   └── BUILD_PROMPT.md            <- this file
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── run_all.py                     # one-click orchestrator, stage order below
├── corpus/
│   ├── manifest/schema.sql        # SQLite manifest: source_id, layer, jurisdiction, access_type...
│   ├── layer_a_national_statutes/
│   ├── layer_b_international_treaties/
│   ├── layer_c_registries/        # Stage 2+
│   ├── layer_d_case_law/          # Stage 2+
│   └── layer_e_classification_guidance/
├── ingestion/
│   ├── crawl/enumerate_sources.py     # Stage 1: build the URL manifest FIRST, never scrape blind
│   ├── parse/parse_documents.py       # PDF/HTML -> structure-preserving text
│   ├── chunk/chunk_by_legal_structure.py
│   ├── embed/
│   │   ├── embed_config.yaml
│   │   └── embed_all.py               # BGE-M3 dense + BM25 sparse -> Qdrant, per-layer collections
│   └── diff_tracker.py                # version tracking, never overwrite
├── knowledge_graph/
│   ├── schema/ontology.yaml
│   ├── build_graph.py                 # NetworkX (Stage 1) -> FalkorDB (Stage 2/3)
│   ├── extract_entities.py            # LLM-assisted, provenance-tagged, never invents edges
│   └── graph_queries.py               # path_exists() is the function the validator calls
├── retrieval/
│   ├── bm25_index.py
│   ├── dense_index.py
│   ├── hybrid_retriever.py            # normalize -> filter -> fan-out -> RRF merge -> rerank
│   ├── reranker.py
│   └── kg_lookup.py
├── classification/
│   ├── decision_tree.yaml             # hand-curated, expert-reviewed, NOT scraped
│   └── classifier.py
├── generation/
│   ├── prompt_templates/{india,international}_answer.jinja
│   ├── citation_validator.py          # THE hard-veto verifier — see DESIGN.md #6
│   └── answer_generator.py
├── backend/
│   ├── main.py
│   ├── schemas.py
│   ├── routes/{chat,classify,registry_search}.py
│   └── middleware/{audit_log,prompt_injection_filter}.py
├── frontend/
│   ├── ayurip-guardian-mockup.html    # existing UX spec — see DESIGN.md #7 for the field mapping
│   └── README.md
├── eval/
│   ├── gold_set/gold_qna_template.jsonl
│   └── run_eval.py
└── data/
    ├── vector_store/                  # Qdrant persistence (or point at a running Qdrant instance)
    └── graph/                         # serialized NetworkX graph
```

Every stub file already contains a docstring pointing back to the relevant doc section — read the
docstring before writing the implementation, it's not boilerplate.

## Build order (do not reorder — each stage assumes the previous one works)

### Stage 1 — Citation-grounded MVP (India-only)

1. **Manifest first.** Implement `corpus/manifest/schema.sql` + a thin Python wrapper. Populate
   it by running `ingestion/crawl/enumerate_sources.py` against Layer A + B sources only
   (`DATA_ORGANIZATION.md` §2–3). Do not write a single scraper before the manifest exists.
2. **Parse + chunk.** Implement `parse_documents.py` and `chunk_by_legal_structure.py`. Validate
   on one Act end-to-end (suggest: Patents Act 1970) before running the full corpus — confirm
   section numbers survive parsing.
3. **Embed.** Implement `embed_all.py` against Qdrant, one collection per layer, using BGE-M3
   dense + BM25 sparse (`TRD.md` §4.1, §4.3). Confirm hybrid queries actually return both exact
   section-number matches and semantic matches.
4. **Classification flow.** Implement `classification/decision_tree.yaml` +
   `classifier.py` from `DATA_ORGANIZATION.md` §4.1. Get a domain-expert sanity check on the
   tree before wiring it into retrieval.
5. **Hybrid retrieval.** Implement `hybrid_retriever.py`: normalize → jurisdiction/layer filter →
   BM25 + dense fan-out → RRF merge → `reranker.py` (BGE-reranker-v2-m3) → top 8.
6. **Minimal knowledge graph.** Implement `build_graph.py` for Act→Section edges only (near-free
   from chunk metadata — no LLM extraction needed yet). This is enough to support a first,
   simple version of the citation validator.
7. **Citation-grounded generation.** Implement `answer_generator.py` +
   `citation_validator.py` per `DESIGN.md` §5–6. **This is the step that must not be cut for
   time.** At minimum: every citation the LLM proposes must exist as a real chunk/section in the
   graph or manifest, or the system must abstain with the exact language from `PRD.md` §4.3.
8. **Backend + wire to the existing UI.** Implement `backend/main.py` + routes per
   `DESIGN.md` §8's API contract. Point `frontend/ayurip-guardian-mockup.html` at the live
   `/chat` and `/classify` endpoints, following the field mapping in `DESIGN.md` §7 exactly —
   don't redesign the UI, wire it.
9. **Eval harness.** Hand-write 50–100 gold Q&A pairs (`eval/gold_set/`) and run
   `eval/run_eval.py` before calling Stage 1 done. Report the metrics in `TRD.md` §7.

**Definition of done for Stage 1**: a demo query in each jurisdiction returns a structured
answer with real citations traceable to real retrieved chunks, abstains correctly on an
out-of-scope question, and never mixes India/International content in one response.

### Stage 2 — Knowledge graph + evaluation

10. Add Layers C (registries) and D (case law) to the corpus and vector store.
11. Extend the ontology with case-law relationship types (`CITES`, `OVERRULES`,
    `DISTINGUISHES`, `CONFLICTS_WITH`, `RESOLVED_BY`) and migrate the graph backend from
    NetworkX to FalkorDB (`TRD.md` §5).
12. Extend `citation_validator.py` with CONFLICT-status handling (`DESIGN.md` §6) — surface
    doctrinal splits rather than silently resolving them.
13. Grow the gold evaluation set to 150–300 expert-reviewed questions and get sign-off from one
    Ayurveda/regulatory expert and one IP/legal expert.

### Stage 3 — International + multilingual expansion

14. Add Layer B depth (PCT, Madrid, Hague, Budapest procedural detail; CBD/Nagoya national ABS
    measures) and 1–2 target export-country regulatory sources.
15. Add AI4Bharat IndicTrans2 + Bhashini ASR/TTS for the full multilingual layer (`TRD.md` §4.5).
16. Add paid connectors (TKDL subscription, premium case-law tiers) behind the explicit,
    logged-authorization flow — never before this stage.

## Non-negotiables (repeat, because they're easy to quietly drop under time pressure)

- Jurisdiction sections are never merged.
- No claim ships without a traceable citation; abstain instead of guessing.
- No restricted/paid source is bulk-ingested without a logged authorization.
- Every amendment is a new version, never an overwrite.
- "Information, not legal advice" appears on every substantive answer.
- High-risk questions (infringement, deadlines, regulatory approval, clinical claims, ABS
  liability, litigation) escalate to a human rather than getting a definitive answer.

## When you're unsure

Default to the smaller, more defensible scope: a reliable India-only MVP on Layers A/B/E beats
partial, unverified coverage of every country and every product category. This is explicit in
`PRD.md` §8 and is the right tie-breaker for any scope question that comes up mid-build.
