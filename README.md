# Voice Scribe

A voice-based medical scribe for noisy Indian OPD consultations: transcribe only the doctor–patient conversation, label who said what, and handle Indian English first, then Hindi, Kannada and code-switched speech.

This repository merges the two strands of work done so far:

- **Research and raw-data EDA** (dataset search, catalogue, licences, raw-audio profiling)
- **The English benchmark v1.1 and its EDA** (fixed dev/test splits, cleaned references, simulated noisy OPD audio, scoring rules) plus a single model-evaluation harness

## Layout

```
README.md                  this file
CORRECTIONS.md             facts in earlier documents that turned out to be wrong, with the correct values
benchmark_v1/              THE shared test set: build scripts, README, benchmark EDA
  scripts/                 run_all.py builds everything; normalize.py holds the scoring rules (v1, v2)
  eda/                     EDA of the built test set (eda_v1.ipynb, figures, tables)
  data/                    built test set (not in git; rebuild with run_all.py)
experiments/
  asr/                     model evaluation: run_asr.py (transcribe), score.py (metrics), models.py (adapters)
  benchmark_diarization.py diarization scoring scaffold (to be wired to the benchmark next)
  benchmark_attribution.py doctor/patient role-attribution metrics
research/audio-datasets/   dataset search, catalogue, comparison, access and licence notes
eda/                       EDA of the raw downloads (inventory, signal levels, vocabulary, data quality)
prototype/aws-dashboard/   early Streamlit demo (Amazon Transcribe + Bedrock)
results/                   transcripts and scores written by the harness (created on first run)
eka_medical_asr/ svarah/ sources/   raw downloads (not in git)
```

## 1. Build the test set (once per machine)

```
python -m pip install -r experiments/asr/requirements/base.txt
hf download ekacare/eka-medical-asr-evaluation-dataset --repo-type dataset --local-dir eka_medical_asr
hf download ai4bharat/Svarah --repo-type dataset --local-dir svarah      # accept its terms on Hugging Face first
python benchmark_v1/scripts/run_all.py
```

`sources/` holds the PriMock57 transcripts and notes (github.com/babylonhealth/primock57) and the MS-SNSD noise clips (github.com/microsoft/MS-SNSD). `run_all.py` downloads the PriMock57 audio, builds everything into `benchmark_v1/data/` and checks the result against the reference build: it must end with five `OK` lines. Details of every file and column: `benchmark_v1/README.md`.

| Part | Manifest name | Dev | Test |
|---|---|---|---|
| Eka Medical ASR, English (Indian doctors, drug names) | `eka_en` | 735 clips, 1.6 h | 2,884 clips, 6.8 h |
| Svarah (Indian-English accents) | `svarah` | 1,351 clips, 2.2 h | 5,305 clips, 7.4 h |
| PriMock57 utterances (doctor / patient tracks) | `pm57_utt` | 1,285 | 5,266 |
| PriMock57 full consultations, clean | `pm57_clean` | 11, 1.7 h | 46, 7.0 h |
| PriMock57 noisy versions (10 conditions each) | `pm57_noisy` | 110 | 460 |

## 2. Evaluate a model

One environment per model family (their libraries conflict). From the repo root, on the GPU server:

```
python -m venv .venv-hf && source .venv-hf/bin/activate
pip install -r experiments/asr/requirements/hf.txt
hf auth login                                   # needed for gated models (Parrotlet, IndicConformer)

# 1. pipeline check without a model: must give 0% WER
python experiments/asr/run_asr.py --model echo --manifest eka_en --split dev --limit 50 --device cpu
python experiments/asr/score.py   --model echo --manifest eka_en --split dev

# 2. smoke test the real model on 3 clips, read the output, then run the dev split
python experiments/asr/run_asr.py --model whisper-large-v3 --manifest eka_en --split dev --limit 3
python experiments/asr/run_asr.py --model whisper-large-v3 --manifest eka_en --split dev
python experiments/asr/score.py   --model whisper-large-v3 --manifest eka_en --split dev

# 3. one table of everything scored so far
python experiments/asr/score.py --summary --split dev
```

Runs resume where they stopped; failed clips are logged and retried on the next run. Transcripts go to `results/hyps/<model>/`, scores to `results/scores/<model>/`.

**Order of work:** every model on **dev** first (`eka_en`, `svarah`, `pm57_utt`, `pm57_clean`, `pm57_noisy`), shortlist, then the shortlist on **test**. Never tune anything on test.

