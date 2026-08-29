import sqlite3
from datetime import datetime
from typing import List, Optional, Dict

class ManifestManager:
    """
    Manager for the IP-SAKTI Sahayak source manifest.
    Handles tracking of legal documents across different layers and jurisdictions.
    """
    def __init__(self, db_path: str = "data/manifest.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        # Import schema from the sql file
        with open("corpus/manifest/schema.sql", "r") as f:
            schema = f.read()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)

    def add_source(self, source_data: Dict):
        """Adds a new source to the manifest."""
        query = """
        INSERT OR IGNORE INTO sources 
        (source_id, url, layer, jurisdiction, document_type, authority, access_type) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, (
                source_data['source_id'],
                source_data['url'],
                source_data['layer'],
                source_data['jurisdiction'],
                source_data.get('document_type'),
                source_data.get('authority'),
                source_data.get('access_type', 'free')
            ))

    def update_status(self, source_id: str, status: str, error_log: Optional[str] = None):
        """Updates the processing status of a source."""
        query = "UPDATE sources SET status = ?, error_log = ?, last_fetched = ? WHERE source_id = ?"
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, (status, error_log, datetime.now(), source_id))

    def get_pending_sources(self, layer: Optional[str] = None, jurisdiction: Optional[str] = None) -> List[Dict]:
        """Retrieves sources that need processing."""
        query = "SELECT * FROM sources WHERE status = 'pending'"
        params = []
        
        if layer:
            query += " AND layer = ?"
            params.append(layer)
        if jurisdiction:
            query += " AND jurisdiction = ?"
            params.append(jurisdiction)
            
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    # Simple test
    import os
    os.makedirs("data", exist_ok=True)
    manager = ManifestManager()
    print("Manifest initialized successfully.")
