# BTP Voice Scribe: Shortlisted Top 5 Datasets

Following rigorous evaluation of 22 candidate corpora across 7 scoring dimensions, the following 5 datasets are shortlisted as the primary evaluation suite for the Voice Scribe pipeline.

---

## 1. PriMock57 (`primock57`) — Best End-to-End Primary Care Benchmark

* **Official Repository**: [https://github.com/babylonhealth/primock57](https://github.com/babylonhealth/primock57)
* **Citation**: Papadopoulos Korfiatis et al., *"PriMock57: A Dataset of Primary Care Mock Consultations"*, ACL 2022 / arXiv:2204.00333.
* **Access Type**: Open Access (Direct download via Git LFS / GitHub CDN).
* **License**: Creative Commons Attribution 4.0 International (**CC-BY-4.0**).
* **Modality & Audio**: 57 primary care mock consultations (~8.6 hours total, 17.3 hours across separated tracks). 16 kHz 16-bit mono WAV.
* **Annotations**: 
  - Utterance-level manual transcriptions with millisecond start/end intervals in Praat `TextGrid` format.
  - Separate physical audio channels for Doctor and Patient (`dayX_consultationYY_doctor.wav` / `_patient.wav`).
  - Clinician-written consultation notes in JSON format with clinician-highlighted medical entities.
* **Pipeline Alignment**:
  - **ASR**: Evaluate Word Error Rate (WER) and Medical Terminology Error Rate on spontaneous medical consultation dialogue.
  - **Diarization**: By mixing the two isolated channels with controlled SNR and overlap ratios, precise Diarization Error Rate (DER) can be measured against ground truth.
  - **Role Attribution**: Perfect ground truth for classifying Doctor vs. Patient channels.
  - **Clinical Notes**: Direct evaluation of clinical note generation from transcripts against notes written by consulting clinicians.
* **Limitations**: Mock/simulated consultations based on case cards (not real patients). British English accent only.

---

## 2. MeDial-Speech (`medial_speech`) — Best Large-Scale Doctor-Patient Speech Benchmark

* **Official Repository**: [https://huggingface.co/datasets/hcuayahu/MeDial-Speech](https://huggingface.co/datasets/hcuayahu/MeDial-Speech)
* **Citation**: H. Cuayahuitl and G. Jang, *"A Dataset of Robot-Patient and Doctor-Patient Medical Dialogues for Spoken Language Processing Tasks"*, IEEE ICASSP 2026 / arXiv:2605.26747.
* **Access Type**: Open Access (Direct download from Hugging Face).
* **License**: Creative Commons Attribution NonCommercial 4.0 (**CC-BY-NC-4.0**).
* **Modality & Audio**: Over **111 hours** of unaugmented speech recordings across 9.26 GB of zip archives (`MeDial-Speech_part1.zip` & `part2.zip`). Lossless 16 kHz WAV.
* **Annotations**:
  - Organized by dialogue folder with turn-level `.wav` files and corresponding `.txt` transcripts.
  - Explicit speaker role annotations (`[DOCTOR]` vs. `[PATIENT]` vs. virtual patient).
  - Speech segmentation turn annotations.
  - Evaluation subsets for 4 medical conditions: Lewy body dementia, heart failure, shoulder pain, and angina.
* **Pipeline Alignment**:
  - **ASR**: Real conversational multi-turn dialogue with patient symptoms, history, and clinician responses.
  - **Role Attribution**: Directly benchmark classifiers predicting whether a spoken turn originated from a clinician or patient.
* **Limitations**: Non-commercial license (CC-BY-NC-4.0); focuses on four specific clinical scenarios.

---

## 3. Eka Medical ASR Evaluation Dataset (`eka_medical_asr`) — Best Indian Clinical Speech Benchmark

* **Official Repository**: [https://huggingface.co/datasets/ekacare/eka-medical-asr-evaluation-dataset](https://huggingface.co/datasets/ekacare/eka-medical-asr-evaluation-dataset)
* **Citation**: Eka Care AI Research, 2024.
* **Access Type**: Open Access (Direct download / streaming via Hugging Face Hub).
* **License**: **MIT License** (Fully open for research and commercial use).
* **Modality & Audio**: 3,939 audio recordings (~6.2 hours). 16 kHz audio embedded in Parquet format.
  - English (`en` split): 3,619 recordings (1.81 GB).
  - Hindi (`hi` split): 320 recordings (160 MB).
* **Annotations**:
  - High-precision medical transcripts.
  - Tagged medical entity types: branded Indian pharmaceutical products (e.g., Augmentin, Dolo, Pan-D), generic dosages, medical procedures, and clinical sentences.
  - Sourced from practicing doctors and students across multiple Indian medical colleges.
* **Pipeline Alignment**:
  - **Indian Accent Adaptation**: Critical stress-test for speech recognition on Indian English accents and phonology.
  - **Pharma Brand Recognition**: Only public benchmark testing ASR recognition of drug brand names common in Indian clinical practice.
* **Limitations**: Isolated medical utterances and dictated sentences rather than full two-way multi-turn consultations.

---

## 4. Synth-DoPaCo (`synth_dopaco`) — Best High-Volume Synthetic Consultation & Note Corpus

* **Official Repository**: [https://huggingface.co/datasets/Play-Your-Part/Synth-DoPaCo](https://huggingface.co/datasets/Play-Your-Part/Synth-DoPaCo)
* **Citation**: JSALT 2025 Play-Your-Part Team, *"BeTraC 2026: Beyond Transcription Challenge"*, arXiv:2604.06138.
* **Access Type**: Open Access (WebDataset shards on Hugging Face).
* **License**: Creative Commons Attribution 4.0 International (**CC-BY-4.0**).
* **Modality & Audio**: **8,800 full doctor-patient consultations** (~1,329 hours total). 16 kHz mono Opus audio in TAR shards.
  - `dev` split: 400 dialogues (1 shard, 469 MB).
  - `train` split: 7,200 dialogues (9 shards, 8.7 GB).
* **Annotations**:
  - Synchronized `.transcript.txt` and `.opus` audio.
  - Turn-level metadata `.json` defining speaker personas, generation parameters, and dialogue turns.
  - Paired ground-truth `.soap.txt` target clinical notes for every dialogue.
  - Room acoustics simulation with 66 background noise / clinic event classes.
* **Pipeline Alignment**:
  - **Full Pipeline Stress-Testing**: Provides the scale needed for training or fine-tuning end-to-end models on long-context medical audio (conversations range from 2 to 47 minutes).
  - **Audio-to-SOAP**: Evaluates hallucination and clinical fact retention from speech to structured clinical note.
* **Limitations**: Synthetic audio generated via Kokoro-82M (more fluent and less hesitant than natural human speech).

---

## 5. AMI Meeting Corpus (`ami_corpus`) — Gold Standard for Conversational Speaker Diarization

* **Official Repository**: [https://groups.inf.ed.ac.uk/ami/corpus/](https://groups.inf.ed.ac.uk/ami/corpus/)
* **Citation**: Carletta et al., *"The AMI Meeting Corpus: A Pre-announcement"*, 2005.
* **Access Type**: Open Access (Direct download via HTTP).
* **License**: Creative Commons Attribution 4.0 International (**CC-BY-4.0**).
* **Modality & Audio**: 100 hours of multi-party spontaneous conversational audio. Lossless 16 kHz WAV across headset mics (IHM), lapel mics, and multiple distant microphone arrays (MDM).
* **Annotations**:
  - Full word-level and turn-level timestamps.
  - Synchronized speaker IDs, speech overlaps, laughter, and non-speech vocalizations.
* **Pipeline Alignment**:
  - **Speaker Diarization (pyannote.audio / NeMo)**: The international gold standard for measuring Diarization Error Rate (DER), Jaccard Error Rate (JER), and speech separation in multi-speaker meeting rooms.
* **Limitations**: Non-medical corporate project meetings (no clinical terminology or doctor/patient roles).

---

## Summary of Shortlist Coverage

| Target Capability | Primary Shortlisted Dataset | Secondary Shortlisted Dataset |
| :--- | :--- | :--- |
| **Real Clinician Teleconsultation** | `primock57` | `medial_speech` |
| **Multi-turn Clinical Speech (100h+)** | `medial_speech` | `synth_dopaco` |
| **Indian English Clinical Accents** | `eka_medical_asr` | `ai4bharat/Svarah` |
| **Clinical Note (SOAP) Benchmarking** | `primock57` | `synth_dopaco` / `aci_bench` (text) |
| **Conversational Speaker Diarization** | `ami_corpus` | `voxconverse` |

---

## 6. Acoustic Feasibility & Background-Speech Isolation Audit

An exhaustive physical inspection of downloaded audio samples was conducted across all shortlisted datasets (detailed in [TARGET_AUDIO_FEASIBILITY_REPORT.md](TARGET_AUDIO_FEASIBILITY_REPORT.md)):

* **`primock57`**: Proved to be isolated VoIP tracks (-92 dBFS noise floor). It has perfect consultation transcripts and isolated channels, but **zero background chatter or clinic noise**.
* **`medial_speech`**: Sequential turns between Robot/Doctor and Patient in quiet rooms (-53 dBFS floor). No overlapping voices or background chatter.
* **`eka_medical_asr`**: Single-doctor read dictations (10s clips); zero patient speech, zero multi-speaker interaction.
* **`synth_dopaco`**: Synthetic Kokoro-82M TTS audio with point sound effects (`[pen_clicking]`); no competing conversations.
* **`ami_corpus`**: Realistic 4-speaker meeting room overlaps and distant arrays, but 100% non-medical with no target vs. background separation.

**Conclusion**: No single shortlisted dataset meets our background-speech isolation requirement out-of-the-box. We recommend combining `primock57` and `eka_medical_asr` with the **`ClinicalMix` simulation protocol** (adding competing talkers from Svarah/MeDial-Speech and DEMAND noise) to maintain 100% uncompromised ground truth.
