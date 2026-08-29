# Data Organization Document — IP-SAKTI Sahayak

This is a corpus-construction problem before it's a model problem. The MVP is only as
trustworthy as its retrieval corpus — treat this document as the actual Stage-1 deliverable;
the RAG pipeline is comparatively simple once the corpus is clean, chunked, and tagged with
jurisdiction + layer metadata.

## 1. The five data layers (keep as separate collections from day one)

| Layer | Content | Retrieval pattern | Vector store collection |
|---|---|---|---|
| **A. Primary legal text (national)** | Patents Act 1970 + 2024 Rules, GI Act, Trade Marks Act, Designs Act, Copyright Act, Plant Variety Act, Biological Diversity Act 2002 (2023 amendment) + 2024 Rules, Drugs and Cosmetics Act, Drugs and Magic Remedies Act, FSSAI Ayurveda-Aahar regs | Section-level semantic + exact-number lookup | `layer_a_national_statutes` |
| **B. Primary legal text (international)** | TRIPS, CBD, Nagoya Protocol, WIPO GRATK Treaty (2024), PCT, Madrid Protocol, Hague Agreement, Budapest Treaty | Article-level, + per-country accession status | `layer_b_international_treaties` |
| **C. Registry / prior-art records** | TKDL entries (public/authorized only), IP India InPASS, GI registry, Trade Marks registry, WIPO Global Brand/Design DBs | Structured lookup, not semantic search | `layer_c_registries` |
| **D. Case law / precedent** | Section 3(p) rejection rulings, IPAB/Delhi HC IP judgments, WIPO arbitration decisions | Citation-graph traversal, not just full-text | `layer_d_case_law` |
| **E. Regulatory / classification guidance** | AYUSH First Schedule texts, CDSCO classical/proprietary/new-drug criteria, phytopharmaceutical guidelines | Powers the classification decision tree directly | `layer_e_classification_guidance` |

