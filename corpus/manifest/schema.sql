-- IP-SAKTI Sahayak Corpus Manifest
-- This table tracks every authoritative source before ingestion.
-- See DATA_ORGANIZATION.md #3

CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    layer TEXT CHECK(layer IN ('A', 'B', 'C', 'D', 'E')),
    jurisdiction TEXT CHECK(jurisdiction IN ('india', 'international')),
    document_type TEXT, -- e.g., 'Act', 'Rule', 'Treaty', 'Guideline'
    authority TEXT,     -- e.g., 'India Code', 'WIPO Lex', 'NBA'
    access_type TEXT CHECK(access_type IN ('free', 'paid', 'restricted')),
    license_terms TEXT,
    last_fetched DATETIME,
    last_changed DATETIME,
    content_hash TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'fetched', 'parsed', 'embedded', 'error'
    error_log TEXT
);

CREATE INDEX IF NOT EXISTS idx_layer_jurisdiction ON sources(layer, jurisdiction);
