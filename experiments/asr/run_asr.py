#!/usr/bin/env python3
"""Run one ASR model over one benchmark manifest and save its transcripts.

Examples (from the repo root):
  python experiments/asr/run_asr.py --model whisper-large-v3 --manifest eka_en --split dev --limit 3   # smoke test
  python experiments/asr/run_asr.py --model whisper-large-v3 --manifest eka_en --split dev
  python experiments/asr/run_asr.py --model qwen3-asr-1.7b  --manifest pm57_noisy --split dev
  python experiments/asr/run_asr.py --model echo --manifest svarah --split dev --limit 50                # pipeline check

Output: results/hyps/<model>/<manifest>_<split>.jsonl, one line per clip. Re-running resumes: clips already
in the file are skipped (use --overwrite to start again). Errors are recorded per clip and retried next run.
"""
import argparse
import json
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))

from audio import SR, load_sample                      # noqa: E402
from models import REGISTRY                            # noqa: E402
from references import MANIFESTS, read_manifest, read_hyps, reference_text   # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, choices=sorted(REGISTRY))
    ap.add_argument("--manifest", required=True, choices=sorted(MANIFESTS))
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    ap.add_argument("--language", default="en", choices=["en", "hi", "kn"])
    ap.add_argument("--data-root", default=str(REPO / "benchmark_v1" / "data"))
    ap.add_argument("--out-dir", default=str(REPO / "results" / "hyps"))
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--checkpoint", help="local checkpoint folder (indicwhisper)")
    ap.add_argument("--limit", type=int, help="only the first N clips (smoke tests)")
    ap.add_argument("--condition", help="pm57_noisy only: run one condition, e.g. talker_in_sir0")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    rows = read_manifest(a.data_root, a.manifest, a.split)
    if a.condition:
        rows = [r for r in rows if r.get("condition") == a.condition]
    if a.limit:
        rows = rows[: a.limit]
    out = Path(a.out_dir) / a.model / f"{a.manifest}_{a.split}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    if a.overwrite and out.exists():
        out.unlink()
    done = {k for k, v in read_hyps(out).items() if not v.get("error")}
    todo = [r for r in rows if r["sample_id"] not in done]
    print(f"{a.model} on {a.manifest}/{a.split}: {len(rows)} clips, {len(rows) - len(todo)} already done, {len(todo)} to run")
    if not todo:
        return

    kw = {"checkpoint": a.checkpoint} if a.model == "indicwhisper" else {}
    t0 = time.time()
    model = REGISTRY[a.model](language=a.language, device=a.device, **kw)
    load_s = time.time() - t0
    gpu = ""
    try:
        import torch
        gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
    except Exception:
        pass
    print(f"loaded in {load_s:.0f} s on {gpu or platform.node()}")

    total_audio = total_decode = 0.0
    with open(out, "a", encoding="utf-8") as fh:
        for i, r in enumerate(todo, 1):
            rec = {"sample_id": r["sample_id"], "model": a.model, "language": a.language, "gpu": gpu}
            try:
                x = load_sample(a.data_root, r)
                if a.model == "echo":
                    model.reference = reference_text(a.data_root, r)
                t = time.time()
                hyp = model.transcribe(x)
                rec.update(hyp=hyp, audio_s=round(len(x) / SR, 3), decode_s=round(time.time() - t, 3))
                total_audio += rec["audio_s"]; total_decode += rec["decode_s"]
            except Exception as e:                       # keep going; the clip is retried on the next run
                rec.update(hyp="", error=f"{type(e).__name__}: {e}")
                print(f"  ! {r['sample_id']}: {rec['error']}", file=sys.stderr)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
            if i % 50 == 0 or i == len(todo):
                rtf = total_decode / total_audio if total_audio else 0
                print(f"  {i}/{len(todo)}  audio {total_audio / 60:.1f} min  real-time factor {rtf:.3f}")
    print(f"saved -> {out}")


if __name__ == "__main__":
    main()
