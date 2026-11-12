#!/usr/bin/env python3
"""
Discovery script for Hugging Face Hub datasets relevant to medical speech,
clinical consultation, diarization, and Indic speech.
Saves raw API responses to research/audio-datasets/raw_responses/
"""

import json
import os
import sys
from datetime import datetime, timezone
from huggingface_hub import HfApi

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw_responses")
os.makedirs(RAW_DIR, exist_ok=True)

api = HfApi()

SEARCH_QUERIES = [
    "medical speech",
    "clinical speech",
    "doctor patient audio",
    "medical consultation audio",
    "medical dictation",
    "radiology audio",
    "healthcare speech",
    "clinical conversation audio",
    "medical diarization",
    "primock57",
    "aci-bench",
    "svarah",
    "indicvoices",
    "kathbath",
    "shrutilipi",
    "lahaja",
    "medical asr",
    "clinical asr"
]

def search_hf():
    results = {}
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Hugging Face dataset discovery...")
    
    for query in SEARCH_QUERIES:
        print(f"Searching HF for: '{query}'...")
        try:
            datasets = list(api.list_datasets(search=query, full=True, limit=50))
            cleaned = []
            for d in datasets:
                cleaned.append({
                    "id": d.id,
                    "author": d.author,
                    "description": d.description,
                    "downloads": getattr(d, "downloads", 0),
                    "likes": getattr(d, "likes", 0),
                    "tags": getattr(d, "tags", []),
                    "private": getattr(d, "private", False),
                    "gated": getattr(d, "gated", False),
                    "created_at": str(getattr(d, "created_at", "")),
                    "last_modified": str(getattr(d, "last_modified", "")),
                    "sha": getattr(d, "sha", ""),
                })
            results[query] = cleaned
            print(f"  -> Found {len(cleaned)} candidates.")
        except Exception as e:
            print(f"  -> Error searching '{query}': {e}", file=sys.stderr)
            results[query] = {"error": str(e)}

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(RAW_DIR, f"hf_discovery_{timestamp}.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved HF discovery raw results to {out_file}")
    return out_file

if __name__ == "__main__":
    search_hf()
