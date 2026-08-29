# IP-SAKTI Sahayak: Implementation Brief and Research Resources

## 1. What You Should Build

**IP-SAKTI Sahayak** should be designed as a citation-grounded legal and regulatory information assistant, not as a general chatbot. Its purpose is to help Ayurveda practitioners, researchers, startups, MSMEs and cultivators identify:

1. The type of product or formulation.
2. The Indian or international regulations that apply.
3. The appropriate intellectual-property route.
4. Whether biodiversity or access-and-benefit-sharing obligations arise.
5. The official forms, registries, databases or authorities to consult.

The system should always display the selected jurisdiction prominently:

- **India:** Patents, GI, trademarks, designs, copyright, plant varieties, the Biological Diversity Act, AYUSH drug rules, FSSAI Ayurveda-Aahara rules and advertising requirements.
- **International:** TRIPS, CBD, the Nagoya Protocol, the WIPO GRATK Treaty, PCT, Madrid, Hague, Budapest Treaty and the regulations of the selected export country.

The system must not combine Indian and international rules into one answer. It should return separate sections such as **India**, **International**, **Assumptions**, **Sources** and **When to consult a professional**.

## 2. Recommended Architecture

### A. Query and Formulation Classification

Begin with a short decision flow:

- Is the product based on an authoritative classical Ayurveda text?
- Is it a proprietary or modified formulation?
- Is it intended to be a drug, food, cosmetic or wellness product?
- Does it use an Indian biological resource or associated traditional knowledge?
- Is it being sold only in India or exported?
- What claims appear on the label or advertisement?

The classifier can route the user to categories such as:

- Classical Ayurvedic medicine.
- Patent or proprietary medicine.
- New or non-classical drug.
- Phytopharmaceutical.
- Ayurveda-Aahara or nutraceutical.
- Cosmetic.
- Research material or raw biological resource.

This step is essential because the same ingredient may have different obligations depending on its formulation, intended use and product claims.

### B. Hybrid Retrieval System

Use a **hybrid RAG pipeline**, rather than vector search alone:

1. Query normalization and language detection.
2. Translation or transliteration into a canonical search language.
3. Metadata filtering by jurisdiction, IP category, product category, authority, effective date and document type.
4. BM25 or keyword retrieval for exact section and rule numbers.
5. Multilingual dense retrieval for semantic similarity.
6. Cross-encoder reranking.
7. Optional knowledge-graph lookup for relationships such as Act -> section -> rule and product category -> licensing authority.
8. Answer generation using only retrieved evidence.
9. Citation and confidence validation.

### C. Citation-Aware Answer Generation

Each answer should cite:

- Document title.
- Authority.
- Section, rule, article or paragraph.
- Version or notification date.
- Official URL or database identifier.
- Retrieval timestamp.

Do not allow the model to produce a legal proposition without retrieved evidence. If no authoritative evidence is found, it should say:

> I could not verify this proposition from the indexed authoritative sources. Please consult an IP professional or the relevant authority.

The system should distinguish between:

- **Directly supported:** explicitly stated in the source.
- **Reasoned interpretation:** inferred from multiple sources.
- **Unverified:** not suitable for a definitive answer.

### D. Compliance and Escalation Modules

Useful modules include:

- IP-route recommender.
- Patent novelty and TK prior-art pointer.
- ABS checklist.
- Product-classification assistant.
- Export-country compliance checklist.
- Label and advertising claim checker.
- Official-registry search launcher.
- Human IP facilitator escalation.

The assistant should not make a final patentability, infringement, licensing or regulatory-approval determination. It should provide an evidence-based preliminary assessment.

## 3. Suggested Development Stages

### Stage 1: Citation-Grounded MVP

Implement:

- India-only jurisdiction.
- English plus one or two Indian languages.
- Product-classification questionnaire.
- Hybrid BM25 and vector retrieval.
- Section-level citations.
- Patents, biodiversity, AYUSH and Ayurveda-Aahara sources.
- Confidence score and abstention mechanism.

### Stage 2: Knowledge Graph and Evaluation

Add entities and relationships for:

- Acts.
- Rules.
- Sections.
- Authorities.
- Product categories.
- Ingredients.
- Biological resources.
- Traditional knowledge sources.
- Registries.
- Treaties.
- Countries and export requirements.

