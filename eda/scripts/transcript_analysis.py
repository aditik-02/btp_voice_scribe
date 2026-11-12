#!/usr/bin/env python3
"""
eda/scripts/transcript_analysis.py
Phase 3: Transcript and Language Analysis for Medical Voice Scribe.
Analyzes text corpora from PriMock57 (TextGrids & Clinical Notes),
Eka Medical ASR (Clinical sentences, drug names, dosage, entity spans),
and Svarah (Indic accented general English speech).
Computes lexical stats, vocabulary sizes, TTR, clinical entity distributions, and n-grams.
"""

import os
import sys
import re
import json
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

def tokenize(text: str):
    """Simple alphanumeric tokenizer preserving clinical hyphenations and numbers."""
    # Remove Praat markup like <UNSURE>...</UNSURE>
    cleaned = re.sub(r'<[^>]+>', ' ', text)
    # Split on non-alphanumeric except hyphens
    tokens = re.findall(r'\b[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*\b', cleaned.lower())
    return tokens

def parse_textgrid(tg_path: Path):
    """Extracts all non-empty utterance intervals from a Praat TextGrid file."""
    lines = tg_path.read_text(encoding='utf-8', errors='ignore').splitlines()
    intervals = []
    in_interval = False
    curr_xmin, curr_xmax, curr_text = None, None, None
    for line in lines:
        line = line.strip()
        if line.startswith("intervals ["):
            in_interval = True
            curr_xmin, curr_xmax, curr_text = None, None, None
        elif in_interval:
            if line.startswith("xmin ="):
                curr_xmin = float(line.split("=")[1].strip())
            elif line.startswith("xmax ="):
                curr_xmax = float(line.split("=")[1].strip())
            elif line.startswith("text ="):
                # Handle text spanning multiple lines or quotes
                parts = line.split("=", 1)
                curr_text = parts[1].strip().strip('"')
                if curr_text:
                    intervals.append({
                        "xmin": curr_xmin,
                        "xmax": curr_xmax,
                        "duration": curr_xmax - curr_xmin if curr_xmax and curr_xmin else 0.0,
                        "text": curr_text
                    })
                in_interval = False
    return intervals

def analyze_primock57_transcripts(base_dir: Path):
    print(">>> Analyzing PriMock57 Transcripts & Clinical Notes...")
    tg_dir = base_dir / "primock57" / "transcripts"
    notes_dir = base_dir / "primock57" / "notes"

    tg_files = sorted(tg_dir.glob("*.TextGrid"))
    note_files = sorted(notes_dir.glob("*.json"))

    utterances = []
    doc_utterances = []
    pat_utterances = []

    for tg in tg_files:
        role = "Doctor" if tg.stem.endswith("_doctor") else "Patient"
        intervals = parse_textgrid(tg)
        for it in intervals:
            it["role"] = role
            it["file"] = tg.name
            utterances.append(it)
            if role == "Doctor":
                doc_utterances.append(it)
            else:
                pat_utterances.append(it)

    # Note texts
    notes = []
    for nf in note_files:
        with open(nf) as f:
            data = json.load(f)
            notes.append(data.get("note", ""))

    # Lexical statistics
    all_texts = [u["text"] for u in utterances]
    word_counts = [len(tokenize(t)) for t in all_texts]
    char_counts = [len(t) for t in all_texts]
    all_tokens = [t for text in all_texts for t in tokenize(text)]
    vocab = Counter(all_tokens)

    # Doctor vs Patient token counts
    doc_tokens = [t for u in doc_utterances for t in tokenize(u["text"])]
    pat_tokens = [t for u in pat_utterances for t in tokenize(u["text"])]

    stats = {
        "total_textgrid_files": len(tg_files),
        "total_utterance_intervals": len(utterances),
        "doctor_utterance_count": len(doc_utterances),
        "patient_utterance_count": len(pat_utterances),
        "total_clinical_notes": len(notes),
        "total_tokens": len(all_tokens),
        "unique_vocab_size": len(vocab),
        "type_token_ratio_ttr": len(vocab) / len(all_tokens) if all_tokens else 0.0,
        "hapax_legomena_count": sum(1 for w, c in vocab.items() if c == 1),
        "word_count": {
            "mean": float(np.mean(word_counts)),
            "median": float(np.median(word_counts)),
            "min": int(np.min(word_counts)) if word_counts else 0,
            "max": int(np.max(word_counts)) if word_counts else 0,
            "std": float(np.std(word_counts))
        },
        "char_count": {
            "mean": float(np.mean(char_counts)),
            "median": float(np.median(char_counts)),
            "min": int(np.min(char_counts)) if char_counts else 0,
            "max": int(np.max(char_counts)) if char_counts else 0,
            "std": float(np.std(char_counts))
        },
        "doctor_total_words": len(doc_tokens),
        "patient_total_words": len(pat_tokens),
        "top_25_words": vocab.most_common(25)
    }

    # Clinical entity analysis in PriMock57
    medical_keywords = [
        "pain", "headache", "fever", "cough", "diarrhea", "vomiting", "asthma", "inhaler",
        "paracetamol", "ibuprofen", "blood", "chest", "throat", "stomach", "rash", "infection",
        "antibiotics", "dose", "mg", "tablet", "capsule", "doctor", "hospital", "prescription"
    ]
    clinical_freq = {kw: vocab[kw] for kw in medical_keywords if kw in vocab}
    stats["clinical_keywords_frequency"] = clinical_freq

    return stats

