# Svarah: Indic-Accented English ASR Benchmark EDA

**Document ID**: `eda/reports/svarah_eda.md`  
**Dataset**: Svarah (Indic Accented English Speech Dataset)  
**Source**: AI4Bharat / Bhashini / MeitY (`https://huggingface.co/datasets/ai4bharat/Svarah`)  
**Storage Path**: `voice_scribe_data/svarah/`  
**Figures**: `eda/figures/svarah/`  

---

## 1. Dataset Overview & Provenance

Svarah is a benchmark dataset created by AI4Bharat to evaluate automatic speech recognition models on Indian English. India's linguistic landscape features diverse phonological transfer effects from native regional mother tongues (L1) into English (L2). Svarah captures this acoustic and phonological variation across multiple Indian regions, states, and mother-tongue backgrounds.

---

## 2. Ingestion & Shard Verification

The evaluation split comprises **3 Apache Parquet files** in `voice_scribe_data/svarah/data/`:
* `test-00000-of-00003.parquet`: **2,219 records** (348.15 MB)
* `test-00001-of-00003.parquet`: **2,219 records** (343.70 MB)
* `test-00002-of-00003.parquet`: **2,218 records** (352.42 MB)
* **Verified Total Test Records**: **EXACTLY 6,656 records** (1.02 GB uncompressed).
* **Data Integrity**: 100% verified; zero missing audio bytes, corrupted headers, or null transcript strings.

---

## 3. Demographics & Regional Accent Diversity

The dataset provides demographic annotations per speaker:

### 3.1 Gender Distribution
* **Female**: **3,579 records (53.8%)**
* **Male**: **3,077 records (46.2%)**
* **Assessment**: Exceptionally well-balanced gender distribution, preventing acoustic bias toward male or female vocal tract resonances.

### 3.2 Age-Group Distribution
* **30–45 years**: **2,670 records (40.1%)**
* **18–30 years**: **2,219 records (33.3%)**
* **45–60 years**: **1,305 records (19.6%)**
* **60+ years**: **462 records (6.9%)**

### 3.3 Representation Across 19 Primary Native Languages (L1)
Phonetic interference in Indian English originates primarily from the speaker's first language. Svarah evaluates 19 distinct L1 backgrounds:

| Primary Language | Record Count | Percentage | Linguistic Family |
| :--- | :---: | :---: | :--- |
| **Nepali** | 599 | 9.0% | Indo-Aryan |
| **Kannada** | **577** | **8.7%** | **Dravidian (Core Project Target)** |
| **Urdu** | 514 | 7.7% | Indo-Aryan |
| **Malayalam** | 503 | 7.6% | Dravidian |
| **Maithili** | 462 | 6.9% | Indo-Aryan |
| **Odia** | 456 | 6.9% | Indo-Aryan |
| **Bodo** | 402 | 6.0% | Sino-Tibetan |
| **Tamil** | 384 | 5.8% | Dravidian |
| **Telugu** | 334 | 5.0% | Dravidian |
| **Kashmiri** | 310 | 4.7% | Dardic / Indo-Aryan |
| **Konkani** | 302 | 4.5% | Indo-Aryan |
| **Bengali** | 297 | 4.5% | Indo-Aryan |
| **Hindi** | **256** | **3.8%** | **Indo-Aryan (Core Project Target)** |
| **Dogri** | 255 | 3.8% | Indo-Aryan |
| **Gujarati** | 242 | 3.6% | Indo-Aryan |
| **Marathi** | 231 | 3.5% | Indo-Aryan |
| **Assamese** | 205 | 3.1% | Indo-Aryan |
| **Punjabi** | 189 | 2.8% | Indo-Aryan |
| **Sindhi** | 138 | 2.1% | Indo-Aryan |

### 3.4 Geographic State Representation
Speakers originate from **17 Indian states and union territories**, led by West Bengal (11.9%), Karnataka (11.6%), Assam (10.2%), Kerala (8.6%), Jammu & Kashmir (8.5%), Gujarat (8.5%), Bihar (7.8%), Odisha (7.3%), Goa (6.3%), and Maharashtra (6.1%).

