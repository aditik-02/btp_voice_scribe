"""Noisy / background-talker variants of PriMock57 consultations (ClinicalMix v1).
Reference transcript stays the ORIGINAL consultation; any distractor words a model outputs are errors.
Usage: python3 make_noisy_primock57.py <vs_data/primock57> <MS-SNSD dir>
"""
import sys, os, json, glob, random, csv
import numpy as np, soundfile as sf
import builtins, functools; open = functools.partial(builtins.open, encoding="utf-8")  # same bytes on Windows and Linux
OUT, SNSD = sys.argv[1], sys.argv[2]
SR = 16000
POOL = {  # OPD-like noise categories; dev and test draw from DIFFERENT MS-SNSD clip sets (train vs test folders)
  "dev":  {"bed": ["AirConditioner"], "ambient": ["Babble","CafeTeria","Hallway","Station","Office","NeighborSpeaking"],
           "events": ["ShuttingDoor","SqueakyChair","Typing","AirportAnnouncements","CopyMachine"], "dir": "noise_train"},
  "test": {"bed": ["AirConditioner"], "ambient": ["Babble","Neighbor"],
           "events": ["ShuttingDoor","Typing","AirportAnnouncements","CopyMachine"], "dir": "noise_test"}}
CONDITIONS = [("noise_snr20", None, 20), ("noise_snr10", None, 10), ("noise_snr5", None, 5),
              ("talker_sir10", 10, None), ("talker_sir5", 5, None), ("talker_sir0", 0, None),
              ("opd_sir5_snr10", 5, 10)]
def load(p):
    x, sr = sf.read(p, dtype="float32"); x = x.mean(1) if x.ndim > 1 else x
    assert sr == SR, (p, sr); return x
def clips(split, cats):
    return sorted(f for c in cats for f in glob.glob(f"{SNSD}/{POOL[split]['dir']}/{c}_*.wav"))
def tile_random(files, n, rng, used):
    out = np.zeros(0, np.float32)
    while len(out) < n:
        f = rng.choice(files); used.append(os.path.basename(f)); x = load(f)
        x = x[: n - len(out)] if len(out) + len(x) > n else x
        out = np.concatenate([out, x])
    return out
def noise_bed(split, n, rng, used):
    P = POOL[split]
    bed = tile_random(clips(split, P["bed"]), n, rng, used)
    amb = tile_random(clips(split, P["ambient"]), n, rng, used)
    ev = np.zeros(n, np.float32); ev_files = clips(split, P["events"]); t = int(rng.uniform(5, 20) * SR)
    while t < n:   # sparse events every 15-45 s
        x = load(rng.choice(ev_files)); used.append("event"); x = x[: min(len(x), 6 * SR, n - t)]
        ev[t:t+len(x)] += x; t += len(x) + int(rng.uniform(15, 45) * SR)
    def nrm(v): r = np.sqrt(np.mean(v**2)); return v / r if r > 0 else v
    return nrm(0.5 * nrm(bed) + 1.0 * nrm(amb) + 0.7 * nrm(ev))
def active_power(x, segs):
    idx = np.concatenate([np.arange(int(s["start"]*SR), min(int(s["end"]*SR), len(x))) for s in segs] or [np.arange(len(x))])
    return float(np.mean(x[idx]**2))
refs = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(glob.glob(f"{OUT}/references/*.json"))}
os.makedirs(f"{OUT}/noisy", exist_ok=True); rows = []
for split in ("dev", "test"):
    ids = [c for c in refs if refs[c]["split"] == split]
    for i, cid in enumerate(ids):
        rng = random.Random(f"{cid}-v1")
        tgt = load(f"{OUT}/mixed/{cid}.wav"); n = len(tgt); pt = active_power(tgt, refs[cid]["segments"])
        did = ids[(i + 1) % len(ids)]                      # distractor = another consultation, same split
        d = load(f"{OUT}/mixed/{did}.wav"); off = rng.randrange(len(d)); d = np.roll(d, -off)
        d = np.tile(d, int(np.ceil(n / len(d))))[:n]; pd_ = active_power(load(f"{OUT}/mixed/{did}.wav"), refs[did]["segments"])
        used = []; nz = noise_bed(split, n, rng, used); pn = float(np.mean(nz**2))
        for name, sir, snr in CONDITIONS:
            y = tgt.copy(); meta = dict(condition=name, sir_db=sir, snr_db=snr)
            if sir is not None:
                g = np.sqrt(pt / (10**(sir/10)) / pd_); y += g * d; meta.update(distractor=did, distractor_offset_s=off/SR, distractor_gain=float(g))
            if snr is not None:
                g = np.sqrt(pt / (10**(snr/10)) / pn); y += g * nz; meta.update(noise_gain=float(g), noise_clips=sorted(set(u for u in used if u != "event")))
            pk = np.abs(y).max(); scale = 0.99 / pk if pk > 0.99 else 1.0; y *= scale; meta["peak_scale"] = float(scale)
            path = f"noisy/{cid}__{name}.flac"; sf.write(f"{OUT}/{path}", y, SR, subtype="PCM_16")
            rows.append(dict(sample_id=f"pm57_{cid}__{name}", dataset_id="primock57", relative_audio_path=f"primock57/{path}",
                sample_rate_hz=SR, duration_seconds=round(n/SR, 2), condition=name, sir_db=sir if sir is not None else "",
                snr_db=snr if snr is not None else "", distractor_consultation=meta.get("distractor", ""),
                source_consultation=cid, split=split, reference_path=f"primock57/references/{cid}.json", mix_meta=json.dumps(meta)))
        print(split, cid, "done", flush=True)
with open(f"{OUT}/manifest_noisy.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(rows), "noisy files")
