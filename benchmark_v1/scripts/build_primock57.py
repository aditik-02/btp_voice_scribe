import sys, os, re, json, random, csv, glob
import numpy as np, wave
sys.path.insert(0, os.path.dirname(__file__)); from normalize import clean_tags, normalize
import builtins, functools; open = functools.partial(builtins.open, encoding="utf-8")  # same bytes on Windows and Linux
SRC, OUT = sys.argv[1], sys.argv[2]   # SRC: primock57 repo (transcripts, notes); OUT: vs_data/primock57
AUD = os.path.join(OUT, "audio")
def read_tg(p):
    s = open(p).read()
    return [(float(a), float(b), t.replace('""','"')) for a, b, t in
            re.findall(r'xmin = ([\d.]+)\s*\n\s*xmax = ([\d.]+)\s*\n\s*text = "(.*?)"\s*\n', s.replace("\r\n", "\n"), re.S) if t.strip()]
def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768; return x, w.getframerate()
def wr(p, x, sr):
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes()); w.close()
ids = sorted({os.path.basename(f).rsplit("_",1)[0] for f in glob.glob(f"{AUD}/*_doctor.wav")})
random.seed(57); by_day = {}
for i in ids: by_day.setdefault(i.split("_")[0], []).append(i)
dev = set(sum([random.sample(v, round(len(v)*0.2)) for v in by_day.values()], []))
os.makedirs(f"{OUT}/mixed", exist_ok=True); os.makedirs(f"{OUT}/references", exist_ok=True)
conv_rows, utt_rows = [], []
for cid in ids:
    d, sr = rd(f"{AUD}/{cid}_doctor.wav"); p, _ = rd(f"{AUD}/{cid}_patient.wav")
    n = max(len(d), len(p)); m = np.zeros(n, np.float32); m[:len(d)] += d; m[:len(p)] += p
    pk = np.abs(m).max(); m = m/pk*0.99 if pk > 0.99 else m
    wr(f"{OUT}/mixed/{cid}.wav", m, sr)
    segs = [dict(speaker=r, start=a, end=b, text_raw=t, text=clean_tags(t), unsure="<UNSURE>" in t, unintelligible="<UNIN" in t)
            for r in ("doctor","patient") for a, b, t in read_tg(f"{SRC}/transcripts/{cid}_{r}.TextGrid")]
    segs.sort(key=lambda s: s["start"]); segs = [s for s in segs if s["text"] or s["unintelligible"]]
    ref = " ".join(s["text"] for s in segs if s["text"])
    json.dump(dict(consultation_id=cid, duration_s=n/sr, split="dev" if cid in dev else "test", segments=segs,
                   reference=ref, reference_norm=normalize(ref)), open(f"{OUT}/references/{cid}.json","w"), indent=1)
    split = "dev" if cid in dev else "test"
    conv_rows.append(dict(sample_id=f"pm57_{cid}", dataset_id="primock57", relative_audio_path=f"primock57/mixed/{cid}.wav",
        sample_rate_hz=sr, duration_seconds=round(n/sr,2), condition="clean", source_consultation=cid, split=split,
        n_words_ref=len(normalize(ref).split()), reference_path=f"primock57/references/{cid}.json", soap_note_path=f"primock57/notes/{cid}.json"))
    for k, s in enumerate(segs):
        if not s["text"] or not normalize(s["text"]): continue
        utt_rows.append(dict(sample_id=f"pm57_{cid}_{k:03d}", dataset_id="primock57", relative_audio_path=f"primock57/audio/{cid}_{s['speaker']}.wav",
            start_s=round(s["start"],3), end_s=round(s["end"],3), speaker_role=s["speaker"], source_consultation=cid, split=split,
            unsure=s["unsure"], unintelligible=s["unintelligible"], transcript=s["text"], transcript_norm=normalize(s["text"])))
os.makedirs(f"{OUT}/notes", exist_ok=True)
import shutil
for f in glob.glob(f"{SRC}/notes/day*.json"): shutil.copy(f, f"{OUT}/notes/")
for name, rows in (("manifest_consultations.csv", conv_rows), ("manifest_utterances.csv", utt_rows)):
    with open(f"{OUT}/{name}", "w", newline="") as fh:
        w = csv.DictWriter(fh, rows[0].keys()); w.writeheader(); w.writerows(rows)
print(len(conv_rows), "consultations;", len(utt_rows), "utterances;", sum(r["split"]=="dev" for r in conv_rows), "dev")