### Models

Adapters exist for the free open models. Loading code follows each official model card (Nov 2026) and is untested on a GPU: run the 3-clip smoke test first for each.

| `--model` | Model | Languages | Environment | Notes |
|---|---|---|---|---|
| `whisper-large-v3` | OpenAI Whisper large-v3 | en, hi, kn | hf | baseline |
| `whisper-large-v3-turbo` | Whisper large-v3 turbo | en, hi, kn | hf | speed comparison |
| `parrotlet-a-en-5b` | Eka Care Parrotlet | en | hf | gated; 28 s chunks |
| `indicconformer-600m` | AI4Bharat IndicConformer | hi, kn | hf | gated |
| `indicwhisper` | AI4Bharat IndicWhisper (Vistaar) | hi, kn | hf | `--checkpoint <unzipped folder>` |
| `medasr` | Google MedASR | en | medasr | Health AI Developer Foundations terms |
| `qwen3-asr-1.7b` | Qwen3-ASR 1.7B | en, hi | qwen | |
| `parakeet-tdt-0.6b-v2` | NVIDIA Parakeet TDT | en | nemo | |
| `canary-qwen-2.5b` | NVIDIA Canary-Qwen 2.5B | en | nemo (GitHub main) | 35 s chunks |
| `echo` | returns the reference | – | base | pipeline check only |

Still to add: SraVaani and Omnilingual ASR (Hindi/Kannada phase), and the API models (Gemini 3.5 Transcribe / 3.8 Flash free tier; Chirp 3, Amazon Transcribe, Sarvam Saaras v4 and Sarvam Audio, paid). The full list with costs and reasons is in the EDA Findings doc.

### Metrics (`score.py`)

- WER and CER **pooled over all words** of a group, never averaged per clip. CER ignores spaces.
- Breakdowns: Eka by clip type, Svarah by first language, PriMock57 utterances by doctor/patient plus a strict score without flagged utterances, noisy PriMock57 by condition.
- Eka medical-term accuracy per term type, with drugs reported separately.
- Background-speech leakage for talker conditions: output words that come from the background conversation and never occur in the consultation, per 100 reference words. It is a conservative count (words shared with the consultation are not counted); the clean run gives the chance level.
- Real-time factor (decoding time ÷ audio length).
- Normaliser: `--norm v1` (default: lowercase, no punctuation, fillers removed) or `--norm v2` (also splits "40Mg" → "40 mg", unifies unit words, converts number words to digits). Pick one before reporting test results and use it everywhere.

## Documents

- Dataset Selection & English Benchmark v1.1: https://claude.ai/artifact/6W6WveMJ4zDQedAzCuigoP
- Dataset Progress Report: https://claude.ai/artifact/4EFMBwQWyFSfha9aVYA9wP
- EDA Findings & Next Steps (incl. the 17-model list): https://claude.ai/artifact/4hniqRdtiuwoexfVLrNtXf

## What was merged, replaced or left out

| From the research/EDA repo | Status |
|---|---|
| `research/audio-datasets/` | kept as is (see `CORRECTIONS.md`) |
| `eda/` (raw-data EDA) | kept as a record. Its scripts expect the old `voice_scribe_data/<dataset>` layout and are not re-run here |
| `experiments/benchmark_attribution.py`, `benchmark_diarization.py` | kept; next to be wired to the benchmark for the diarization track |
| `experiments/simulate_clinical_mix.py` | left out: replaced by the built and verified noisy set in `benchmark_v1` |
| `experiments/benchmark_wer_cer.py`, `run_benchmarks.py`, `results_summary.md` | left out: replaced by `experiments/asr/` (same WER/CER/RTF, plus pooled scoring, term accuracy and leakage) |
| `aws-dashboard/` | moved to `prototype/aws-dashboard/` |

## Next

1. Run the six free English models on dev: Whisper large-v3, Parrotlet, Qwen3-ASR, Canary-Qwen, Parakeet, MedASR.
2. Add the Eka Hindi split (320 clips) as a small Hindi test before DISPLACE-M access arrives.
3. Wire the diarization scaffold to PriMock57 (pyannote 3.1 on the mixed consultations; speaker turns are in `benchmark_v1/data/primock57/references/`).
4. Add API adapters (Gemini first, on the free tier, public data only).
