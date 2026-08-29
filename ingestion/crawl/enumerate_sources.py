from corpus.manifest.manager import ManifestManager
import uuid

def enumerate_sources():
    """
    Initializes the manifest with target sources for Stage 1 (Layers A, B, and E).
    In a production setting, this would crawl landing pages to find all PDFs/HTML.
    For MVP, we seed it with the authoritative repositories mentioned in DATA_ORGANIZATION.md.
    """
    manager = ManifestManager()
    
    # Define seed sources for Stage 1
    seed_sources = [
        # LAYER A - National Statutes (India)
        {
            "authority": "India Code",
            "layer": "A",
            "jurisdiction": "india",
            "document_type": "Act",
            "url": "https://indiacode.nic.in/",
            "access_type": "free"
        },
        {
            "authority": "IP India",
            "layer": "A",
            "jurisdiction": "india",
            "document_type": "Act/Rules",
            "url": "https://ipindia.gov.in/",
            "access_type": "free"
        },
        {
            "authority": "National Biodiversity Authority",
            "layer": "A",
            "jurisdiction": "india",
            "document_type": "Act/Rules",
            "url": "https://nbaindia.org/",
            "access_type": "free"
        },
        {
            "authority": "FSSAI",
            "layer": "A",
            "jurisdiction": "india",
            "document_type": "Regulations",
            "url": "https://fssai.gov.in/",
            "access_type": "free"
        },
        {
            "authority": "AYUSH Ministry",
            "layer": "A",
            "jurisdiction": "india",
            "document_type": "Guidelines",
            "url": "https://ayush.gov.in/",
            "access_type": "free"
        },
        # LAYER B - International Treaties
        {
            "authority": "WIPO Lex",
            "layer": "B",
            "jurisdiction": "international",
            "document_type": "Treaty",
            "url": "https://wipolex.wipo.int/",
            "access_type": "free"
        },
        {
            "authority": "WTO",
            "layer": "B",
            "jurisdiction": "international",
            "document_type": "Agreement",
            "url": "https://www.wto.org/",
            "access_type": "free"
        },
        {
            "authority": "CBD Secretariat",
            "layer": "B",
            "jurisdiction": "international",
            "document_type": "Convention",
            "url": "https://www.cbd.int/",
            "access_type": "free"
        },
        # LAYER E - Classification Guidance
        {
            "authority": "CDSCO",
            "layer": "E",
            "jurisdiction": "india",
            "document_type": "Guideline",
            "url": "https://cdsco.gov.in/",
            "access_type": "free"
        },
    ]

    print(f"Seeding manifest with {len(seed_sources)} primary sources...")
    
    for src in seed_sources:
        # Generate a unique source_id based on authority and layer
        src['source_id'] = f"src_{src['layer']}_{src['authority'].lower().replace(' ', '_')}"
        manager.add_source(src)
        print(f"Added: {src['source_id']} -> {src['url']}")

    print("Manifest seeding complete.")

if __name__ == "__main__":
    enumerate_sources()
