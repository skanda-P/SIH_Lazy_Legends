# Technical Requirements Document — IP-SAKTI Sahayak

Companion to `PRD.md` (what/why) and `DESIGN.md` (how it fits together). This document is
the concrete tool/model selection with rationale, so the build prompt doesn't have to guess.

## 1. System summary

A hybrid retrieval-augmented generation system over a jurisdiction-partitioned, layer-partitioned
legal/regulatory corpus, with a knowledge graph used as a **hard verification constraint** on
generation (not just a retrieval aid), fronted by a classification flow and a FastAPI backend.

## 2. Reference architecture note

The file/module layout in this repo (`ingestion/`, `knowledge_graph/`, `retrieval/`, `backend/`,
`frontend/`, `data/{vector_store,graph}/`) is adapted from a hackathon "unified knowledge
intelligence" pattern (ingestion pipeline → embeddings + entity extraction → hybrid retriever →
LLM → 4-tab UI) — the same shape used successfully for an industrial-knowledge copilot. What's
changed for IP-SAKTI:

- Retrieval must be **jurisdiction- and layer-partitioned from day one** (separate vector
  collections per corpus layer — see `DATA_ORGANIZATION.md` #1), not a single global index.
- The knowledge graph is used for **citation verification with a hard veto**, not only for
  answering "what's related to X" — see #5 and `DESIGN.md` #6.
- A **classification flow** sits in front of retrieval (the reference project has no analogue —
  industrial equipment doesn't need a "what kind of product is this" step; Ayurveda formulations do).
- **Abstention is a first-class output**, not a fallback string. It has its own confidence tier and
  is tracked as a metric (#7).

## 3. Tech stack at a glance

| Layer | MVP (Stage 1) choice | Rationale | Stage 2/3 evolution |
|---|---|---|---|
| Backend | FastAPI + Uvicorn | Async, typed, fast to demo | Add auth, rate limiting |
| Vector store | **Qdrant** | Native hybrid dense+sparse (BM25) search in one system — see #4.3 | Same; shard by layer if corpus grows |
| Sparse/lexical | Qdrant sparse vectors (BM25) | Avoids standing up a second search engine for MVP | OpenSearch/Elasticsearch if legal-specific BM25 tuning is needed |
| Dense embeddings | **BGE-M3** (self-hosted) | Free, multilingual, strong hybrid dense+sparse+multi-vector support — see #4.1 | Add Qwen3-Embedding or Gemini Embedding 2 for cross-lingual-heavy Stage 3 queries |
| Reranker | **BGE-reranker-v2-m3** (self-hosted) | Free, multilingual, the standard self-hosted baseline — see #4.2 | Qwen3-Reranker or a managed API (Cohere Rerank 4) if quality/latency demands it |
| Knowledge graph | **NetworkX** (in-process, serialized to `data/graph/`) | Zero infra, fast to iterate during a hackathon | **FalkorDB** — Cypher-compatible, sub-ms hybrid vector+graph queries, clean LangGraph integration — see #5 |
| Generation LLM | **Claude Sonnet 5** (primary), Claude Opus 5 (hard cases / verifier), Claude Haiku 4.5 (cheap auxiliary tasks) | See #4.4 — this is a comparison, not a single-vendor lock-in | Keep model-agnostic behind one interface; add GPT-5.5 as a second-opinion / cross-check model for high-stakes answers |
| Translation (Stage 3) | AI4Bharat IndicTrans2 + Bhashini APIs | Purpose-built for all 22 scheduled Indian languages, open-source, government-aligned | — |
| Corpus manifest | SQLite | Zero infra for MVP | Postgres if multi-writer/concurrent crawling |

## 4. Model selection — detailed rationale

Model rankings move fast; treat the specific names below as **the current best default**, not
permanent choices. The interface contracts in `retrieval/` and `generation/` are written so any
of these can be swapped via `.env` without touching pipeline logic.

### 4.1 Embedding model

**Default: BGE-M3** (BAAI, open-source, Apache-2.0-style license, self-hosted).

Why: it natively supports dense + sparse + multi-vector (ColBERT-style) retrieval from one model,
which is exactly the hybrid-retrieval shape the brief requires, it's free to run at hackathon
scale, and it has strong multilingual coverage including Hindi and other Indic languages, which
matters given the multilingual requirement even at MVP scope.

Alternatives and when to reach for them:

| Model | Reach for it when |
|---|---|
| **Qwen3-Embedding** | You want the strongest open-weight cross-lingual retrieval and are willing to self-host a larger model; pairs naturally with Qwen3-Reranker. |
| **Gemini Embedding 2** | Cross-lingual accuracy is the bottleneck (it benchmarks at the top of cross-lingual retrieval suites) and an API dependency + per-call cost is acceptable. |
| **OpenAI text-embedding-3-large** | You want the easiest managed integration and don't need best-in-class multilingual performance. |
| **InLegalBERT** (fine-tuning base, not a drop-in embedder) | Stage 2+, if you fine-tune a retrieval or classification head specifically on Indian statute/case-law text — it's pre-trained on 5.4M Indian legal documents and is the standard domain-adapted base for Indian legal NLP tasks. |

Decision rule: don't over-invest here before checking whether reranking closes the gap — in
production RAG, a mediocre top-50 retrieval fixed by a good reranker often beats swapping
embedding models outright.

### 4.2 Reranker

**Default: BGE-reranker-v2-m3** (self-hosted, free, multilingual, the standard baseline paired
with BGE-M3).

Alternatives:

| Model | Reach for it when |
|---|---|
| **Qwen3-Reranker** | You want the strongest open-weight reranking quality and can afford its higher latency (larger variants are noticeably slower per query). |
| **Cohere Rerank 4** | Zero self-host infra is preferred and a managed API cost is acceptable — broadest managed language coverage. |
| **jina-reranker-v3** | Long-document, listwise reranking (useful once Layer D case law is in scope — full judgments are long). |

### 4.3 Vector database

**Default: Qdrant**, self-hosted (Docker) for the hackathon, managed Qdrant Cloud if it needs to
survive past demo day.

Why over Chroma (the reference project's choice): Qdrant has first-class native hybrid
dense+sparse (BM25-style) search in a single query, which maps directly onto the brief's
"hybrid BM25 and vector retrieval" requirement in Stage 1 without running two separate systems.
Chroma is fine for a pure-vector MVP but pushes you toward a bolt-on BM25 layer later.

### 4.4 Generation LLM

This is a fast-moving choice; the important design decision is **the verification layer matters
more than which model you pick** — a 2026 legal-AI benchmark across ten frontier models found
that roughly a quarter of graded answers cited or misapplied law that didn't support the claim,
and *every* frontier model tested fabricated or misapplied at least one citation. No model is
safe for legal-adjacent work without the hard citation-verification layer in `DESIGN.md` #6 —
that layer is not optional hardening, it is the product.

With that said, current relative strengths worth knowing when picking a primary model:

- **Claude (Sonnet 5 / Opus 5)** — in a 2026 commercial legal-work benchmark, Claude's frontier
  model led overall across a 300-task suite and won the most individual tasks. Recommended as
  the primary generation model, with Opus 5 reserved for the citation-validator's revision step
  and any multi-hop reasoning across jurisdictions.
- **GPT-5.5** — the same benchmark found it scored highest on raw accuracy with the fewest
  fabricated citations of the three vendors tested, and is strong on numerically heavy work
  (useful if damages/valuation-style calculations ever enter scope). A reasonable second-opinion
  or cross-check model for high-stakes answers.
- **Gemini 3.1 Pro** — a close third overall with a clear edge on very long documents; worth
  considering specifically for Layer D (full case-law judgments) once that layer is in scope.
- **Claude Haiku 4.5** — cheap, fast auxiliary tasks: query normalization/language detection,
  translation orchestration, bulk entity extraction during ingestion (`knowledge_graph/extract_entities.py`),
  where a frontier model would be overkill and slow.

Practical recommendation for this build: **Claude Sonnet 5** as the default answer-generation
model, **Claude Opus 5** for the citation validator's harder revision/adjudication passes (it's
the step where correctness matters most and answer volume is lowest), **Claude Haiku 4.5** for
high-volume ingestion-time extraction. Keep the LLM client behind one interface
(`generation/answer_generator.py`) so GPT-5.5 or Gemini 3.1 Pro can be swapped in per-layer or
run as a cross-check without a pipeline rewrite.

### 4.5 Domain-adapted models worth knowing about (optional, Stage 2+)

- **InLegalBERT / InCaseLawBERT** (law-ai, IIT Kharagpur) — BERT-family models pre-trained on
  5.4M Indian court documents. Useful as a fine-tuning base if you build a dedicated statute-
  retrieval or classification head rather than relying purely on general-purpose embeddings.
- **AI4Bharat IndicTrans2** — open-source, all 22 scheduled Indian languages, the natural choice
  for the Stage 3 translation layer, and it's what the Bhashini government initiative itself is
  built around, so it aligns with the brief's own Stage 3 direction.

## 5. Knowledge graph: NetworkX now, FalkorDB next

**Stage 1:** NetworkX, serialized to `data/graph/`. Zero infrastructure, trivial to iterate on the
ontology (`knowledge_graph/schema/ontology.yaml`) during a hackathon, and it's exactly the
pattern the reference architecture used successfully at this scale.

**Stage 2/3:** migrate to **FalkorDB**. Reasons specific to this product, not graph-DB fashion:

- FalkorDB speaks Cypher, so the migration from a NetworkX prototype to a real graph query layer
  doesn't require relearning a query language, and most MATCH/WHERE/RETURN/MERGE patterns port
  with only minor edits.
- It supports **hybrid vector-plus-graph queries at sub-millisecond latency**, which matters once
  the citation validator needs to run several sequential graph queries per answer (one per cited
  section/case) without the user noticing.
- A recent Indian-judicial-AI research prototype (Falkor-IRAC — graph-constrained generation for
  Indian case law, using FalkorDB as the substrate) demonstrates exactly the pattern this
  product needs for Layer D: **a Verifier Agent that checks whether a valid citation path exists
  in the graph before an answer is returned, with a hard veto (not a soft confidence penalty) on
  unverifiable claims, and explicit abstention after failed revision attempts.** That is the
  correct architecture for `generation/citation_validator.py` — see `DESIGN.md` #6 for the full
  adaptation from case-law IRAC graphs to IP-SAKTI's statute/rule/authority graph.
- Neo4j remains a reasonable alternative if the team already has Neo4j experience — its Graph
  Data Science library and Bloom visualizer are more mature than FalkorDB's tooling — but it
  carries more memory/JVM overhead and most of its advanced tooling sits behind Enterprise/Aura
  tiers, which is a worse fit for a lean MVP budget.

## 6. Safeguards → implementation mapping

| PRD safeguard | Implementation |
|---|---|
| No blogs/marketing as legal authority | Source-tier gating enforced at ingestion (`ingestion/crawl/enumerate_sources.py` only enumerates Tier-1/2/3 domains from `DATA_ORGANIZATION.md` #2) |
| Version every amendment, never overwrite | `corpus/manifest/schema.sql` — new row per version, old row marked `superseded` |
| Access control for restricted sources | `access_type` column in the manifest (`free`/`paid`/`restricted`) gates ingestion and query-time filtering |
| Full audit logging | `backend/middleware/audit_log.py` on every request |
| No paid DB use without logged authorization | Paid connectors (TKDL, Indian Kanoon paid tier) are Stage 3, gated behind an explicit consent flow before any call |
| Prompt-injection filtering | `backend/middleware/prompt_injection_filter.py` |
| "Information, not legal advice" banner | Enforced in `generation/prompt_templates/*.jinja` and the frontend response renderer |
| Escalate high-risk questions | Router in `generation/answer_generator.py` flags infringement/deadline/approval/clinical/ABS-liability/litigation keywords and short-circuits to the human-escalation module |

## 7. Evaluation plan

Run `eval/run_eval.py` against the expert-reviewed gold set (`eval/gold_set/`, 150–300 questions
per `DATA_ORGANIZATION.md` #7) and report:

- Retrieval precision & recall (per jurisdiction, per layer)
- Citation correctness and citation completeness
- Answer groundedness (does every claim trace to a cited, retrieved passage?)
- Product-classification accuracy
- Safe-abstention rate (did the system abstain exactly when it should have?)
- Translation quality (Stage 3)
- End-to-end latency (p50/p95)

Prefer graph-native metrics over lexical ones (BLEU/ROUGE) for anything touching the citation
validator — a well-worded answer citing a non-existent section is a worse outcome than a
clumsily-worded answer with a valid citation chain, and lexical metrics can't tell the difference.

## 8. Staged build order

See `BUILD_PROMPT.md` for the concrete, ordered list of what to build first. In one line: corpus
manifest + Layer A/B/E ingestion → hybrid retrieval → classification flow → citation-grounded
generation with abstention → FastAPI + existing UI mockup wiring → eval harness → (Stage 2) full
KG + Layers C/D → (Stage 3) international + multilingual.
