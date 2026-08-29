# Product Requirements Document — IP-SAKTI Sahayak (AyurIP Guardian)

## 0. Document control

| | |
|---|---|
| Product | IP-SAKTI Sahayak — citation-grounded IP & regulatory assistant for Ayurveda |
| UI codename | AyurIP Guardian (existing static mockup: `frontend/ayurip-guardian-mockup.html`) |
| Context | Hackathon (SIH-style) problem statement, staged toward a real MVP |
| Companion docs | `TRD.md` (how it's built) · `DESIGN.md` (architecture + UX) · `DATA_ORGANIZATION.md` (corpus + KG) · `BUILD_PROMPT.md` (the build order) |

## 1. Problem statement

Ayurveda practitioners, researchers, startups, MSMEs and cultivators routinely need to answer five questions about a product or formulation, and today have no single place to get a trustworthy, sourced answer:

1. What type of product/formulation is this?
2. Which Indian or international regulations apply?
3. What is the appropriate IP route (patent, GI, trademark, design, copyright, plant variety, trade secret)?
4. Do biodiversity / access-and-benefit-sharing (ABS) obligations arise?
5. Which official forms, registries, databases or authorities should they consult?

General-purpose chatbots answer these questions fluently and **wrongly often enough to be dangerous** — a confidently-stated but fabricated citation, or an Indian rule applied to an export market, can cost a founder a patent filing or trigger a compliance breach.

## 2. Product vision

IP-SAKTI Sahayak is **not a general chatbot**. It is a citation-grounded legal and regulatory research assistant, scoped narrowly and honestly:

- Every substantive claim is backed by a retrieved, cited, dated source.
- Every answer states its jurisdiction explicitly and never blends India and International rules in one answer.
- Every answer distinguishes what is *directly supported*, *reasoned interpretation*, and *unverified* — and abstains rather than guesses when evidence is insufficient.
- The system routes, it does not decide: it never issues a final patentability, infringement, licensing, or regulatory-approval determination. It hands off to a human IP facilitator for anything high-stakes.

## 3. Users and jobs-to-be-done

| User | Job to be done |
|---|---|
| Individual Ayurveda practitioner / cultivator | "Can I do anything to protect my grandmother's formulation?" |
| Startup / MSME founder | "What IP route and what regulatory filings does my product need before I sell it?" |
| Researcher | "Is this compound/use already in TKDL or patented? What's the prior-art landscape?" |
| Exporter | "What changes about my compliance obligations if I sell in the EU/US instead of only India?" |
| Domain/legal reviewer (internal) | Curate and sign off the classification decision tree and gold evaluation set. |

## 4. Core functional requirements

### 4.1 Jurisdiction-first design (hard requirement)
- A persistent, prominent India ⇄ International toggle (already prototyped in the UI mockup).
- The system **must not** combine Indian and international rules in a single answer. Output is always structured as separate sections: **India**, **International**, **Assumptions**, **Sources**, **When to consult a professional**.
- India covers: Patents, GI, trademarks, designs, copyright, plant varieties, the Biological Diversity Act, AYUSH drug rules, FSSAI Ayurveda-Aahara rules, advertising requirements.
- International covers: TRIPS, CBD, the Nagoya Protocol, the WIPO GRATK Treaty, PCT, Madrid, Hague, Budapest Treaty, and the regulations of the user-selected export country.

### 4.2 Formulation / query classification
A short decision flow (see `classification/decision_tree.yaml`) that routes every query into one of:
classical Ayurvedic medicine · patent or proprietary medicine · new/non-classical drug · phytopharmaceutical · Ayurveda-Aahara/nutraceutical · cosmetic · research material or raw biological resource.

This matters because the *same ingredient* carries different obligations depending on formulation, intended use, and label claims — classification is not a nicety, it's load-bearing for correctness.

### 4.3 Citation-aware answer generation
Every answer must cite: document title, authority, section/rule/article/paragraph, version or notification date, official URL or database identifier, and retrieval timestamp.

The model must never state a legal proposition without retrieved evidence backing it. If no authoritative evidence is found, the system returns, verbatim in spirit:

> "I could not verify this proposition from the indexed authoritative sources. Please consult an IP professional or the relevant authority."

Every claim is labeled one of:
- **Directly supported** — explicitly stated in a source.
- **Reasoned interpretation** — inferred by combining multiple sources.
- **Unverified** — not suitable for a definitive answer.

### 4.4 Compliance and escalation modules
- IP-route recommender
- Patent novelty / TK prior-art pointer (TKDL link-out, not bulk ingestion — see `DATA_ORGANIZATION.md` #5)
- ABS checklist
- Product-classification assistant
- Export-country compliance checklist
- Label and advertising claim checker
- Official-registry search launcher (InPASS, GI Registry, WIPO Global Brand DB)
- Human IP facilitator escalation

### 4.5 Multilingual access
English plus one or two Indian languages at MVP (Stage 1), expanding toward Bhashini-based translation/ASR/TTS and full multilingual coverage at Stage 3. The existing mockup already advertises "Multilingual (11 Languages)" — treat that as the Stage 3 target, not the MVP bar.

## 5. Non-functional / safeguard requirements (non-negotiable, see `TRD.md` #6)

- Never treat blogs, marketing pages, or AI-generated summaries as primary legal authority.
- Version every amendment as a new document — never overwrite.
- Document- and passage-level access control for restricted/paid sources (TKDL, paid case-law databases).
- Log retrieval results, model version, prompt version, citations, and selected jurisdiction for every answer.
- No paid database use without explicit, logged user authorization.
- Prompt-injection filtering on uploaded documents and web content.
- Encrypt personal/business information; support deletion, retention, and audit controls.
- Display "information, not legal advice" on every substantive answer.
- Escalate high-risk questions (infringement, patent deadlines, regulatory approval, clinical claims, ABS liability, litigation) to a human rather than answering definitively.

## 6. Out of scope (explicitly, for the MVP)

- Final legal determinations of any kind (patentability, infringement, licensing, regulatory approval).
- Bulk ingestion of TKDL or any other access-restricted/paid corpus without a logged permission flow.
- Case-law reasoning and precedent-conflict detection (Layer D) — Stage 2+, and even then behind its own verification layer (see `DESIGN.md` #6).
- Full 22-language Indic coverage, voice interfaces — Stage 3.
- Countries beyond the MVP's chosen 1–2 pilot export markets — Stage 3.

## 7. Success metrics (see `TRD.md` #7 for the measurement plan)

| Metric | Why it matters here |
|---|---|
| Citation correctness & completeness | The entire value proposition is "don't trust a chatbot that fabricates law" |
| Safe abstention rate | A confident wrong answer is worse than "I don't know" in this domain |
| Product-classification accuracy | Everything downstream (which rules apply) depends on this being right |
| Retrieval precision/recall per jurisdiction | Jurisdiction bleed is a correctness bug, not a UX nit |
| Latency | Judged live demo + real usability both need this to feel responsive |
| Human-escalation precision | Escalating too much erodes trust in the tool; too little is a liability |

## 8. Staged roadmap (detail in `BUILD_PROMPT.md` and `TRD.md` #8)

1. **Stage 1 — Citation-grounded MVP.** India-only, English + 1–2 Indian languages, hybrid BM25+vector retrieval, section-level citations, Layers A/B/E only, confidence scoring + abstention.
2. **Stage 2 — Knowledge graph + evaluation.** Full entity/relationship graph, registries + case law (Layers C/D), the graph-constrained citation validator, the 150–300 question expert-reviewed benchmark.
3. **Stage 3 — International + multilingual expansion.** WIPO/PCT/Madrid/Hague/Budapest, CBD/Nagoya/GRATK, selected export markets, Bhashini-based translation/ASR/TTS, paid connectors (TKDL subscription) behind the explicit-permission flow.

The strongest hackathon deliverable is a small, reliable India-focused MVP — not partial coverage of everything. See `BUILD_PROMPT.md` for the concrete build order that enforces this.
