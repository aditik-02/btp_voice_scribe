# BTP Voice Scribe: Medical Audio Dataset Discovery & Benchmarking Catalogue

[![Validation Status](https://img.shields.io/badge/Catalog%20Validation-Passing-success)](scripts/validate_catalog.py)
[![Evidence Ledger](https://img.shields.io/badge/Evidence%20Ledger-242%20Claims%20Verified-blue)](EVIDENCE_LEDGER.csv)
[![License](https://img.shields.io/badge/License-CC--BY--4.0-green.svg)](../../LICENSE)

## 1. Project Context & Purpose
The **BTP Voice Scribe** project develops an automated ambient clinical intelligence system tailored for healthcare:
$$\text{Audio} \xrightarrow{\text{ASR}} \text{Transcribed Speech} \xrightarrow{\text{Diarization}} \text{Speaker Turns} \xrightarrow{\text{Attribution}} \text{Doctor / Patient} \xrightarrow{\text{LLM}} \text{Clinical Note (SOAP)}$$

This research directory establishes a comprehensive, phase-wise, evidence-first catalogue of every downloadable audio dataset capable of evaluating or training any component of this pipeline, backed by empirical verification and zero hallucination.

---

## 2. Directory Structure & Deliverables

```
research/audio-datasets/
├── README.md                          # Master catalogue documentation (this file)
├── TARGET_AUDIO_FEASIBILITY_REPORT.md # Empirical verification & acoustic feasibility report
├── SEARCH_PLAN.md                     # Initial search plan & 166-keyword universe
├── RESEARCH_LOG.md                    # Detailed log of search execution & seed verifications
├── EVIDENCE_LEDGER.csv                # 253-row evidence ledger with full claim tracing
├── dataset_catalog.csv                # 23 candidate datasets in standardized CSV schema
├── dataset_catalog.json               # Full JSON representation matching CSV catalog
├── DATASET_COMPARISON.md              # 7-dimension scoring rubric, comparison matrix & gap analysis
├── SHORTLIST.md                       # Deep analysis of the Top 5 recommended datasets
├── DATASET_ACCESS_GUIDE.md            # Step-by-step acquisition & download guide
├── DATASET_LICENSES_AND_PRIVACY.md    # Legal compliance, HIPAA/GDPR/DPDP & ethical review
├── MANIFEST_TEMPLATE.csv              # Standardized audio sample manifest format
├── DOWNLOADS.md                       # Download audit log, checksums & storage estimates
├── references.bib                     # BibTeX entries for all cited papers and datasets
└── scripts/
    ├── discover_hf.py                 # Hugging Face Hub automated discovery script
    ├── discover_zenodo.py             # Zenodo REST API discovery script
    ├── check_links.py                 # Link verification & HTTP status checker
    ├── validate_catalog.py            # Automated CSV/JSON/Ledger parity validator
    └── build_catalog.py               # Programmatic catalog builder
```

---

## 3. The Top 5 Shortlisted Datasets

| Rank | Dataset ID | Name | Hours | Modality & Annotations | License | Access | Key Role in Pipeline |
| :---: | :--- | :--- | :---: | :--- | :--- | :---: | :--- |
| **1** | **`primock57`** | [PriMock57](https://github.com/babylonhealth/primock57) | 8.6h | Isolated Doctor & Patient WAV channels, TextGrid transcripts, clinician consultation notes | CC-BY-4.0 | Open | **Best Overall End-to-End Benchmark** (Audio $\rightarrow$ ASR $\rightarrow$ Diarization $\rightarrow$ Role $\rightarrow$ Notes) |
| **2** | **`medial_speech`** | [MeDial-Speech](https://huggingface.co/datasets/hcuayahu/MeDial-Speech) | 111.0h | 111h Doctor-Patient & Robot dialogue audio turns, explicit `[DOCTOR]` / `[PATIENT]` tags | CC-BY-NC-4.0 | Open | **Large-Scale Spoken Clinical Dialogue & Role Attribution** |
| **3** | **`eka_medical_asr`** | [Eka Medical ASR](https://huggingface.co/datasets/ekacare/eka-medical-asr-evaluation-dataset) | 6.2h | 3,939 Indian doctor recordings (Indian English & Hindi), branded pharmaceuticals | MIT | Open | **Indian Accents & Pharmaceutical Entity Recognition** |
| **4** | **`synth_dopaco`** | [Synth-DoPaCo](https://huggingface.co/datasets/Play-Your-Part/Synth-DoPaCo) | 1,329h | 8,800 doctor-patient visits, WebDataset Opus audio, dialogue turns, target SOAP notes | CC-BY-4.0 | Open | **High-Scale Long-Context Visit Summarization** |
| **5** | **`ami_corpus`** | [AMI Meeting Corpus](https://groups.inf.ed.ac.uk/ami/corpus/) | 100.0h | Multi-channel audio (headset/lapel/arrays), precise word/turn timestamps & speaker IDs | CC-BY-4.0 | Open | **Gold Standard Conversational Diarization & Overlap** |

---

## 4. Classification Breakdown (Categories A to H)

- **Category A: Best Overall Fit**: `primock57`, `medial_speech`, `synth_dopaco`.
- **Category B: Medical Speech-to-Text Benchmarking**: `modulate_synthetic_dictation`, `medical_speech_intent`.
- **Category C: Conversational Speaker Diarization**: `ami_corpus`, `voxconverse`.
- **Category D: Doctor vs Patient Role Attribution**: `medial_speech`, `primock57`.
- **Category E: Multilingual & Indian Context**: `eka_medical_asr`, `svarah`, `indicvoices`, `openslr_mucs2021`, `openslr_hindi1111`.
- **Category F: Small Datasets for First Tests**: `pauleyc_radiology_iphone`.
- **Category G: Supplementary General Speech**: `librispeech`, `common_voice`.
- **Category H: Restricted, Gated, Unsuitable or Unverified**:
  * *Challenge Gated / Encrypted*: `displace_2026` (IISc LEAP Lab DUA & zip encryption password).
  * *Text-only (No Audio)*: `aci_bench`, `mts_dialog`.
  * *Gated / 401 Restricted*: `whissleai_simulated_exams`.
  * *Credentialed Clinical*: `physionet_egd_cxr`, `physionet_b2ai_voice`.
  * *Consortium Gated*: `dihard3_clinical` (LDC DUA).
  * *Commercial Enterprise*: `defined_ai_doctor_patient`.

---

## 5. Feasibility Audit: Ambient Audio & Background Speech

> [!IMPORTANT]
> **Audio Verification Findings**: As established in [TARGET_AUDIO_FEASIBILITY_REPORT.md](TARGET_AUDIO_FEASIBILITY_REPORT.md), **no single open dataset in the world** contains live doctor-patient consultations with simultaneous competing background speech, clinic environmental noise, and pure target-only reference transcripts.
>
> - **`primock57` & `medial_speech`**: Clean isolated VoIP/telemedicine channels with a -92 dBFS noise floor; zero background speech or clinic noise.
> - **`eka_medical_asr`**: Single-doctor dictated prescription sentences (10s chunks); zero patient dialogue or multi-speaker interaction.
> - **`ami_corpus`**: Gold standard for multi-party conversational overlap and far-field arrays, but 100% non-medical with all 4 speakers in the same target discussion.
> - **`displace_2026`**: Real ASHA field recordings in India with noise and diarization, but encrypted behind the official IISc challenge agreement.
>
> **Recommended Strategy**: Combine `primock57` (clean target consultations) + `eka_medical_asr` (Indian accents & drug entities) + `ami_corpus` (diarization engine baseline) with the **`ClinicalMix` Controlled Simulation Protocol** to benchmark background-speech isolation with untainted ground truth.

---

## 6. Automation & Validation Scripts

### Validate Catalog & Evidence Parity
```bash
python3 research/audio-datasets/scripts/validate_catalog.py
```
Checks schema completeness, CSV/JSON parity, and verifies that every single dataset maps to verified rows in `EVIDENCE_LEDGER.csv`.

### Verify All Remote URLs
```bash
python3 research/audio-datasets/scripts/check_links.py research/audio-datasets/EVIDENCE_LEDGER.csv evidence_url
```

### Run Discovery Tools
```bash
# Query Hugging Face Hub for newly published medical speech corpora
python3 research/audio-datasets/scripts/discover_hf.py

# Query Zenodo REST API for datasets
python3 research/audio-datasets/scripts/discover_zenodo.py
```

---

## 6. Benchmark Scaffolding (`experiments/`)

Evaluation scripts are established under `experiments/`:
- `experiments/benchmark_wer_cer.py`: Computes Word Error Rate and Character Error Rate with medical text normalization.
- `experiments/benchmark_diarization.py`: Evaluates Diarization Error Rate (DER) and speech overlap.
- `experiments/benchmark_attribution.py`: Evaluates Doctor vs. Patient turn attribution accuracy and F1 score.
- `experiments/run_benchmarks.py`: Orchestration script tracking Real-Time Factor (RTF) and cost per hour.
- `experiments/results_summary.md`: Benchmark results table (all unrun models explicitly marked `Not run`).

Run benchmark scaffolding:
```bash
python3 experiments/run_benchmarks.py research/audio-datasets/MANIFEST_TEMPLATE.csv
```
