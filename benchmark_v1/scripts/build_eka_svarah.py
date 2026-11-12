"""Build Eka Medical ASR (en) and Svarah into the Voice Scribe benchmark.
Usage: python3 build_eka_svarah.py <voice_scribe_data dir with eka_medical_asr/ and svarah/> <vs_data out dir>
- audio decoded to 16 kHz mono FLAC
- dev/test split by SPEAKER (Eka: speaker id; Svarah: no id released -> demographic profile used as speaker proxy,
  115 profiles for 117 speakers, so at worst two speakers sharing a profile stay together)
- Eka speaker e-mails replaced by anonymous ids
"""
import sys, os, io, json, glob, random, csv, subprocess
import numpy as np, soundfile as sf, pyarrow.parquet as pq
sys.path.insert(0, os.path.dirname(__file__)); from normalize import normalize
import builtins, functools; open = functools.partial(builtins.open, encoding="utf-8")  # same bytes on Windows and Linux
SRC, OUT = sys.argv[1], sys.argv[2]; SR = 16000
def decode(b):
    try:
        x, sr = sf.read(io.BytesIO(b), dtype="float32")
    except Exception:
        sr = None
    if sr is None or sr != SR:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "pipe:1"], input=b, capture_output=True, check=True)
        return np.frombuffer(p.stdout, np.float32)
    return x.mean(1) if x.ndim > 1 else x
def speaker_split(counts, frac=0.2, seed=57):
    spk = sorted(counts); random.Random(seed).shuffle(spk); tot = sum(counts.values()); dev, n = set(), 0
    for s in spk:
        if n + counts[s] <= frac * tot * 1.1: dev.add(s); n += counts[s]
        if n >= frac * tot: break
    return dev
def write_csv(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, rows[0].keys()); w.writeheader(); w.writerows(rows)
# ---------------- Eka (en) ----------------
files = sorted(glob.glob(f"{SRC}/eka_medical_asr/en/*.parquet")); meta = []
for f in files:
    t = pq.read_table(f, columns=["file_name", "duration", "text", "session_id", "speaker", "type_concept", "recording_context", "medical_entities"])
    meta += [dict(m, speaker=m["speaker"] or "UNKNOWN") for m in t.to_pylist()]
spk_ids = {s: f"eka_spk_{i:02d}" for i, s in enumerate(sorted({m["speaker"] for m in meta}))}
# split: narration clips by speaker, balanced so each recording_context is ~20% dev (search over seeds);
# conversation clips have no speaker id -> split by session_id
from collections import Counter
cnt = Counter((spk_ids[m["speaker"]], m["recording_context"]) for m in meta if m["speaker"] != "UNKNOWN")
spks = sorted({s for s, _ in cnt}); ctxs = sorted({c for _, c in cnt}); tot = Counter(c for (_, c), n in cnt.items() for _ in range(n))
best = None
for seed in range(2000):
    rng = random.Random(seed); d = {s for s in spks if rng.random() < 0.2}
    err = sum(abs(sum(cnt[(s, c)] for s in d) / tot[c] - 0.2) for c in ctxs)
    if best is None or err < best[0]: best = (err, d)
dev = best[1]
conv_sessions = sorted({m["session_id"] for m in meta if m["speaker"] == "UNKNOWN"}); random.Random(57).shuffle(conv_sessions)
dev_sessions = set(conv_sessions[: round(0.2 * len(conv_sessions))])
os.makedirs(f"{OUT}/eka_en/audio", exist_ok=True); rows = []; k = 0
for f in files:
    for r in pq.read_table(f).to_pylist():
        x = decode(r["audio"]); sid = f"eka_en_{k:05d}"; k += 1
        sf.write(f"{OUT}/eka_en/audio/{sid}.flac", x, SR, subtype="PCM_16")
        ents = [dict(text=e[0], type=e[1], norm=normalize(e[0])) for e in json.loads(r["medical_entities"] or "[]")]
        spk = spk_ids[r["speaker"] or "UNKNOWN"]
        rows.append(dict(sample_id=sid, dataset_id="eka_medical_asr_en", relative_audio_path=f"eka_en/audio/{sid}.flac",
            sample_rate_hz=SR, duration_seconds=round(len(x)/SR, 3), speaker_id=spk, session_id=r["session_id"],
            recording_context=r["recording_context"], type_concept=r["type_concept"], split="dev" if (spk in dev or r["session_id"] in dev_sessions) else "test",
            transcript=r["text"], transcript_norm=normalize(r["text"]), medical_entities=json.dumps(ents, ensure_ascii=False),
            original_file_name=r["file_name"]))
write_csv(f"{OUT}/eka_en/manifest.csv", rows); print("eka", len(rows), "clips", sum(r["split"] == "dev" for r in rows), "dev")
# ---------------- Svarah ----------------
KEY = ["gender", "age-group", "primary_language", "native_place_state", "native_place_district", "highest_qualification", "job_category", "occupation_domain"]
files = sorted(glob.glob(f"{SRC}/svarah/data/*.parquet")); prof = {}
for f in files:
    for r in pq.read_table(f, columns=KEY).to_pylist(): p = "|".join(str(r[c]) for c in KEY); prof[p] = prof.get(p, 0) + 1
pid = {p: f"svarah_spk_{i:03d}" for i, p in enumerate(sorted(prof))}; counts = {pid[p]: n for p, n in prof.items()}
dev = speaker_split(counts); os.makedirs(f"{OUT}/svarah/audio", exist_ok=True); rows = []; k = 0
for f in files:
    for r in pq.read_table(f).to_pylist():
        x = decode(r["audio_filepath"]["bytes"]); sid = f"svarah_{k:05d}"; k += 1
        sf.write(f"{OUT}/svarah/audio/{sid}.flac", x, SR, subtype="PCM_16")
        spk = pid["|".join(str(r[c]) for c in KEY)]
        rows.append(dict(sample_id=sid, dataset_id="svarah", relative_audio_path=f"svarah/audio/{sid}.flac", sample_rate_hz=SR,
            duration_seconds=round(len(x)/SR, 3), speaker_id=spk, gender=r["gender"], age_group=r["age-group"],
            primary_language=r["primary_language"], native_state=r["native_place_state"], split="dev" if spk in dev else "test",
            transcript=r["text"], transcript_norm=normalize(r["text"]), original_file_name=r["audio_filepath"]["path"]))
write_csv(f"{OUT}/svarah/manifest.csv", rows); print("svarah", len(rows), "clips", sum(r["split"] == "dev" for r in rows), "dev")
