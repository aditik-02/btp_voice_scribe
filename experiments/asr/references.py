"""Reference transcripts and manifest helpers shared by run_asr.py and score.py."""
import csv
import json
from pathlib import Path

# which manifests exist, relative to benchmark_v1/data, and how their rows are grouped when scoring
MANIFESTS = {
    "eka_en":       {"path": "eka_en/manifest.csv",                       "by": ["recording_context"]},
    "svarah":       {"path": "svarah/manifest.csv",                       "by": ["primary_language"]},
    "pm57_utt":     {"path": "primock57/manifest_utterances.csv",         "by": ["speaker_role"]},
    "pm57_clean":   {"path": "primock57/manifest_consultations.csv",      "by": []},
    "pm57_noisy":   {"path": "primock57/manifest_noisy.csv",              "by": ["condition"]},
}


def read_manifest(data_root, name, split=None):
    m = MANIFESTS[name]
    with open(Path(data_root) / m["path"], encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return [r for r in rows if split in (None, "all") or r["split"] == split]


_ref_cache = {}

def reference_text(data_root, row):
    """Raw reference text (tags already removed) for any manifest row."""
    if row.get("transcript") not in (None, ""):
        return row["transcript"]
    p = Path(data_root) / row["reference_path"]
    if p not in _ref_cache:
        with open(p, encoding="utf-8") as fh:
            _ref_cache[p] = json.load(fh)
    return _ref_cache[p]["reference"]


def read_hyps(path):
    """Hypothesis file: one JSON object per line {sample_id, hyp, audio_s, decode_s, ...}; later lines win."""
    out = {}
    if Path(path).exists():
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    d = json.loads(line); out[d["sample_id"]] = d
    return out