def analyze_eka_medical_transcripts(base_dir: Path):
    print(">>> Analyzing Eka Medical ASR Transcripts & Entities...")
    en_files = sorted((base_dir / "eka_medical_asr" / "en").glob("*.parquet"))
    
    texts = []
    entities_all = []
    recording_contexts = Counter()
    type_concepts = Counter()

    for pf in en_files:
        t = pq.read_table(pf, columns=["text", "type_concept", "recording_context", "medical_entities"])
        df = t.to_pandas()
        texts.extend(df["text"].dropna().tolist())
        recording_contexts.update(df["recording_context"].dropna().tolist())
        type_concepts.update(df["type_concept"].dropna().tolist())
        
        # parse medical_entities
        for ent_str in df["medical_entities"].dropna():
            if ent_str and ent_str != "[]":
                try:
                    parsed = json.loads(ent_str)
                    for item in parsed:
                        # item format: [entity_text, category, [[start, end]]]
                        if len(item) >= 2:
                            entities_all.append((item[0].lower(), item[1]))
                except Exception:
                    pass

    word_counts = [len(tokenize(t)) for t in texts]
    char_counts = [len(t) for t in texts]
    all_tokens = [t for text in texts for t in tokenize(text)]
    vocab = Counter(all_tokens)

    # Group entities by category
    entities_by_cat = defaultdict(Counter)
    for ent_text, cat in entities_all:
        entities_by_cat[cat][ent_text] += 1

    stats = {
        "total_english_records": len(texts),
        "total_tokens": len(all_tokens),
        "unique_vocab_size": len(vocab),
        "type_token_ratio_ttr": len(vocab) / len(all_tokens) if all_tokens else 0.0,
        "hapax_legomena_count": sum(1 for w, c in vocab.items() if c == 1),
        "word_count": {
            "mean": float(np.mean(word_counts)),
            "median": float(np.median(word_counts)),
            "min": int(np.min(word_counts)) if word_counts else 0,
            "max": int(np.max(word_counts)) if word_counts else 0,
            "std": float(np.std(word_counts))
        },
        "char_count": {
            "mean": float(np.mean(char_counts)),
            "median": float(np.median(char_counts)),
            "min": int(np.min(char_counts)) if char_counts else 0,
            "max": int(np.max(char_counts)) if char_counts else 0,
            "std": float(np.std(char_counts))
        },
        "recording_contexts": dict(recording_contexts),
        "type_concepts": dict(type_concepts),
        "top_25_words": vocab.most_common(25),
        "top_drugs": entities_by_cat["drugs"].most_common(20),
        "top_clinical_findings": entities_by_cat["clinical_findings"].most_common(15),
        "top_advices": entities_by_cat["advices"].most_common(10),
        "top_diagnostics": entities_by_cat["diagnostics"].most_common(10)
    }

    # Dosage expressions & units
    dosage_units = ["mg", "ml", "tablet", "tablets", "capsule", "capsules", "syrup", "drops", "od", "bd", "tds", "qid", "sos", "daily", "times", "bedtime"]
    stats["dosage_units_frequency"] = {unit: vocab[unit] for unit in dosage_units if unit in vocab}

    return stats

def analyze_svarah_transcripts(base_dir: Path):
    print(">>> Analyzing Svarah Transcripts...")
    parquet_files = sorted((base_dir / "svarah" / "data").glob("*.parquet"))

    texts = []
    for pf in parquet_files:
        t = pq.read_table(pf, columns=["text"])
        df = t.to_pandas()
        texts.extend(df["text"].dropna().tolist())

    word_counts = [len(tokenize(t)) for t in texts]
    char_counts = [len(t) for t in texts]
    all_tokens = [t for text in texts for t in tokenize(text)]
    vocab = Counter(all_tokens)

    # Check for presence of clinical / medical terms
    clinical_keywords = [
        "doctor", "patient", "medicine", "fever", "cough", "pain", "hospital",
        "paracetamol", "tablet", "dosage", "prescription", "clinic", "diagnosis"
    ]
    clinical_occurrences = {kw: vocab[kw] for kw in clinical_keywords if kw in vocab}

    stats = {
        "total_records": len(texts),
        "total_tokens": len(all_tokens),
        "unique_vocab_size": len(vocab),
        "type_token_ratio_ttr": len(vocab) / len(all_tokens) if all_tokens else 0.0,
        "hapax_legomena_count": sum(1 for w, c in vocab.items() if c == 1),
        "word_count": {
            "mean": float(np.mean(word_counts)),
            "median": float(np.median(word_counts)),
            "min": int(np.min(word_counts)) if word_counts else 0,
            "max": int(np.max(word_counts)) if word_counts else 0,
            "std": float(np.std(word_counts))
        },
        "char_count": {
            "mean": float(np.mean(char_counts)),
            "median": float(np.median(char_counts)),
            "min": int(np.min(char_counts)) if char_counts else 0,
            "max": int(np.max(char_counts)) if char_counts else 0,
            "std": float(np.std(char_counts))
        },
        "top_25_words": vocab.most_common(25),
        "clinical_terms_in_svarah": clinical_occurrences,
        "domain_assessment": "General Indian English (geography, culture, history, civic topics) with near-zero clinical terminology."
    }

    return stats

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    base_data = repo_root / "voice_scribe_data"
    reports_root = repo_root / "eda" / "reports"

    pri_trans = analyze_primock57_transcripts(base_data)
    eka_trans = analyze_eka_medical_transcripts(base_data)
    sva_trans = analyze_svarah_transcripts(base_data)

    comb_summary = {
        "primock57": pri_trans,
        "eka_medical_asr": eka_trans,
        "svarah": sva_trans
    }

    with open(reports_root / "transcript_lexical_summary.json", "w") as f:
        json.dump(comb_summary, f, indent=2)

    print("\nTranscript & Lexical Analysis Complete! Saved to eda/reports/transcript_lexical_summary.json")

if __name__ == "__main__":
    main()
