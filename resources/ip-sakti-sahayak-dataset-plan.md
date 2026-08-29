# IP-SAKTI Sahayak — Data Sourcing & Dataset-Building Plan

This is a corpus-construction problem before it's a model problem. The MVP is only as trustworthy as the retrieval corpus, so treat "build the dataset" as the actual SIH deliverable in phase 1 — the RAG pipeline itself is comparatively simple once the corpus is clean, chunked, and tagged with jurisdiction + source metadata.

## 1. What kind of data you actually need (5 layers)

| Layer | Content | Why it's structurally different |
|---|---|---|
| **A. Primary legal text (national)** | Patents Act 1970 + 2024 Rules, GI Act, Trade Marks Act, Designs Act, Copyright Act, Plant Variety Act, Biological Diversity Act 2002 (2023 amendment) + 2024 Rules, Drugs and Cosmetics Act, Drugs and Magic Remedies Act, FSSAI Ayurveda-Aahar regs | Static, versioned, needs section-level chunking with amendment history |
| **B. Primary legal text (international)** | TRIPS, CBD, Nagoya Protocol, WIPO GRATK Treaty (2024), PCT, Madrid Protocol, Hague Agreement, Budapest Treaty | Treaty text + accession/ratification status per country matters |
| **C. Registry / prior-art records** | TKDL entries, IP India patent database (InPASS), GI registry, Trade Marks registry, WIPO Global Brand/Design DBs | Structured records, not prose — different retrieval pattern (lookup, not semantic search) |
| **D. Case law / precedent** | Patent office rulings on §3(p) rejections, IPAB/Delhi HC IP judgments, WIPO arbitration decisions | Needs citation graph, not just full text |
| **E. Regulatory/classification guidance** | AYUSH First Schedule texts, CDSCO classical/proprietary/new-drug criteria, phytopharmaceutical guidelines | This is what powers your formulation-classification flow — arguably the highest-value, hardest-to-source layer |

Keep these five layers as **separate collections** in your vector store / knowledge graph from day one — it's what lets you implement the jurisdiction toggle cleanly later instead of retrofitting it.

## 2. Concrete sources, mapped to each layer

**A. National statutes/rules**
- **India Code (indiacode.nic.in)** — the authoritative digital repository for all central/state acts and subordinate legislation. No official public API exists; it's built for human browsing, so plan on **scraping the HTML/PDF pages** (each act has a stable URL you can enumerate) rather than expecting a feed. Third-party wrappers exist but aren't official — treat them as convenience, not authority.
- **IP India (ipindia.gov.in)** — Patents Act text, the 2024 Patent Rules, Designs Act, GI Act, Trade Marks Act — all published as PDFs directly by the office that administers them. Prefer these over India Code where both exist, since they're closer to the source of truth for IP-specific amendments.
- **National Biodiversity Authority (nbaindia.org)** — Biological Diversity Act, 2023 amendment, 2024 ABS Rules, and NBA guidelines/circulars on ABS for AYUSH.
- **FSSAI (fssai.gov.in)** — Ayurveda-Aahar regulations, food/nutraceutical classification circulars.
- **CDSCO / AYUSH Ministry (ayush.gov.in, cdsco.gov.in)** — classical/proprietary/phytopharmaceutical drug classification rules, First Schedule texts.

**B. International treaties**
- **WIPO Lex (wipolex.wipo.int)** — the single best source: full treaty texts, country-by-country accession status, and links to each member state's implementing legislation. This is your backbone for the "international" side of the jurisdiction toggle.
- **WTO (wto.org)** — TRIPS official text and dispute-panel rulings.
- **CBD Secretariat (cbd.int)** and the **ABS Clearing-House (absch.cbd.int)** — Nagoya Protocol text plus country ABS measures, which you'll need for the ABS-compliance helper specifically.
- **WIPO IGC** page — for the 2024 GRATK Treaty text and negotiating history (useful for grounding "why" answers).

**C. Registries**
- **TKDL (tkdl.res.in)** — important caveat confirmed by current sources: TKDL is **not openly public**. Access is via a **paid subscription with phased opening**, and full database access is otherwise restricted to ~16–17 national patent offices under non-disclosure agreements. Build your MVP's "TKDL pointer" as a *link-out / citation to how to request access*, not as bulk-ingested TKDL content — ingesting TKDL text wholesale would likely violate its access terms. This matches the problem statement's own instruction to use paid sources "only with explicit, logged permission."
- **IP India's InPASS / patent search** — for prior-art and granted-patent lookups (structured, queryable).
- **GI Registry (ipindia.gov.in/gi)** — registered Ayurvedic GI products list.
- **WIPO Global Brand Database / PATENTSCOPE** — for international patent and trademark prior-art search.

