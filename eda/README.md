# Medical Voice Scribe: Exploratory Data Analysis (EDA) Suite

**Project**: BTP - Medical Voice Scribe for Indian Clinical Environments  
**Role**: Senior Speech Data Scientist, Audio ML Researcher & Clinical NLP Specialist  
**Status**: 100% Completed, Verified & Documented  
**Date**: November 2, 2026  

---

## 1. Overview & Directory Index

This directory contains the complete, reproducible, research-grade Exploratory Data Analysis (EDA) suite for our BTP project. It evaluates four benchmark speech and noise datasets located in `voice_scribe_data/`:
1. **PriMock57**: Primary care mock doctor-patient consultations (114 tracks, 17.27 audio hours, dual-channel).
2. **Eka Medical ASR**: Indian medical terminology, drug brand names, and clinical dictations (3,619 English + 320 Hindi records).
3. **Svarah**: Indian-accented English speech benchmark across 19 regional mother tongues (6,656 test records, 9.61 hours).
4. **MS-SNSD**: Microsoft Scalable Noisy Speech Dataset (179 ambient noise soundscapes across 28 categories).

---

## 2. Directory Layout

```
eda/
├── README.md                              # Master navigation & architecture documentation
│
├── reports/                               # Deep-dive analytical research reports
│   ├── dataset_inventory.md               # Phase 1: File counts, sizes, formats, parquet schemas, discrepancy audit
│   ├── primock57_eda.md                   # Phase 2: Dual-track pairing, TextGrid intervals, clinical consultation notes
│   ├── eka_medical_asr_eda.md             # Phase 3: Resolution of 3,619 count, context breakdown, drug entities
│   ├── svarah_eda.md                      # Phase 4: 19 L1 languages, 17 states, general vs. medical vocabulary
│   ├── ms_snsd_eda.md                     # Phase 5: Noise categories, acoustic spectra, SNR/SIR simulation math
│   ├── cross_dataset_comparison.md        # Phase 7: 12-parameter matrix, cross-dataset audio metrics, suitability
│   ├── data_quality_report.md             # Phase 6: Quality audit, imbalances, microphone bleed, critical risks
│   ├── project_recommendations.md         # Phase 8: Answers to 12 core project questions & phased roadmap
│   ├── inventory_summary.json             # Programmatic output from dataset_inventory.py
│   ├── audio_signal_summary.json          # Programmatic output from audio_analysis.py
│   ├── transcript_lexical_summary.json    # Programmatic output from transcript_analysis.py
│   └── data_quality_summary.json          # Programmatic output from data_quality_checks.py
│
├── notebooks/                             # Executable, self-contained Jupyter notebooks
│   ├── 01_primock57_eda.ipynb             # Consultation pairing, TextGrids, dual-channel spectrograms
│   ├── 02_eka_medical_asr_eda.ipynb       # 3,619 record verification, drug entities, dictation context
│   ├── 03_svarah_eda.ipynb                # Indian accent demographics (19 L1s), general English vocabulary
│   ├── 04_ms_snsd_eda.ipynb               # Ambient acoustic noise categorization & OPD distractor spectrograms
│   └── 05_cross_dataset_analysis.ipynb    # Cross-dataset duration & RMS distributions, project alignment
│
├── scripts/                               # Reproducible batch processing & audit scripts
│   ├── dataset_inventory.py               # Complete inventory, file extensions, and parquet schema scanner
│   ├── audio_analysis.py                  # Signal metrics (RMS, peak, silence %, clipping) & plot generator
│   ├── transcript_analysis.py             # Tokenization, TTR, vocabulary counters, and clinical entity parser
│   ├── data_quality_checks.py             # Integrity audit, missing pairs, speaker concentration checker
│   └── generate_notebooks.py              # Automated builder for executable Jupyter notebooks
│
└── figures/                               # Research-grade visualization figures (300 DPI)
    ├── primock57/
    │   ├── primock57_duration_distribution.png
    │   ├── primock57_rms_vs_silence.png
    │   └── primock57_sample_waveform_spectrogram.png
    ├── eka_medical_asr/
    │   ├── eka_duration_by_context.png
    │   ├── eka_rms_energy_distribution.png
    │   └── eka_sample_waveforms_spectrograms.png
    ├── svarah/
    │   ├── svarah_duration_distribution.png
    │   ├── svarah_rms_by_gender.png
    │   └── svarah_accent_waveforms_spectrograms.png
    ├── ms_snsd/
    │   ├── ms_snsd_noise_rms_by_category.png
    │   └── ms_snsd_distractor_spectrograms.png
    └── comparison/
        ├── cross_dataset_duration_comparison.png
        └── cross_dataset_rms_comparison.png
```

---

## 3. How to Run the Analysis Suite

All scripts use relative paths and can be executed from the project root:

```bash
# 1. Run the structural inventory audit
python3 eda/scripts/dataset_inventory.py

# 2. Run signal processing analysis and generate all figures
python3 eda/scripts/audio_analysis.py

# 3. Run transcript lexical and clinical entity extraction
python3 eda/scripts/transcript_analysis.py

# 4. Run data quality and integrity checks
python3 eda/scripts/data_quality_checks.py
```

All 5 notebooks in `eda/notebooks/` can be launched and executed sequentially in JupyterLab or VSCode:
```bash
jupyter lab eda/notebooks/
```
