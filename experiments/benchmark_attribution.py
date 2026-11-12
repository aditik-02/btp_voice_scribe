#!/usr/bin/env python3
"""
Benchmark module for Doctor vs. Patient Speaker Role Attribution.
Evaluates accuracy, precision, recall, and F1-score of assigning clinical
speaker roles ('Doctor' vs. 'Patient') to diarized speech turns.
"""

from typing import Dict, List, Tuple

def compute_attribution_metrics(ref_roles: List[str], hyp_roles: List[str]) -> Dict[str, float]:
    """Computes binary classification metrics for Doctor vs. Patient role attribution."""
    if len(ref_roles) != len(hyp_roles) or len(ref_roles) == 0:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "total_turns": len(ref_roles)}

    correct = 0
    tp, fp, fn, tn = 0, 0, 0, 0  # Positive class = 'doctor'

    for r, h in zip(ref_roles, hyp_roles):
        r_clean = r.lower().strip()
        h_clean = h.lower().strip()
        if r_clean == h_clean:
            correct += 1

        if r_clean == "doctor" and h_clean == "doctor":
            tp += 1
        elif r_clean != "doctor" and h_clean == "doctor":
            fp += 1
        elif r_clean == "doctor" and h_clean != "doctor":
            fn += 1
        else:
            tn += 1

    total = len(ref_roles)
    acc = correct / total if total > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "total_turns": total,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn
    }

SUPPORTED_ATTRIBUTION_MODELS = [
    "heuristic-turn-length-classifier",
    "clinical-llm-role-prompting",
    "acoustic-voice-profile-classifier"
]

def run_attribution_evaluation(model_name: str, transcript_turns: List[Dict[str, str]]) -> Dict[str, any]:
    """Scaffold evaluation runner for speaker role attribution. Unrun = 'Not run'."""
    if model_name not in SUPPORTED_ATTRIBUTION_MODELS:
        raise ValueError(f"Attribution model {model_name} not supported.")

    return {
        "model": model_name,
        "status": "Not run",
        "accuracy": None,
        "f1_score": None,
        "real_time_factor": None
    }

if __name__ == "__main__":
    refs = ["doctor", "patient", "doctor", "patient", "doctor"]
    hyps = ["doctor", "patient", "patient", "patient", "doctor"]
    metrics = compute_attribution_metrics(refs, hyps)
    print("Role Attribution Benchmark Unit Verification:")
    print("Reference roles: ", refs)
    print("Hypothesis roles:", hyps)
    print("Metrics:         ", metrics)
