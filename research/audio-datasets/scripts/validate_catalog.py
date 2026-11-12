#!/usr/bin/env python3
"""
Catalog validator script.
Ensures consistency between dataset_catalog.csv, dataset_catalog.json,
and EVIDENCE_LEDGER.csv, and checks for required schema fields.
"""

import csv
import json
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(BASE_DIR, "dataset_catalog.csv")
JSON_PATH = os.path.join(BASE_DIR, "dataset_catalog.json")
LEDGER_PATH = os.path.join(BASE_DIR, "EVIDENCE_LEDGER.csv")

REQUIRED_FIELDS = [
    "dataset_id",
    "dataset_name",
    "primary_category",
    "pipeline_stages",
    "audio_available",
    "audio_hours",
    "sample_rate_hz",
    "format",
    "speaker_count",
    "has_role_labels",
    "has_timestamps",
    "language",
    "accent_dialect",
    "domain_clinical_relevance",
    "access_type",
    "official_url",
    "license",
    "citation"
]

VALID_CATEGORIES = {"A", "B", "C", "D", "E", "F", "G", "H"}

def validate():
    errors = []
    warnings = []

    if not os.path.exists(CSV_PATH):
        errors.append(f"Missing {CSV_PATH}")
    if not os.path.exists(JSON_PATH):
        errors.append(f"Missing {JSON_PATH}")
    if not os.path.exists(LEDGER_PATH):
        errors.append(f"Missing {LEDGER_PATH}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return False

    # Load Ledger
    ledger_ids = set()
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get("candidate_id", "").strip()
            if cid:
                ledger_ids.add(cid)
    print(f"Loaded {len(ledger_ids)} unique candidate IDs from evidence ledger.")

    # Load CSV Catalog
    csv_rows = []
    csv_ids = set()
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            csv_rows.append(row)
            cid = row.get("dataset_id", "").strip()
            if not cid:
                errors.append(f"CSV row {i+1} missing dataset_id")
            elif cid in csv_ids:
                errors.append(f"Duplicate dataset_id '{cid}' in CSV")
            csv_ids.add(cid)

            for req in REQUIRED_FIELDS:
                if req not in row or row[req] is None or row[req] == "":
                    errors.append(f"Dataset '{cid}' missing required field: {req}")

            cat = row.get("primary_category", "").strip().upper()
            if cat not in VALID_CATEGORIES:
                errors.append(f"Dataset '{cid}' has invalid primary_category: '{cat}'")

            if cid not in ledger_ids:
                errors.append(f"Dataset '{cid}' has NO corresponding entries in EVIDENCE_LEDGER.csv")

    # Load JSON Catalog
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        try:
            json_data = json.load(f)
        except Exception as e:
            errors.append(f"Failed to parse {JSON_PATH}: {e}")
            json_data = []

    json_ids = set()
    if isinstance(json_data, list):
        for item in json_data:
            cid = item.get("dataset_id")
            if cid:
                json_ids.add(cid)
    else:
        errors.append(f"JSON catalog root must be a list of records")

    # Check parity
    csv_diff = csv_ids - json_ids
    json_diff = json_ids - csv_ids
    if csv_diff:
        errors.append(f"IDs in CSV but not JSON: {csv_diff}")
    if json_diff:
        errors.append(f"IDs in JSON but not CSV: {json_diff}")

    print("\n--- VALIDATION REPORT ---")
    print(f"Total CSV records: {len(csv_rows)}")
    print(f"Total JSON records: {len(json_ids)}")
    print(f"Ledger mapped candidates: {len(csv_ids & ledger_ids)} / {len(csv_ids)}")

    if errors:
        print(f"\nFound {len(errors)} ERROR(S):", file=sys.stderr)
        for err in errors:
            print(f"  [X] {err}", file=sys.stderr)
        return False
    else:
        print("\nAll catalog records passed schema, parity, and ledger-traceability validations successfully.")
        return True

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