**D. Case law**
- **Indian Kanoon** — the most practical bulk source for Indian IP/patent judgments; it has a documented API but commercial/rate-limited terms — budget for that as a paid-source connector in your staged build, exactly as the problem statement's roadmap anticipates.
- **IPAB archive / Delhi High Court IP Division judgments** — published directly by the courts, scrapeable as PDFs.

**E. Classification guidance**
- This is the layer you'll likely need to **construct rather than find**, since no single authoritative "how to classify a formulation" corpus exists — it's synthesized from CDSCO guidance documents, the Ayurveda pharmacopoeia standards, and AYUSH circulars. Plan for a manual curation pass here with an actual mentor/domain expert (your problem statement calls for "human IP facilitator" escalation anyway — get a domain expert to sanity-check this layer before the demo).

## 3. How to actually fetch it

1. **Enumerate before you scrape.** For India Code and IP India, first crawl the site structure (act lists, section indexes) to build a manifest of URLs — don't scrape blind. Store the manifest as your first dataset artifact; it's also your update-tracking mechanism later.
2. **PDF-first pipeline.** Most primary sources here are PDFs, not clean HTML. Use a PDF-to-structured-text pipeline (e.g., `pdfplumber`/`PyMuPDF` for digital PDFs; OCR fallback like Tesseract for scanned gazette notifications) and preserve section/clause numbering during extraction — this is what makes citations verifiable later.
3. **Chunk by legal structure, not by token count.** Chunk at the section/sub-section level for statutes, article level for treaties, and paragraph/holding level for case law. Attach metadata to every chunk: `{source, jurisdiction, act/treaty name, section, version/amendment date, url, retrieval_date}`. This metadata is what your citation + confidence-indicator features run on.
4. **Version-track from day one.** Since the 2024 Patent Rules, 2024 Biodiversity Rules, and the 2024 GRATK Treaty are all recent, build a simple diffing job (hash each source page, re-crawl periodically, flag changes) rather than treating the corpus as static — the problem statement explicitly requires the corpus to "stay current as the law changes."
5. **Rate-limit and respect robots.txt / ToS**, especially for Indian Kanoon and any WIPO databases — you'll want these as durable data partners post-hackathon, not sources you get blocked from during the demo.

## 4. Building the "must-create" parts of the dataset

Two things in this problem statement can't just be scraped — they have to be authored/curated:

- **Formulation-classification decision logic** (classical vs proprietary vs new drug vs phytopharmaceutical vs Ayurveda-Aahar vs cosmetic): build this as a small, hand-curated **question-tree + rule table**, cross-checked against CDSCO/AYUSH guidance, then have a domain expert review it. This becomes structured metadata your agent uses for routing, not raw RAG text.
- **Gold evaluation set** for your accuracy/citation-correctness/abstention metrics: hand-write 50–100 Q&A pairs across both jurisdictions with verified correct citations, including deliberately out-of-scope or ambiguous questions to test safe abstention. You cannot get this from scraping — it has to be authored by your team (ideally with a legal/AYUSH advisor), and it's the artifact judges will actually use to score you.

## 5. Staged build order (matches the problem statement's own roadmap)

1. **MVP retrieval corpus**: Layers A + B only (national + international statutes/treaties), scraped from India Code, IP India, WIPO Lex, NBA, FSSAI — all free, no permission gating. Ship jurisdiction-tagged citation-grounded Q&A on this alone first.
2. **Add registries + case law**: InPASS, GI registry, Indian Kanoon (free tier or trial) for prior-art and precedent grounding.
3. **Add the knowledge graph + agentic layer**: link entities (Act → Section → related treaty article → related case) once you have enough structured metadata from steps 1–2 to build edges.
4. **Paid connectors last**: TKDL subscription and any premium Indian Kanoon/WIPO tiers, gated behind the explicit-permission flow the problem statement requires — this is honestly a good thing to leave for a post-hackathon roadmap slide rather than the live demo, since paid access + logging infrastructure is non-trivial to stand up in hackathon time.

## 6. One structural recommendation

Given the volume, I'd build a small **corpus-manifest database** (even just a SQLite/Postgres table: `source_id, url, layer, jurisdiction, last_fetched, last_changed, license/access_type`) before writing any scraping code. It becomes the backbone for (a) your version-tracking requirement, (b) your paid-vs-free access logging requirement, and (c) reproducibility for the judges — you can show exactly where every citation in a demo answer came from.
