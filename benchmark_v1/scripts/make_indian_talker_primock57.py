"""Indian-accented background conversation for PriMock57 (ClinicalMix v1.1).
Distractor = two Svarah speakers taking turns (same dev/test split as the consultation), looped to length.
Conditions: talker_in_sir10 / talker_in_sir5 / talker_in_sir0 ; rows appended to primock57/manifest_noisy.csv
Usage: python3 make_indian_talker_primock57.py <vs_data dir>
"""
import sys, os, json, glob, random, csv
import numpy as np, soundfile as sf
import builtins, functools; open = functools.partial(builtins.open, encoding="utf-8")  # same bytes on Windows and Linux
VS = sys.argv[1]; OUT = f"{VS}/primock57"; SR = 16000
sv = list(csv.DictReader(open(f"{VS}/svarah/manifest.csv")))
by_spk = {}
for r in sv: by_spk.setdefault((r["split"], r["speaker_id"]), []).append(r)
def stream(split, n, rng):
    spks = sorted(s for (sp, s) in by_spk if sp == split); a, b = rng.sample(spks, 2)
    qa, qb = by_spk[(split, a)][:], by_spk[(split, b)][:]; rng.shuffle(qa); rng.shuffle(qb)
    out, i, used = [], 0, []
    while sum(len(x) for x in out) < n:
        q = qa if i % 2 == 0 else qb; r = q[(i // 2) % len(q)]; i += 1
        x, _ = sf.read(f"{VS}/{r['relative_audio_path']}", dtype="float32"); used.append(r["sample_id"])
        out += [x, np.zeros(int(rng.uniform(0.2, 0.8) * SR), np.float32)]
    return np.concatenate(out)[:n], (a, b), used
def active_power(x, segs):
    idx = np.concatenate([np.arange(int(s["start"]*SR), min(int(s["end"]*SR), len(x))) for s in segs]); return float(np.mean(x[idx]**2))
rows = []
for f in sorted(glob.glob(f"{OUT}/references/*.json")):
    ref = json.load(open(f)); cid = ref["consultation_id"]; split = ref["split"]; rng = random.Random(f"{cid}-in-v1")
    tgt, _ = sf.read(f"{OUT}/mixed/{cid}.wav", dtype="float32"); pt = active_power(tgt, ref["segments"])
    d, spk, used = stream(split, len(tgt), rng); pd_ = float(np.mean(d[np.abs(d) > 1e-4]**2))   # power over talker's voiced samples
    for sir in (10, 5, 0):
        name = f"talker_in_sir{sir}"; g = np.sqrt(pt / (10**(sir/10)) / pd_); y = tgt + g * d
        pk = np.abs(y).max(); sc = 0.99/pk if pk > 0.99 else 1.0; y *= sc
        path = f"noisy/{cid}__{name}.flac"; sf.write(f"{OUT}/{path}", y, SR, subtype="PCM_16")
        meta = dict(condition=name, sir_db=sir, snr_db=None, distractor="svarah:" + "+".join(spk), distractor_gain=float(g), peak_scale=float(sc),
                    distractor_utterances=used)
        rows.append(dict(sample_id=f"pm57_{cid}__{name}", dataset_id="primock57", relative_audio_path=f"primock57/{path}", sample_rate_hz=SR,
            duration_seconds=round(len(tgt)/SR, 2), condition=name, sir_db=sir, snr_db="", distractor_consultation="svarah:" + "+".join(spk),
            source_consultation=cid, split=split, reference_path=f"primock57/references/{cid}.json", mix_meta=json.dumps(meta)))
    print(cid, flush=True)
man = f"{OUT}/manifest_noisy.csv"; old = [r for r in csv.DictReader(open(man)) if not r["condition"].startswith("talker_in_")]
with open(man, "w", newline="") as fh:
    w = csv.DictWriter(fh, old[0].keys()); w.writeheader(); w.writerows(old + rows)
print(len(rows), "new files;", len(old) + len(rows), "rows in manifest_noisy.csv")
