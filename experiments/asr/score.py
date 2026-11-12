#!/usr/bin/env python3
"""Score saved transcripts against the benchmark references.

  python experiments/asr/score.py --model whisper-large-v3 --manifest eka_en --split dev
  python experiments/asr/score.py --summary --split dev            # one table of every scored model/manifest

Metrics (decided in the EDA):
  * WER / CER pooled over all words / characters of the group (never the mean of per-clip WER).
    CER ignores spaces. Both reference and output go through the same normaliser (--norm v1 | v2).
  * Breakdowns: Eka by clip type, Svarah by first language, PriMock57 utterances by doctor/patient
    (plus a strict score without utterances flagged unintelligible/uncertain), noisy PriMock57 by condition.
  * Eka medical-term accuracy: share of tagged terms (per type; drugs separately) that appear intact in the output.
  * Background-speech leakage (noisy PriMock57 with a talker): output words that are inserted or substituted,
    occur in the background conversation, and never occur in the consultation itself; per 100 reference words.
    If the clean consultation was also run, the same count on the clean output is reported as the chance level.
  * Real-time factor = decoding time / audio duration (lower is faster).
"""
import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import jiwer

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "benchmark_v1" / "scripts"))

from normalize import NORMALIZERS                                       # noqa: E402
from references import MANIFESTS, read_manifest, read_hyps, reference_text   # noqa: E402


def wer_counts(refs, hyps):
    """Pooled word and character error counts for parallel lists of normalised strings (refs non-empty)."""
    if not refs:
        return None
    w = jiwer.process_words(refs, hyps)
    n = w.hits + w.substitutions + w.deletions
    rc = [r.replace(" ", "") for r in refs]; hc = [h.replace(" ", "") for h in hyps]
    c = jiwer.process_characters(rc, hc)
    nc = c.hits + c.substitutions + c.deletions
    return {"wer": (w.substitutions + w.deletions + w.insertions) / n, "cer": (c.substitutions + c.deletions + c.insertions) / nc,
            "sub": w.substitutions, "del": w.deletions, "ins": w.insertions, "ref_words": n, "clips": len(refs)}


def inserted_or_substituted_words(ref, hyp):
    """Output words that the alignment marks as inserted or substituted."""
    out = jiwer.process_words(ref, hyp)
    hw = out.hypotheses[0]; words = []
    for ch in out.alignments[0]:
        if ch.type in ("insert", "substitute"):
            words += hw[ch.hyp_start_idx: ch.hyp_end_idx]
    return words


def score(data_root, manifest, split, hyps_path, norm, clean_hyps_path=None):
    N = NORMALIZERS[norm]
    rows = read_manifest(data_root, manifest, split)
    hyps = read_hyps(hyps_path)
    errors = sum(1 for r in rows if hyps.get(r["sample_id"], {}).get("error"))
    have = [r for r in rows if r["sample_id"] in hyps and not hyps[r["sample_id"]].get("error")]
    res = {"manifest": manifest, "split": split, "norm": norm, "hyps_file": str(hyps_path),
           "clips_in_split": len(rows), "clips_scored": 0, "clips_missing": len(rows) - len(have), "clips_failed": errors}
    pairs = []
    for r in have:
        ref = N(reference_text(data_root, r)); hyp = N(hyps[r["sample_id"]].get("hyp", ""))
        if ref:
            pairs.append((r, ref, hyp))
    res["clips_scored"] = len(pairs)
    res["overall"] = wer_counts([p[1] for p in pairs], [p[2] for p in pairs])
    a = sum(float(hyps[r["sample_id"]].get("audio_s") or 0) for r in have)
    d = sum(float(hyps[r["sample_id"]].get("decode_s") or 0) for r in have)
    res["real_time_factor"] = d / a if a else None
    res["audio_hours"] = a / 3600

    groups = defaultdict(list)
    for col in MANIFESTS[manifest]["by"]:
        for p in pairs:
            groups[f"{col}={p[0][col]}"].append(p)
    res["by_group"] = {g: wer_counts([p[1] for p in ps], [p[2] for p in ps]) for g, ps in sorted(groups.items())}

    if manifest == "pm57_utt":
        strict = [p for p in pairs if p[0]["unintelligible"] == "False" and p[0]["unsure"] == "False"]
        res["strict_no_flagged_utterances"] = wer_counts([p[1] for p in strict], [p[2] for p in strict])
        for role in ("doctor", "patient"):
            s = [p for p in strict if p[0]["speaker_role"] == role]
            res[f"strict_{role}"] = wer_counts([p[1] for p in s], [p[2] for p in s])

    if manifest == "eka_en":
        found, total = defaultdict(int), defaultdict(int)
        for r, ref, hyp in pairs:
            padded = f" {hyp} "
            for e in json.loads(r["medical_entities"]):
                term = N(e["text"])
                if not term:
                    continue
                total[e["type"]] += 1; total["all"] += 1
                if f" {term} " in padded:
                    found[e["type"]] += 1; found["all"] += 1
        res["medical_term_accuracy"] = {t: {"terms": total[t], "correct": found[t], "accuracy": found[t] / total[t]}
                                        for t in sorted(total)}

    if manifest == "pm57_noisy":
        sv = {}
        clean = read_hyps(clean_hyps_path) if clean_hyps_path else {}
        leak = defaultdict(lambda: {"leaked_words": 0, "ref_words": 0, "chance_leaked_words": 0, "chance_ref_words": 0})
        for r, ref, hyp in pairs:
            meta = json.loads(r["mix_meta"])
            if not r["condition"].startswith(("talker", "opd")):
                continue
            if meta["distractor"].startswith("svarah:"):
                if not sv:
                    sv = {x["sample_id"]: x["transcript"] for x in read_manifest(data_root, "svarah")}
                dtext = " ".join(sv[u] for u in meta["distractor_utterances"])
            else:
                dtext = reference_text(data_root, {"reference_path": f"primock57/references/{meta['distractor']}.json"})
            dwords, twords = set(N(dtext).split()), set(ref.split())
            only_bg = dwords - twords
            L = leak[r["condition"]]
            L["leaked_words"] += sum(w in only_bg for w in inserted_or_substituted_words(ref, hyp))
            L["ref_words"] += len(ref.split())
            ch = clean.get(f"pm57_{r['source_consultation']}")
            if ch and not ch.get("error"):
                L["chance_leaked_words"] += sum(w in only_bg for w in inserted_or_substituted_words(ref, N(ch["hyp"])))
                L["chance_ref_words"] += len(ref.split())
        res["background_leakage_per_100_words"] = {
            c: {"leaked": 100 * v["leaked_words"] / v["ref_words"],
                "chance_level_from_clean_run": (100 * v["chance_leaked_words"] / v["chance_ref_words"]) if v["chance_ref_words"] else None}
            for c, v in sorted(leak.items())}
    return res


