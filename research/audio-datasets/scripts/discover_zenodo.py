#!/usr/bin/env python3
"""
Discovery script for Zenodo API querying dataset records for medical speech,
consultation audio, clinical dialogue, and speech benchmarks.
Saves raw API responses to research/audio-datasets/raw_responses/
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
import requests

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw_responses")
os.makedirs(RAW_DIR, exist_ok=True)

ZENODO_API_URL = "https://zenodo.org/api/records"

SEARCH_QUERIES = [
    "doctor-patient audio",
    "medical consultation audio",
    "clinical speech",
    "medical dictation audio",
    "simulated medical consultation audio",
    "primock57",
    "svarah",
    "medical asr dataset",
    "clinical conversation speech",
    "telehealth audio",
    "triage audio",
    "indicvoices"
]

def search_zenodo():
    results = {}
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Zenodo dataset discovery...")
    
    headers = {"User-Agent": "BTP-Voice-Scribe-Research/1.0 (academic research)"}
    
    for query in SEARCH_QUERIES:
        print(f"Searching Zenodo for: '{query}'...")
        params = {
            "q": query,
            "type": "dataset",
            "size": 25,
            "sort": "mostrecent"
        }
        try:
            resp = requests.get(ZENODO_API_URL, params=params, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                hits = data.get("hits", {}).get("hits", [])
                cleaned = []
                for h in hits:
                    metadata = h.get("metadata", {})
                    files = h.get("files", [])
                    cleaned.append({
                        "id": h.get("id"),
                        "doi": h.get("doi"),
                        "title": metadata.get("title"),
                        "creators": metadata.get("creators"),
                        "description": metadata.get("description"),
                        "license": metadata.get("license"),
                        "access_right": metadata.get("access_right"),
                        "publication_date": metadata.get("publication_date"),
                        "keywords": metadata.get("keywords", []),
                        "files": [{"key": f.get("key"), "size": f.get("size"), "type": f.get("type")} for f in files]
                    })
                results[query] = cleaned
                print(f"  -> Found {len(cleaned)} records.")
            else:
                print(f"  -> Zenodo HTTP {resp.status_code} for '{query}'", file=sys.stderr)
                results[query] = {"status_code": resp.status_code, "error": resp.text[:200]}
        except Exception as e:
            print(f"  -> Error querying Zenodo for '{query}': {e}", file=sys.stderr)
            results[query] = {"error": str(e)}
        time.sleep(1) # respectful rate limiting

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(RAW_DIR, f"zenodo_discovery_{timestamp}.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved Zenodo discovery raw results to {out_file}")
    return out_file

if __name__ == "__main__":
    search_zenodo()
