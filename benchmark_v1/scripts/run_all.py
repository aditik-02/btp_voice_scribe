#!/usr/bin/env python3
"""Voice Scribe English benchmark v1.1 — one-command build (Windows / macOS / Linux).

Run from anywhere:   python benchmark_v1/scripts/run_all.py
Needs:               python -m pip install numpy soundfile pyarrow pandas

Expects this layout (already in voice_scribe_data/):
  eka_medical_asr/  svarah/                      (hf download)
  sources/primock57_data/{transcripts,notes}     (copied from github.com/babylonhealth/primock57)
  sources/ms_snsd_noise/{noise_train,noise_test} (copied from github.com/microsoft/MS-SNSD)
Downloads the PriMock57 audio (1.9 GB) into benchmark_v1/data/primock57/audio, skips anything already done, then builds benchmark_v1/data/.
"""
import os, sys, subprocess, importlib.util, urllib.request, concurrent.futures as cf, hashlib, csv, time
HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(BENCH); DATA = os.path.join(BENCH, "data")
PM_SRC = os.path.join(ROOT, "sources", "primock57_data"); NOISE = os.path.join(ROOT, "sources", "ms_snsd_noise")
URL = "https://media.githubusercontent.com/media/babylonhealth/primock57/main/audio/"
def step(msg): print(f"\n=== {msg}", flush=True)
def check_deps():
    missing = [m for m in ("numpy", "soundfile", "pyarrow", "pandas") if importlib.util.find_spec(m) is None]
    if missing: sys.exit(f"Missing packages: {' '.join(missing)}\nRun:  python -m pip install {' '.join(missing)}")
def ok_wav(p):
    """complete WAV: RIFF header present AND file size equals the size the header declares (catches cut-off downloads)"""
    if not os.path.exists(p) or os.path.getsize(p) < 1_000_000: return False
    h = open(p, "rb").read(8)
    return h[:4] == b"RIFF" and int.from_bytes(h[4:8], "little") + 8 == os.path.getsize(p)
PM_AUDIO = os.path.join(DATA, "primock57", "audio")
def fetch(name):
    dst = os.path.join(PM_AUDIO, name); old = os.path.join(PM_SRC, "audio", name)
    if not ok_wav(dst) and ok_wav(old): os.replace(old, dst)   # files fetched earlier into sources/

    if ok_wav(dst): return name, "have"
    for attempt in range(4):
        try:
            tmp = dst + ".part"; urllib.request.urlretrieve(URL + name, tmp); os.replace(tmp, dst)
            if ok_wav(dst): return name, "downloaded"
        except Exception as e:
            err = e; time.sleep(3)
    return name, f"FAILED ({err})"
def noisy_matches(path, ref_path, rel_tol=1e-4):
    """Compare manifest_noisy.csv with the reference copy: every field must match exactly, except floats inside
    mix_meta (gains), which may differ by up to 1e-4 relative. Gains are computed in float32 and numpy builds sum in
    slightly different orders on different machines (~1e-6 relative, i.e. ~0.00001 dB)."""
    import json, math
    a = list(csv.DictReader(open(path, encoding="utf-8"))); b = list(csv.DictReader(open(ref_path, encoding="utf-8")))
    if len(a) != len(b): return False
    for x, y in zip(a, b):
        mx, my = json.loads(x.pop("mix_meta")), json.loads(y.pop("mix_meta"))
        if x != y or mx.keys() != my.keys(): return False
        for k in mx:
            if isinstance(mx[k], float) and isinstance(my[k], float):
                if not math.isclose(mx[k], my[k], rel_tol=rel_tol): return False
            elif mx[k] != my[k]: return False
    return True
def run(script, *args):
    print(">", script, *args, flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=True)
def main():
    check_deps()
    for p in (PM_SRC + "/transcripts", NOISE + "/noise_test", ROOT + "/eka_medical_asr/en", ROOT + "/svarah/data"):
        if not os.path.isdir(p): sys.exit(f"Missing input folder: {p}")
    step("1/5 PriMock57 audio (114 files)")
    os.makedirs(PM_AUDIO, exist_ok=True)
    names = sorted(f[:-len("_doctor.TextGrid")] + s for f in os.listdir(os.path.join(PM_SRC, "transcripts")) if f.endswith("_doctor.TextGrid") for s in ("_doctor.wav", "_patient.wav"))
    with cf.ThreadPoolExecutor(8) as ex:
        res = list(ex.map(fetch, names))
    bad = [r for r in res if r[1].startswith("FAILED")]
    print(f"{sum(r[1]=='have' for r in res)} already present, {sum(r[1]=='downloaded' for r in res)} downloaded, {len(bad)} failed")
    if bad: sys.exit(f"{len(bad)} downloads failed (first: {bad[0][0]}: {bad[0][1]}). Re-run the script to retry.")
    out_pm = os.path.join(DATA, "primock57")
    stamp = os.path.join(out_pm, "audio_ok.txt")
    if any(r[1] == "downloaded" for r in res) or not os.path.exists(stamp):
        # audio changed (or was never verified): PriMock57-derived files must be rebuilt
        for f in ("manifest_consultations.csv", "manifest_utterances.csv", "manifest_noisy.csv"):
            if os.path.exists(os.path.join(out_pm, f)): os.remove(os.path.join(out_pm, f)); print("will rebuild", f)
    with open(stamp, "w") as fh: fh.write("all 114 PriMock57 WAVs complete\n")
    if not os.path.exists(os.path.join(out_pm, "manifest_consultations.csv")):
        step("2/5 PriMock57 clean consultations + references"); run("build_primock57.py", PM_SRC, out_pm)
    if not os.path.exists(os.path.join(out_pm, "manifest_noisy.csv")):
        step("3/5 PriMock57 noise / background-talker variants (slowest step)"); run("make_noisy_primock57.py", out_pm, NOISE)
    if not os.path.exists(os.path.join(DATA, "svarah", "manifest.csv")):
        step("4/5 Eka Medical ASR (en) + Svarah"); run("build_eka_svarah.py", ROOT, DATA)
    if not any("talker_in_" in r["condition"] for r in csv.DictReader(open(os.path.join(out_pm, "manifest_noisy.csv"), encoding="utf-8"))):
        step("5/5 Indian-accented background talkers"); run("make_indian_talker_primock57.py", DATA)
    step("Verify against the reference build")
    ref = {}
    for line in open(os.path.join(HERE, "reference_md5.txt"), encoding="utf-8"):
        h, p = line.split(); ref[p] = h
    allok = True
    for p, h in ref.items():
        if p.endswith("manifest_noisy.csv"):
            got = h if noisy_matches(os.path.join(DATA, p), os.path.join(HERE, "reference_manifest_noisy.csv")) else "x"
        else: got = hashlib.md5(open(os.path.join(DATA, p), "rb").read()).hexdigest()
        print(("OK      " if got == h else "DIFFERS ") + p); allok &= got == h
    n = sum(1 for _ in csv.DictReader(open(os.path.join(out_pm, "manifest_noisy.csv"), encoding="utf-8")))
    print(f"noisy rows: {n} (expected 570)"); allok &= n == 570
    print("\nDONE - benchmark matches the reference build." if allok else "\nDONE - but some files differ from the reference build; send me the output above.")
if __name__ == "__main__":
    main()