def fmt(x, pct=True):
    return "" if x is None else (f"{100 * x:.2f}" if pct else f"{x:.3f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model"); ap.add_argument("--manifest", choices=sorted(MANIFESTS))
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    ap.add_argument("--norm", default="v1", choices=sorted(NORMALIZERS))
    ap.add_argument("--data-root", default=str(REPO / "benchmark_v1" / "data"))
    ap.add_argument("--hyps-dir", default=str(REPO / "results" / "hyps"))
    ap.add_argument("--scores-dir", default=str(REPO / "results" / "scores"))
    ap.add_argument("--summary", action="store_true", help="score every hypothesis file found and write one CSV")
    a = ap.parse_args()

    jobs = []
    if a.summary:
        for f in sorted(Path(a.hyps_dir).glob(f"*/*_{a.split}.jsonl")):
            man = f.stem[: -len(f"_{a.split}")]
            if man in MANIFESTS:
                jobs.append((f.parent.name, man))
    else:
        if not (a.model and a.manifest):
            ap.error("give --model and --manifest, or --summary")
        jobs.append((a.model, a.manifest))

    table = []
    for model, man in jobs:
        hp = Path(a.hyps_dir) / model / f"{man}_{a.split}.jsonl"
        clean = Path(a.hyps_dir) / model / f"pm57_clean_{a.split}.jsonl"
        res = score(a.data_root, man, a.split, hp, a.norm, clean if clean.exists() else None)
        res["model"] = model
        outp = Path(a.scores_dir) / model / f"{man}_{a.split}_{a.norm}.json"
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(res, indent=1), encoding="utf-8")
        o = res["overall"] or {}
        table.append({"model": model, "manifest": man, "split": a.split, "norm": a.norm,
                      "clips_scored": res["clips_scored"], "clips_missing": res["clips_missing"], "clips_failed": res["clips_failed"],
                      "WER_%": fmt(o.get("wer")), "CER_%": fmt(o.get("cer")),
                      "drug_term_acc_%": fmt(res.get("medical_term_accuracy", {}).get("drugs", {}).get("accuracy")),
                      "real_time_factor": fmt(res["real_time_factor"], pct=False)})
        if not a.summary:
            print(f"\n{model} on {man}/{a.split} (normaliser {a.norm}): {res['clips_scored']} clips scored, "
                  f"{res['clips_missing']} missing, {res['clips_failed']} failed")
            print(f"  WER {fmt(o.get('wer'))}%  CER {fmt(o.get('cer'))}%  real-time factor {fmt(res['real_time_factor'], False)}")
            for g, v in res["by_group"].items():
                if v: print(f"  {g:45s} WER {fmt(v['wer']):>7}%  ({v['ref_words']} words, {v['clips']} clips)")
            for k in ("strict_no_flagged_utterances", "strict_doctor", "strict_patient"):
                if res.get(k): print(f"  {k:45s} WER {fmt(res[k]['wer']):>7}%")
            for t, v in res.get("medical_term_accuracy", {}).items():
                print(f"  term accuracy {t:31s} {100 * v['accuracy']:6.2f}%  ({v['terms']} terms)")
            for c, v in res.get("background_leakage_per_100_words", {}).items():
                ch = "" if v["chance_level_from_clean_run"] is None else f"  (chance {v['chance_level_from_clean_run']:.2f})"
                print(f"  leakage {c:37s} {v['leaked']:.2f} per 100 words{ch}")
            print(f"  full results -> {outp}")
    if a.summary and table:
        sp = Path(a.scores_dir).parent / f"summary_{a.split}_{a.norm}.csv"
        with open(sp, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, table[0].keys()); w.writeheader(); w.writerows(table)
        for t in table: print(t)
        print(f"summary -> {sp}")


if __name__ == "__main__":
    main()