Evaluate:

- Retrieval precision and recall.
- Citation correctness.
- Citation completeness.
- Answer groundedness.
- Product-classification accuracy.
- Safe abstention.
- Translation quality.
- Latency.

### Stage 3: International and Multilingual Expansion

Add:

- WIPO systems.
- PCT, Madrid, Hague and Budapest resources.
- CBD and Nagoya Protocol material.
- WIPO GRATK Treaty material.
- Selected export markets such as the United States, European Union, United Kingdom, Australia and Japan.
- Bhashini-based translation, speech recognition and text-to-speech.

## 4. Relevant Research Papers and Projects

| Paper or project | Relevance to IP-SAKTI |
|---|---|
| [LegalBench-RAG: A Benchmark for Retrieval-Augmented Generation in the Legal Domain](https://arxiv.org/abs/2408.10343) | Relevant to legal retrieval, precise passage extraction, citation generation and evaluation. |
| [Benchmarking Retrieval-Augmented Generation for Legal Documents](https://arxiv.org/html/2603.11772v1) | Provides a legal benchmark with clause-level references, useful for multilingual and citation-focused evaluation. |
| [Legal RAG Bench: An End-to-End Benchmark for Legal RAG](https://arxiv.org/abs/2603.01710) | Useful for separating retrieval errors from generation errors and evaluating supporting passages and long-form answers. |
| [Retrieval Augmented Generation Framework for the Nepali Legal Domain Question Answering](https://arxiv.org/abs/2606.07523) | Relevant to low-resource and multilingual legal question answering. |
| [Benchmarking KG-based RAG Systems: A Case Study of Legal Documents](https://scholar.ui.ac.id/en/publications/benchmarking-kg-based-rag-systems-a-case-study-of-legal-documents/) | Relevant to knowledge-graph-based RAG and comparison with standard RAG. |
| [Domain-Partitioned Hybrid RAG for Legal Reasoning](https://www.alphaxiv.org/abs/2602.23371v1) | Relevant to routing questions among separate legal sub-corpora and combining hybrid retrieval, knowledge graphs and agentic orchestration. |
| [Multi-Lingual Legal Document Assistant](https://ijirt.org/publishedpaper/IJIRT200369_PAPER.pdf) | Useful for multilingual document retrieval and bounded-context answer generation. |
| [Protecting AYUSH as Traditional Knowledge in the AI Era](https://www.cnlu.ac.in/wp-content/uploads/2026/01/Protecting-AYUSH-As-A-Traditional-Knowledge-In-The-AI-Era-An-Intersection-With-Innovation.pdf) | Closely aligned with the relationship between AYUSH, traditional knowledge and AI. |
| [Safeguarding Traditional Medical Knowledge: An Evaluation of TKDL](https://www.ijllr.com/post/safeguarding-traditional-medical-knowledge-an-evaluation-of-the-traditional-knowledge-digital-libra) | Useful for discussing TKDL as a defensive prior-art mechanism. |

For the literature review, divide the research into:

1. Legal question answering.
2. Citation-grounded and retrieval-focused RAG.
3. Multilingual or low-resource legal NLP.
4. Digital preservation and protection of traditional medical knowledge.

## 5. Sources for Building the RAG Corpus

Use a source hierarchy. Official primary sources should receive the highest trust score.

### Tier 1: Indian Government and Statutory Sources

- [India Code](https://www.indiacode.nic.in/): Acts, amended legislation and official statutory text.
- [IP India](https://ipindia.gov.in/): Patents, designs, trademarks, GI, acts, rules, forms, manuals and guidelines.
- [IP India AYUSH-related invention guidelines](https://www.ipindia.gov.in/frontend/pdf/patents/guidelines/Guidelines%20for%20Examination%20of%20Ayush%20Related%20Inventions.pdf): Patent eligibility, prior-art searching and Ayurveda-related inventions.
- [Ministry of Ayush](https://ayush.gov.in/): Drug-related rules, pharmacopoeial information, policies and notifications.
- [FSSAI Regulations](https://fssai.gov.in/food-law/regulations): Ayurveda-Aahara regulations, notifications, advisories and labelling requirements.
- National Biodiversity Authority: ABS regulations, access applications, benefit-sharing rules and notifications.
- Plant Varieties Protection and Farmers' Rights Authority: Plant-variety registration, farmers' rights and benefit-sharing material.
- Copyright Office: Copyright rules, registration information and official notices.
- Controller General of Patents, Designs and Trade Marks: Official patent, trademark, GI and design records.

### Tier 2: Traditional Knowledge and Ayurveda Sources

- Traditional Knowledge Digital Library: Use public material and authorized access only. Restricted records must not be scraped or redistributed.
- Ayush Research Portal: Ayurveda-related research publications.
- FRLHT Indian Medicinal Plants Database: Plant names, medicinal uses and botanical information.
- [e-Charak](https://echarak.ayush.gov.in/): Medicinal-plant trade and market information.
- National Medicinal Plants Board: Cultivation, medicinal-plant and market resources.
- Central Council for Research in Ayurvedic Sciences: Research publications and clinical or pharmacological material.
- Ayurvedic Pharmacopoeia and Formulary publications: Use licensed or officially released copies, preserving edition and page metadata.

### Tier 3: International Sources

- [WIPO PATENTSCOPE](https://www.wipo.int/en/web/patentscope): PCT applications, patent-office records and non-patent literature.
- [WIPO Global Brand Database](https://www.wipo.int/en/web/global-brand-database): International trademarks, appellations of origin, GIs and participating national collections.
- [WIPO IP Portal](https://ipportal.wipo.int/): International IP legal and procedural information.
- WIPO Lex: Treaties, national laws and regulations.
- WIPO GRATK Treaty material: Treaty text, explanatory material and implementation updates.
- WTO TRIPS resources: Agreement text, Council documents and notifications.
- CBD and Nagoya Protocol portals: Treaty text, national ABS measures and implementation information.
- PCT, Madrid, Hague and Budapest Treaty resources: Official procedures, forms and country participation.
- National patent and trademark offices of target export markets.

## 6. Dataset Design

Do not create only question-answer pairs. Create a versioned corpus with fields such as:

```text
document_id
title
authority
jurisdiction
document_type
act_or_treaty
section_rule_article
publication_date
effective_from
effective_to
amendment_status
source_url
access_date
language
page_number
text
text_hash
parent_document_id
related_documents
```

For supervised evaluation, create examples with:

```text
query
language
jurisdiction
product_type
user_facts
expected_classification
required_sources
gold_passages
gold_citations
expected_answer_points
unsafe_or_abstain
reviewer_notes
```

Build an expert-reviewed benchmark of approximately 150–300 questions covering:

- Classical formulation versus proprietary medicine.
- Patentability and Section 3(p).
- Biological-resource access and ABS.
- TKDL and prior-art searching.
- Ayurveda-Aahara versus Ayurvedic drug.
- Trademark and GI questions.
- Labelling and advertising claims.
- International filing routes.
- Export-country regulatory questions.
- Ambiguous or unanswerable questions.

Have at least one Ayurveda or regulatory expert and one IP or legal expert review the gold answers. Keep the corpus versioned so an answer can be reproduced using the law in force at a particular date.

## 7. Important Implementation Safeguards

- Never treat blogs, marketing pages or AI-generated summaries as primary legal authority.
- Store every amendment as a new version instead of overwriting the old document.
- Use document-level and passage-level access control for restricted TKDL or paid resources.
- Log retrieval results, model version, prompt version, citations and selected jurisdiction.
- Do not use paid databases without explicit user authorization.
- Add prompt-injection filtering for uploaded documents and web content.
- Encrypt personal and business information.
- Include deletion, retention and audit controls aligned with applicable data-protection requirements.
- Display “information, not legal advice” in every substantive answer.
- Escalate high-risk questions involving infringement, patent deadlines, regulatory approval, clinical claims, ABS liability or litigation.

## Recommended Hackathon Scope

The strongest hackathon implementation is a small but reliable India-focused MVP consisting of:

- A formulation-classification flow.
- Hybrid legal retrieval.
- Official-source citations.
- ABS and TKDL pointers.
- Multilingual query support.
- Confidence scoring.
- Strong abstention and human-escalation mechanisms.

This is more defensible and easier to evaluate than attempting to cover every country and every Ayurveda product category in the first version.
