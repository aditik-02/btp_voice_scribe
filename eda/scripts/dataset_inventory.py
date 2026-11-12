#!/usr/bin/env python3
"""
eda/scripts/dataset_inventory.py
Phase 1: Dataset Inventory and Validation for Medical Voice Scribe.
Analyzes PriMock57, Eka Medical ASR, Svarah, and MS-SNSD.
Computes exact file counts, sizes, extensions, parquet schemas, and audio header properties.
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict
import pyarrow.parquet as pq
import soundfile as sf

def inspect_dataset_inventory(base_dir: Path):
    datasets = ["primock57", "eka_medical_asr", "svarah", "ms_snsd"]
    inventory_summary = {}

    for ds_name in datasets:
        ds_path = base_dir / ds_name
        if not ds_path.exists():
            print(f"Warning: {ds_path} does not exist.")
            continue

        print(f"--- Scanning Inventory: {ds_name} ---")
        stats = {
            "dataset_name": ds_name,
            "root_path": str(ds_path),
            "total_files": 0,
            "total_size_bytes": 0,
            "extension_counts": defaultdict(int),
            "extension_sizes": defaultdict(int),
            "audio_files_count": 0,
            "transcript_files_count": 0,
            "metadata_files_count": 0,
            "parquet_files": [],
            "parquet_records": 0,
            "audio_properties": {
                "sample_rates": defaultdict(int),
                "channels": defaultdict(int),
                "subtypes": defaultdict(int),
                "formats": defaultdict(int)
            }
        }

        # Track files
        for root, dirs, files in os.walk(ds_path):
            if ".git" in Path(root).parts:
                continue
            for f in files:
                fp = Path(root) / f
                try:
                    sz = fp.stat().st_size
                    ext = fp.suffix.lower() if fp.suffix else "(no ext)"
                    stats["total_files"] += 1
                    stats["total_size_bytes"] += sz
                    stats["extension_counts"][ext] += 1
                    stats["extension_sizes"][ext] += sz

                    if ext == ".wav":
                        stats["audio_files_count"] += 1
                    elif ext in [".textgrid", ".json", ".txt"]:
                        # JSON could be transcript or metadata
                        if "transcript" in f.lower() or "note" in f.lower() or ext == ".textgrid":
                            stats["transcript_files_count"] += 1
                        else:
                            stats["metadata_files_count"] += 1
                    elif ext in [".csv", ".xlsx", ".md", ".cfg"]:
                        stats["metadata_files_count"] += 1
                    elif ext == ".parquet":
                        stats["parquet_files"].append(str(fp.relative_to(ds_path)))
                except Exception as e:
                    print(f"Error reading {fp}: {e}")

        # If parquet files exist, inspect their schema and row counts
        if stats["parquet_files"]:
            parquet_details = []
            for rel_pf in stats["parquet_files"]:
                pf = ds_path / rel_pf
                try:
                    table = pq.read_table(pf)
                    num_rows = table.num_rows
                    stats["parquet_records"] += num_rows
                    parquet_details.append({
                        "file": rel_pf,
                        "rows": num_rows,
                        "size_bytes": pf.stat().st_size,
                        "columns": table.column_names,
                        "schema": str(table.schema)
                    })
                except Exception as e:
                    print(f"Error reading parquet {pf}: {e}")
            stats["parquet_details"] = parquet_details

        # Sample audio headers for .wav files (up to 500 files to avoid slow disk I/O on 24k files)
        wav_files = []
        for root, dirs, files in os.walk(ds_path):
            if ".git" in Path(root).parts:
                continue
            for f in files:
                if f.lower().endswith(".wav"):
                    wav_files.append(Path(root) / f)

        if wav_files:
            # Sample across the dataset
            sample_wavs = wav_files[:200] + wav_files[-50:] if len(wav_files) > 250 else wav_files
            for w in sample_wavs:
                try:
                    info = sf.info(w)
                    stats["audio_properties"]["sample_rates"][str(info.samplerate)] += 1
                    stats["audio_properties"]["channels"][str(info.channels)] += 1
                    stats["audio_properties"]["subtypes"][str(info.subtype)] += 1
                    stats["audio_properties"]["formats"][str(info.format)] += 1
                except Exception as e:
                    print(f"Error reading audio header {w}: {e}")

        # Convert defaultdicts to regular dicts for JSON serialization
        stats["extension_counts"] = dict(stats["extension_counts"])
        stats["extension_sizes"] = dict(stats["extension_sizes"])
        stats["audio_properties"]["sample_rates"] = dict(stats["audio_properties"]["sample_rates"])
        stats["audio_properties"]["channels"] = dict(stats["audio_properties"]["channels"])
        stats["audio_properties"]["subtypes"] = dict(stats["audio_properties"]["subtypes"])
        stats["audio_properties"]["formats"] = dict(stats["audio_properties"]["formats"])

        inventory_summary[ds_name] = stats
        print(f"Done: {ds_name} - {stats['total_files']} files, {stats['total_size_bytes'] / (1024*1024):.2f} MB")

    return inventory_summary

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    base_dir = repo_root / "voice_scribe_data"
    output_json = repo_root / "eda" / "reports" / "inventory_summary.json"

    inventory = inspect_dataset_inventory(base_dir)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(inventory, f, indent=2)

    print(f"\nInventory scan complete. Saved to: {output_json}")

if __name__ == "__main__":
    main()