---

## 4. Audio Signal Analysis

* **Sample Rate**: 16,000 Hz (100% uniform)
* **Channels**: 1 (Mono)
* **Audio Storage**: Embedded byte buffers decoded into 16 kHz float32 arrays.
* **Duration Metrics (Full 6,656 Corpus)**:
  * **Total Audio Duration**: **9.61 hours** (34,608 seconds)
  * **Mean Duration**: 5.20 seconds (Std: 4.57s)
  * **Median Duration**: 4.21 seconds
  * **Min Duration**: 0.10 seconds
  * **Max Duration**: 29.87 seconds
* **Signal Levels**:
  * **Mean RMS Energy**: -24.47 dBFS (Median: -23.26 dBFS, Std: 7.32 dB)
  * **Silence Ratio**: **23.05%** (Prompt-based continuous read speech with short initial/final padding)
  * **Clipping Rate**: 0.00011% (Extremely clean digital capture)

---

## 5. Transcript & Lexical Analysis: General English vs. Clinical Domain

### 5.1 Lexical Diversity
* **Total Tokens**: 69,593 words
* **Unique Vocabulary**: 8,623 unique words
* **Type-Token Ratio (TTR)**: **0.1239** (Substantially higher than PriMock57's 0.0355 due to diverse topical coverage).
* **Hapax Legomena**: 4,682 words (54.3% of vocabulary).

### 5.2 Critical Domain Distinction: Svarah is NOT Medical Speech
A search across all 69,593 tokens confirms that Svarah does not contain clinical dialogue:
* `doctor`: 3 occurrences
* `patient`: 1 occurrence
* `medicine`: 6 occurrences
* `hospital`: 10 occurrences
* `clinic`: 4 occurrences
* `fever`: 1 occurrence
* `cough`: 2 occurrences
* `pain`: 1 occurrence
* Drug names (e.g. Paracetamol, Dolo, Azithromycin, Metformin): **0 occurrences**.

### Research Finding
Svarah consists entirely of **general Indian English read and spontaneous speech** (geography, history, culture, architecture, and civic administration). It cannot be used to evaluate medical terminology or clinical transcription accuracy.

---

## 6. Visualizations & Acoustic Evidence

1. **Duration Distribution**: `eda/figures/svarah/svarah_duration_distribution.png`  
   *Demonstrates the prompt-style distribution of utterance lengths, skewed toward 3–6 seconds.*
2. **RMS Energy by Gender**: `eda/figures/svarah/svarah_rms_by_gender.png`  
   *Confirms balanced acoustic recording levels between male (-23.8 dBFS) and female (-24.9 dBFS) speakers.*
3. **Accent Waveforms & Spectrograms**: `eda/figures/svarah/svarah_accent_waveforms_spectrograms.png`  
   *Illustrates spectral differences across Kannada, Hindi, and Malayalam L1 speaker accents.*

---

## 7. Role in the Medical Voice Scribe Project

### 7.1 What Svarah Achieves
1. **Gold-Standard Indian English Acoustic Benchmark**: Serves as the primary benchmark to ensure our chosen ASR models (e.g., Whisper-large-v3, Conformer, IndicWav2Vec) do not degrade on Indian regional accents.
2. **Specific Support for Kannada & Hindi L1**: Contains 577 Kannada-accented and 256 Hindi-accented English recordings, directly addressing our project's regional language roadmap.
3. **Robustness to Prosodic Variations**: Indian English syllable timing, retroflex consonants ($/ʈ/, /ɖ/$), and non-aspirated stops are represented.

### 7.2 What Svarah Cannot Achieve
1. **Zero Medical Vocabulary**: Cannot benchmark medical term error rate (WER on drugs, dosages, diagnoses).
2. **Zero Conversational Dynamics**: No turn-taking, no multi-speaker diarization, no doctor-patient dialogue.
