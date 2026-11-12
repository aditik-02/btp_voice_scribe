#!/usr/bin/env python3
"""
HTTP link verification script for datasets and evidence sources.
Performs HEAD requests (falling back to GET range=0-10) to verify link status,
content-type, redirect chains, and availability.
"""

import csv
import json
import os
import sys
import time
from urllib.parse import urlparse
import requests

def check_url(url, timeout=15):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # First attempt HEAD
        r = requests.head(url, headers=headers, allow_redirects=True, timeout=timeout)
        # Some servers disallow HEAD or return 403/405
        if r.status_code in [403, 405, 500, 501, 503]:
            # fallback to GET with byte range
            headers["Range"] = "bytes=0-100"
            r = requests.get(url, headers=headers, allow_redirects=True, timeout=timeout)
        return {
            "status_code": r.status_code,
            "final_url": r.url,
            "content_type": r.headers.get("Content-Type", ""),
            "content_length": r.headers.get("Content-Length", ""),
            "ok": r.ok,
            "error": None
        }
    except Exception as e:
        return {
            "status_code": None,
            "final_url": url,
            "content_type": "",
            "content_length": "",
            "ok": False,
            "error": str(e)
        }

def check_all_links(input_csv, url_column="evidence_url"):
    if not os.path.exists(input_csv):
        print(f"File {input_csv} does not exist.")
        return []
    
    results = []
    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get(url_column, "").strip()
            if not url or not url.startswith("http"):
                continue
            print(f"Checking URL: {url}...")
            res = check_url(url)
            row_res = {
                "candidate_id": row.get("candidate_id", ""),
                "claim": row.get("claim", ""),
                "url": url,
                "status_code": res["status_code"],
                "ok": res["ok"],
                "content_type": res["content_type"],
                "error": res["error"]
            }
            results.append(row_res)
            print(f"  -> HTTP {res['status_code']} (ok={res['ok']})")
            time.sleep(0.5)
            
    return results

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "EVIDENCE_LEDGER.csv")
    col = sys.argv[2] if len(sys.argv) > 2 else "evidence_url"
    results = check_all_links(target, col)
    print(f"\nVerification summary: Checked {len(results)} links.")
    failures = [r for r in results if not r["ok"]]
    if failures:
        print(f"WARNING: {len(failures)} link(s) failed:")
        for f in failures:
            print(f" - {f['url']}: {f['error'] or f['status_code']}")
    else:
        print("All tested links passed verification.")
