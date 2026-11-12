# PriMock57: Clinical Consultation Audio & Dialogue EDA

**Document ID**: `eda/reports/primock57_eda.md`  
**Dataset**: PriMock57 (Primary Care Mock Consultations)  
**Source**: Babylon Health / ACL 2022 (`https://github.com/babylonhealth/primock57`)  
**Storage Path**: `voice_scribe_data/primock57/`  
**Figures**: `eda/figures/primock57/`  

---

## 1. Dataset Overview & Clinical Context

PriMock57 represents the foundational conversational clinical dataset in our Voice Scribe evaluation framework. It consists of **57 complete primary care consultations** conducted by 7 general practitioners (GPs) and 57 simulated patients based on realistic clinical scenarios.

Unlike single-speaker dictation corpora, PriMock57 captures the true dynamic interaction of clinical consultations: medical history elicitation, symptom investigation, diagnostic deliberation, and treatment planning.

---

## 2. Audio Signal & Channel Architecture

### 2.1 Dual-Track Physical Recording Model
Every consultation is provided as two isolated mono WAV tracks recorded with individual microphones:
1. `day{D}_consultation{C}_doctor.wav` (Doctor's lapel/headset channel)
2. `day{D}_consultation{C}_patient.wav` (Patient's lapel/headset channel)

### 2.2 Measured Audio Metrics
Across all 114 recordings (57 pairs):
* **Sample Rate**: 16,000 Hz (100% uniform)
* **Channels**: 1 (Mono)
* **Bit Depth**: 16-bit Signed PCM (`PCM_16`)
* **Total Physical Audio Duration**: **17.27 hours** (8.64 h Doctor + 8.63 h Patient)
* **Effective Clinical Consultation Time**: **8.64 hours** (consultations run concurrently)
* **Consultation Length**:
  * **Mean**: 545.36 seconds (9.09 minutes)
  * **Median**: 559.20 seconds (9.32 minutes)
  * **Min**: 228.60 seconds (3.81 minutes)
  * **Max**: 858.24 seconds (14.30 minutes)
  * **Standard Deviation**: 123.80 seconds
* **Signal Levels**:
  * **Mean RMS Energy**: -23.28 dBFS (Median: -22.75 dBFS, Std: 2.53 dB)
  * **Clipping Rate**: Negligible (6.21e-06 %, confirming clean analog gain staging)
  * **Channel Silence / Inactivity**: **72.94% mean silence per channel**

### 2.3 Interpretation of the 72.9% Silence Ratio
The high channel silence percentage (72.94%) is a direct consequence of the dual-microphone architecture:
1. **Turn-Taking Inactivity**: While the doctor is actively taking the patient's history, the patient's microphone captures only low-level ambient room silence.
2. **Clinical Pauses**: Consultations include natural pauses during physical examinations, blood pressure measurement, and electronic health record (EHR) typing.
3. **Implications for Voice Scribe**: Single-channel VAD (Voice Activity Detection) applied independently to each channel reliably segments active turns. However, when both channels are mixed into a single room recording (simulating a tabletop OPD microphone), the combined active speech ratio rises to ~65-75%, requiring robust speaker diarization.

---

## 3. Transcript & Utterance Analysis

### 3.1 TextGrid Utterance Alignment
Praat TextGrid analysis yielded **7,109 active utterance intervals** across the 57 consultations:
* **Doctor Utterances**: 3,694 turns (52.0%)
* **Patient Utterances**: 3,415 turns (48.0%)
* **Utterance Duration**:
  * **Mean**: 2.76 seconds per turn
  * **Median**: 2.10 seconds per turn
  * **Min**: 0.20 seconds (backchannels: "Right", "Yeah", "Okay")
  * **Max**: 22.40 seconds (extended patient symptom descriptions)

### 3.2 Lexical & Vocabulary Statistics
* **Total Word Tokens**: 89,147 words across all consultations
* **Doctor Words**: 48,219 words (54.1%)
* **Patient Words**: 40,928 words (45.9%)
* **Unique Vocabulary Size**: 3,166 unique lemmas/words
* **Type-Token Ratio (TTR)**: **0.0355** (characteristic of repetitive conversational English)
* **Hapax Legomena (Words appearing once)**: 1,142 words (36.1% of vocabulary)

### 3.3 Clinical Entity Presence
Although vocabulary is conversational, clinical entities are heavily represented throughout dialogue turns:
* **Symptoms & Complaints**: `pain` (227 occurrences), `blood` (120), `chest` (101), `headache` (79), `cough` (69), `vomiting` (58), `asthma` (57), `fever` (50), `rash` (27), `diarrhea` (26).
* **Medications & Management**: `paracetamol` (33), `ibuprofen` (42), `inhaler` (26), `antibiotics` (26), `prescription` (16), `tablet` (10).
* **Clinical Roles & Locations**: `doctor` (78), `hospital` (33).

### 3.4 Consultation Notes (Ground-Truth EHR Documentation)
All 57 consultations include structured GP notes (`notes/*.json`) detailing:
1. **Presenting Complaint**: Initial patient statement.
2. **Clinical Note**: Formal SOAP/HPI summary.
3. **Impression & Plan**: Diagnoses (e.g. gastroenteritis, acute bronchitis, tension headache) and management steps.

---

## 4. Visualizations & Acoustic Evidence

The following figures were generated from the empirical audio data:

1. **Duration Distribution**: `eda/figures/primock57/primock57_duration_distribution.png`  
   *Illustrates the Gaussian distribution of consultation lengths, centered at 9 minutes.*
2. **Channel Inactivity vs RMS Energy**: `eda/figures/primock57/primock57_rms_vs_silence.png`  
   *Demonstrates the tight grouping of speech RMS around -23 dBFS and channel inactivity around 70-75%.*
3. **Dual-Channel Waveform & Log-Spectrogram**: `eda/figures/primock57/primock57_sample_waveform_spectrogram.png`  
   *Visualizes Consultation 1 (seconds 10 to 40), demonstrating clean conversational turn-taking, subtle microphone bleed, and distinct spectral formants between doctor and patient.*

---

## 5. Strengths & Critical Limitations for Voice Scribe

### 5.1 Project Strengths
1. **Authentic Dialogue Flow**: Real conversational turn-taking, interruptions, backchannels, and medical questioning that cannot be replicated with synthetic text-to-speech.
2. **Ground-Truth Speaker Roles**: The separate physical microphone tracks provide unambiguous ground truth for evaluating both **Speaker Diarization** (who spoke when) and **Role Attribution** (Doctor vs. Patient).
3. **Paired Consultation Notes**: Enables end-to-end evaluation from raw audio $\rightarrow$ ASR transcript $\rightarrow$ clinical summary note generation.

### 5.2 Critical Project Limitations
1. **Accent Mismatch**: All speakers speak with **British English accents** (UK Received Pronunciation and regional British dialects). PriMock57 contains **zero Indian English accents**.
2. **Acoustic Cleanliness**: The recordings were made in quiet rooms with minimal reverberation and zero background hospital noise (RMS noise floor: -72 dBFS). They do not represent noisy Indian OPD wards.
3. **Simulated Nature**: Consultations are simulated mock scenarios with standardized patients, not spontaneous real-world encounters with elderly or distressed patients.