Keeping these as **separate collections from day one** is what makes the India/International
jurisdiction toggle and the layer-aware retrieval filters (`DESIGN.md` #4) a pre-filter instead
of a retrofit. Layers A, B, E are the Stage 1 MVP scope; C and D are Stage 2+.

## 2. Concrete sources, mapped to each layer

### Layer A — National statutes/rules
- **India Code** (`indiacode.nic.in`) — authoritative digital repository for central/state acts.
  No official public API; plan on scraping stable per-act HTML/PDF URLs after first building a
  manifest (never scrape blind — see #3).
- **IP India** (`ipindia.gov.in`) — Patents Act text, 2024 Patent Rules, Designs Act, GI Act,
  Trade Marks Act, all published as PDFs by the administering office. Prefer these over India
  Code where both exist, since they're closer to the source of truth for IP-specific amendments.
- **National Biodiversity Authority** (`nbaindia.org`) — Biological Diversity Act, 2023
  amendment, 2024 ABS Rules, NBA circulars on ABS for AYUSH.
- **FSSAI** (`fssai.gov.in`) — Ayurveda-Aahar regulations, food/nutraceutical classification
  circulars.
- **CDSCO / AYUSH Ministry** (`ayush.gov.in`, `cdsco.gov.in`) — classical/proprietary/
  phytopharmaceutical drug classification rules, First Schedule texts.

### Layer B — International treaties
- **WIPO Lex** (`wipolex.wipo.int`) — full treaty texts, country-by-country accession status,
  links to each member state's implementing legislation. The backbone of the international side
  of the jurisdiction toggle.
- **WTO** (`wto.org`) — TRIPS official text and dispute-panel rulings.
- **CBD Secretariat** (`cbd.int`) and the **ABS Clearing-House** (`absch.cbd.int`) — Nagoya
  Protocol text plus country ABS measures.
- **WIPO IGC** — 2024 GRATK Treaty text and negotiating history.

### Layer C — Registries
- **TKDL** (`tkdl.res.in`) — **important constraint**: TKDL is not openly public. Access is a
  paid subscription with phased opening, and full database access is otherwise restricted to
  national patent offices under NDAs. Build the MVP's "TKDL pointer" as a **link-out / citation
  to how to request access**, never bulk-ingested content — ingesting TKDL text wholesale would
  likely violate its access terms (see #5).
- **IP India's InPASS** — prior-art and granted-patent lookups (structured, queryable).
- **GI Registry** (`ipindia.gov.in/gi`) — registered Ayurvedic GI products.
- **WIPO Global Brand Database / PATENTSCOPE** — international patent/trademark prior art.

### Layer D — Case law
- **Indian Kanoon** — most practical bulk source for Indian IP/patent judgments; documented API
  but commercial/rate-limited terms — budget as a paid-source connector in the staged build.
- **IPAB archive / Delhi High Court IP Division judgments** — published directly by the courts,
  scrapeable as PDFs.

### Layer E — Classification guidance
This layer must be **constructed, not found** — no single authoritative "how to classify a
formulation" corpus exists. It is synthesized from CDSCO guidance documents, Ayurveda
pharmacopoeia standards, and AYUSH circulars, then reviewed by a domain expert (see #4).

## 3. Corpus manifest and chunk metadata schema

Every source is tracked in a manifest before any content is scraped (`corpus/manifest/schema.sql`):

```
source_id, url, layer, jurisdiction, document_type, authority, access_type,
license_terms, last_fetched, last_changed, content_hash, status
```

`access_type` (`free` / `paid` / `restricted`) is what gates the paid-connector safeguard end to
end — it is checked at ingestion time (don't scrape restricted sources) and can be re-checked at
query time (don't surface restricted-source content without a logged authorization).

Every **chunk** (not document) carries its own metadata record, since a single Act produces many
chunks with different section numbers and amendment histories:

```
document_id, title, authority, jurisdiction, document_type, act_or_treaty,
section_rule_article, publication_date, effective_from, effective_to,
amendment_status, source_url, access_date, language, page_number, text,
text_hash, parent_document_id, related_documents
```

This is the metadata the citation validator (`DESIGN.md` #6) checks against — a citation the LLM
proposes is only as good as the fields attached to the chunk it came from.

### Chunking rule: by legal structure, not token count

- Statutes → section / sub-section level
- Treaties → article level
- Case law → paragraph / holding level
- Registries → one chunk per record (no semantic splitting)

Preserve section/clause numbering through parsing — this is what makes citations verifiable
later; a chunk that has lost its section number is useless as legal evidence no matter how
semantically relevant it is.

## 4. The two "must-author" artifacts (cannot be scraped)

### 4.1 Formulation-classification decision logic
Classical vs. proprietary vs. new drug vs. phytopharmaceutical vs. Ayurveda-Aahar vs. cosmetic:
build as a small, hand-curated question-tree + rule table (`classification/decision_tree.yaml`),
cross-checked against CDSCO/AYUSH guidance, then reviewed by a domain expert. This becomes
structured routing metadata the agent uses — not raw RAG text.

### 4.2 Gold evaluation set
Build an expert-reviewed benchmark of **150–300 questions** (Stage 2 target; start with 50–100
for the MVP), covering: classical vs. proprietary formulation, patentability and Section 3(p),
biological-resource access and ABS, TKDL/prior-art searching, Ayurveda-Aahara vs. Ayurvedic drug,
trademark and GI questions, labelling/advertising claims, international filing routes,
export-country regulatory questions, and deliberately ambiguous/unanswerable questions to test
safe abstention.

Each example (`eval/gold_set/gold_qna_template.jsonl`) records:

```
query, language, jurisdiction, product_type, user_facts, expected_classification,
required_sources, gold_passages, gold_citations, expected_answer_points,
unsafe_or_abstain, reviewer_notes
```

At least one Ayurveda/regulatory expert and one IP/legal expert must review the gold answers —
this cannot be generated purely by scraping or by the model itself, and it's the artifact judges
(or, post-hackathon, users) will actually use to score the system.

## 5. Access-tier safeguards (applies across all layers)

| Tier | Examples | Rule |
|---|---|---|
| Free, official | India Code, IP India, NBA, FSSAI, WIPO Lex, CBD/Nagoya | Ingest freely; still respect robots.txt / rate limits |
| Paid, ToS-gated | Indian Kanoon bulk API, premium WIPO tiers | Stage 2/3; gated behind explicit, logged user authorization before any call |
| Restricted / NDA-only | Full TKDL database | **Never bulk-ingested.** Build a link-out / "how to request access" pointer only |

## 6. Knowledge graph ontology (see `knowledge_graph/schema/ontology.yaml`)

**Node types:** Act, Treaty, Section, Authority, Registry, ProductCategory, Ingredient,
BiologicalResource, TraditionalKnowledgeSource, Country, ExportRequirement, and (Stage 2+) CaseLaw.

**Relationship types (Stage 1):** `CONTAINS` (Act→Section), `IMPLEMENTS` (national law→treaty
obligation), `ADMINISTERED_BY` (Registry/ProductCategory→Authority), `REQUIRES_LICENSING_FROM`
(ProductCategory→Authority), `DERIVED_FROM` (Ingredient→BiologicalResource), `SUBJECT_TO`
(BiologicalResource→Section, i.e. an ABS obligation), `APPLIES_IN` (ExportRequirement→Country).

**Relationship types (Stage 2+, case law only):** `CITES`, `OVERRULES`, `DISTINGUISHES`, and the
two conflict-aware relationships that matter most for honest output — `CONFLICTS_WITH`
(coordinate-bench disagreements, per-incuriam citations, over-broad factual distinctions) and
`RESOLVED_BY` (a larger/full/constitutional bench resolution). See `DESIGN.md` #6 for how these
feed the citation validator's CONFLICT status.

Act→Section edges are near-free to build directly from chunk metadata during ingestion.
Ingredient→BiologicalResource and ProductCategory→Authority edges need either LLM-assisted
extraction with provenance tagging (`knowledge_graph/extract_entities.py` — never invent an edge
the source doesn't support, leave it unextracted instead) or manual curation for the highest-value,
lowest-volume relationships (e.g. the classification-to-authority routing table).

## 7. Versioning and freshness

- Every amendment is a **new row/document version** in the manifest — the old version's `status`
  becomes `superseded`, it is never overwritten. This is what lets an answer be reproduced using
  the law in force at a particular date.
- A diffing job (`ingestion/diff_tracker.py`) hashes each source page, re-crawls periodically, and
  flags changes — the 2024 Patent Rules, 2024 Biodiversity Rules, and 2024 GRATK Treaty are all
  recent enough that treating the corpus as static would go stale fast.
- Re-embedding is scoped to changed documents only, not a full corpus rebuild, by tracking
  `content_hash` per source and per chunk.

## 8. Staged corpus build order

1. **MVP corpus**: Layers A + B only, scraped from India Code, IP India, WIPO Lex, NBA, FSSAI —
   all free, no permission gating. Ship jurisdiction-tagged citation-grounded Q&A on this alone
   first.
2. **Add registries + case law**: InPASS, GI registry, Indian Kanoon (free tier/trial) for
   prior-art and precedent grounding.
3. **Add the knowledge graph + agentic layer**: link entities (Act → Section → related treaty
   article → related case) once enough structured metadata exists from steps 1–2 to build edges.
4. **Paid connectors last**: TKDL subscription and any premium Indian Kanoon/WIPO tiers, gated
   behind the explicit-permission flow — a good post-hackathon roadmap slide rather than a
   live-demo dependency, since paid access + logging infrastructure is non-trivial to stand up in
   hackathon time.

## 9. One structural recommendation

Build the corpus-manifest table (`corpus/manifest/schema.sql`) **before writing any scraping
code**. It becomes the backbone for: (a) the version-tracking requirement, (b) the paid-vs-free
access logging requirement, and (c) reproducibility for judges/users — you can show exactly where
every citation in a demo answer came from, which is the entire point of the product.
