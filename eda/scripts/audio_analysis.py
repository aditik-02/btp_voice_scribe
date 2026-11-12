#!/usr/bin/env python3
"""
eda/scripts/audio_analysis.py
Phase 2: Audio Signal Analysis for Medical Voice Scribe BTP.
Analyzes PriMock57, Eka Medical ASR, Svarah, and MS-SNSD.
Computes duration stats, RMS energy, peak amplitude, clipping, silence percentage,
and generates research-quality figures (histograms, waveforms, spectrograms).
"""

import os
import sys
import io
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import matplotlib.pyplot as plt
import seaborn as sns
import pyarrow.parquet as pq

# Set style
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, DejaVu Sans'
plt.rcParams['figure.autolayout'] = True
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

def compute_audio_metrics(audio: np.ndarray, sr: int):
    """Computes peak amplitude, RMS (dBFS), clipping %, and silence %."""
    if len(audio) == 0:
        return 0.0, -100.0, 0.0, 100.0

    # Ensure float32 in [-1, 1]
    if audio.dtype != np.float32 and audio.dtype != np.float64:
        audio = audio.astype(np.float32) / 32768.0

    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio**2)))
    rms_db = 20 * np.log10(rms) if rms > 1e-7 else -100.0

    # Clipping: samples within 0.001 of 1.0
    clipping_pct = float(np.mean(np.abs(audio) >= 0.999) * 100)

    # Silence percentage: frame-based with 25ms frames, 10ms hop
    frame_length = int(0.025 * sr)
    hop_length = int(0.010 * sr)
    if len(audio) > frame_length:
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
        frame_rms = np.sqrt(np.mean(frames**2, axis=0))
        # Threshold: -40 dB relative to full scale or 10% of peak RMS
        silence_thresh = max(1e-4, 0.05 * np.max(frame_rms) if len(frame_rms) > 0 else 1e-4)
        silence_pct = float(np.mean(frame_rms < silence_thresh) * 100)
    else:
        silence_pct = 100.0 if rms < 1e-4 else 0.0

    return peak, rms_db, clipping_pct, silence_pct

def analyze_primock57(base_dir: Path, fig_dir: Path):
    print(">>> Analyzing PriMock57 Audio...")
    audio_dir = base_dir / "primock57" / "audio"
    wav_files = sorted(audio_dir.glob("*.wav"))

    records = []
    for w in wav_files:
        info = sf.info(w)
        audio, sr = sf.read(w)
        peak, rms_db, clip_pct, sil_pct = compute_audio_metrics(audio, sr)
        role = "Doctor" if w.stem.endswith("_doctor") else "Patient"
        consult_id = w.stem.rsplit("_", 1)[0]
        records.append({
            "file": w.name,
            "consultation_id": consult_id,
            "role": role,
            "duration": info.duration,
            "sr": info.samplerate,
            "channels": info.channels,
            "subtype": info.subtype,
            "peak_amp": peak,
            "rms_dbfs": rms_db,
            "clipping_pct": clip_pct,
            "silence_pct": sil_pct
        })

    df = pd.DataFrame(records)

    # Visualizations
    # 1. Duration Histogram by Role
    plt.figure(figsize=(9, 5))
    sns.histplot(data=df, x="duration", hue="role", bins=15, kde=True, palette={"Doctor": "#1f77b4", "Patient": "#ff7f0e"})
    plt.title("PriMock57: Consultation Channel Audio Duration by Speaker Role", fontsize=13, fontweight='bold')
    plt.xlabel("Duration (seconds)", fontsize=11)
    plt.ylabel("Number of Recordings", fontsize=11)
    plt.savefig(fig_dir / "primock57_duration_distribution.png", dpi=300)
    plt.close()

    # 2. Silence Percentage vs RMS
    plt.figure(figsize=(9, 5))
    sns.scatterplot(data=df, x="rms_dbfs", y="silence_pct", hue="role", style="role", s=80, alpha=0.85, palette={"Doctor": "#1f77b4", "Patient": "#ff7f0e"})
    plt.title("PriMock57: Channel Inactivity (Silence %) vs. Overall RMS Energy", fontsize=13, fontweight='bold')
    plt.xlabel("RMS Energy (dBFS)", fontsize=11)
    plt.ylabel("Silence Percentage (%)", fontsize=11)
    plt.savefig(fig_dir / "primock57_rms_vs_silence.png", dpi=300)
    plt.close()

    # 3. Waveform & Spectrogram of Consultation 1 (Doctor vs Patient)
    w_doc = audio_dir / "day1_consultation01_doctor.wav"
    w_pat = audio_dir / "day1_consultation01_patient.wav"
    a_doc, sr_doc = sf.read(w_doc)
    a_pat, sr_pat = sf.read(w_pat)

    # 30-second window (seconds 10 to 40)
    t_start, t_end = 10, 40
    idx_s, idx_e = int(t_start * sr_doc), int(t_end * sr_doc)
    clip_doc = a_doc[idx_s:idx_e]
    clip_pat = a_pat[idx_s:idx_e]
    time_axis = np.linspace(t_start, t_end, len(clip_doc))

    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    # Waveform Doc
    axes[0].plot(time_axis, clip_doc, color='#1f77b4', lw=0.8)
    axes[0].set_title("Day 1 Consult 01: Doctor Track Waveform (t = 10s to 40s)", fontsize=11, fontweight='bold')
    axes[0].set_ylabel("Amplitude")
    axes[0].set_ylim([-0.6, 0.6])

    # Waveform Pat
    axes[1].plot(time_axis, clip_pat, color='#ff7f0e', lw=0.8)
    axes[1].set_title("Day 1 Consult 01: Patient Track Waveform (t = 10s to 40s)", fontsize=11, fontweight='bold')
    axes[1].set_ylabel("Amplitude")
    axes[1].set_ylim([-0.6, 0.6])

    # Spectrogram Doc
    S_doc = librosa.amplitude_to_db(np.abs(librosa.stft(clip_doc)), ref=np.max)
    img1 = librosa.display.specshow(S_doc, sr=sr_doc, hop_length=512, x_axis='time', y_axis='log', ax=axes[2], cmap='viridis')
    axes[2].set_title("Doctor Track Log-Frequency Spectrogram", fontsize=11, fontweight='bold')
    axes[2].set_ylabel("Freq (Hz)")
    fig.colorbar(img1, ax=axes[2], format="%+2.0f dB")

    # Spectrogram Pat
    S_pat = librosa.amplitude_to_db(np.abs(librosa.stft(clip_pat)), ref=np.max)
    img2 = librosa.display.specshow(S_pat, sr=sr_pat, hop_length=512, x_axis='time', y_axis='log', ax=axes[3], cmap='magma')
    axes[3].set_title("Patient Track Log-Frequency Spectrogram (Notice alternating turn-taking)", fontsize=11, fontweight='bold')
    axes[3].set_ylabel("Freq (Hz)")
    axes[3].set_xlabel("Time (seconds)")
    fig.colorbar(img2, ax=axes[3], format="%+2.0f dB")

    plt.savefig(fig_dir / "primock57_sample_waveform_spectrogram.png", dpi=300)
    plt.close()

    return df

def analyze_eka_medical(base_dir: Path, fig_dir: Path):
    print(">>> Analyzing Eka Medical ASR Audio...")
    parquet_files = sorted((base_dir / "eka_medical_asr" / "en").glob("*.parquet"))

    records = []
    # Sample 300 rows across parquets for deep signal calculation (peak, RMS, silence)
    sample_clips_for_plotting = {}
    
    total_rows = 0
    for pf in parquet_files:
        table = pq.read_table(pf)
        total_rows += table.num_rows
        df_p = table.to_pandas()
        
        # Take a systematic sample (e.g., every 12th row)
        sample_indices = range(0, len(df_p), 12)
        for idx in sample_indices:
            row = df_p.iloc[idx]
            duration = float(row["duration"])
            rec_context = str(row["recording_context"])
            concept = str(row["type_concept"])
            
            # Read audio bytes
            audio_raw = row["audio"]
            audio_bytes = audio_raw["bytes"] if isinstance(audio_raw, dict) and "bytes" in audio_raw else audio_raw
            if audio_bytes and isinstance(audio_bytes, (bytes, bytearray)):
                with io.BytesIO(audio_bytes) as bio:
                    audio, sr = sf.read(bio)
                    peak, rms_db, clip_pct, sil_pct = compute_audio_metrics(audio, sr)
                    records.append({
                        "file_name": row["file_name"],
                        "duration": duration,
                        "recording_context": rec_context,
                        "type_concept": concept,
                        "sr": sr,
                        "peak_amp": peak,
                        "rms_dbfs": rms_db,
                        "clipping_pct": clip_pct,
                        "silence_pct": sil_pct
                    })
                    if rec_context not in sample_clips_for_plotting:
                        sample_clips_for_plotting[rec_context] = (audio, sr, row["text"], concept)

    df_sample = pd.DataFrame(records)

    # 1. Duration by Recording Context
    plt.figure(figsize=(9, 5))
    sns.boxplot(data=df_sample, x="recording_context", y="duration", palette="Set2")
    plt.title("Eka Medical ASR: Clip Duration by Recording Context", fontsize=13, fontweight='bold')
    plt.xlabel("Recording Context", fontsize=11)
    plt.ylabel("Duration (seconds)", fontsize=11)
    plt.savefig(fig_dir / "eka_duration_by_context.png", dpi=300)
    plt.close()

    # 2. RMS Energy distribution
    plt.figure(figsize=(9, 5))
    sns.histplot(data=df_sample, x="rms_dbfs", hue="recording_context", bins=20, kde=True, palette="tab10")
    plt.title("Eka Medical ASR: Signal Energy (RMS dBFS) Distribution", fontsize=13, fontweight='bold')
    plt.xlabel("RMS Energy (dBFS)", fontsize=11)
    plt.ylabel("Number of Clips", fontsize=11)
    plt.savefig(fig_dir / "eka_rms_energy_distribution.png", dpi=300)
    plt.close()

    # 3. Waveform & Spectrogram of Entity vs Sentence
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    ctx_keys = ["narration_entity", "narration_sentence"]
    for col_idx, ctx in enumerate(ctx_keys):
        if ctx in sample_clips_for_plotting:
            audio, sr, txt, cpt = sample_clips_for_plotting[ctx]
            t_axis = np.linspace(0, len(audio) / sr, len(audio))
            # Waveform
            axes[0, col_idx].plot(t_axis, audio, color="#2ca02c" if col_idx == 0 else "#1f77b4", lw=0.9)
            axes[0, col_idx].set_title(f"Context: {ctx}\nText: \"{txt[:40]}...\" ({cpt})", fontsize=10, fontweight='bold')
            axes[0, col_idx].set_ylabel("Amplitude")
            axes[0, col_idx].set_xlabel("Time (s)")
            axes[0, col_idx].set_ylim([-1.0, 1.0])

            # Spectrogram
            S = librosa.amplitude_to_db(np.abs(librosa.stft(audio.astype(np.float32))), ref=np.max)
            img = librosa.display.specshow(S, sr=sr, hop_length=512, x_axis='time', y_axis='log', ax=axes[1, col_idx], cmap='viridis')
            axes[1, col_idx].set_title(f"Log Spectrogram ({ctx})", fontsize=10, fontweight='bold')
            axes[1, col_idx].set_ylabel("Freq (Hz)")
            axes[1, col_idx].set_xlabel("Time (s)")
            fig.colorbar(img, ax=axes[1, col_idx], format="%+2.0f dB")

    plt.tight_layout()
    plt.savefig(fig_dir / "eka_sample_waveforms_spectrograms.png", dpi=300)
    plt.close()

    return df_sample

def analyze_svarah(base_dir: Path, fig_dir: Path):
    print(">>> Analyzing Svarah Audio...")
    parquet_files = sorted((base_dir / "svarah" / "data").glob("*.parquet"))

    records = []
    sample_clips_by_lang = {}
    
    for pf in parquet_files:
        table = pq.read_table(pf)
        df_p = table.to_pandas()
        
        # Sample every 20th row across 6,656 records (~330 clips)
        sample_indices = range(0, len(df_p), 20)
        for idx in sample_indices:
            row = df_p.iloc[idx]
            duration = float(row["duration"])
            lang = str(row["primary_language"])
            gender = str(row["gender"])
            state = str(row["native_place_state"])
            
            audio_raw = row["audio_filepath"]
            audio_bytes = audio_raw["bytes"] if isinstance(audio_raw, dict) and "bytes" in audio_raw else audio_raw
            if audio_bytes and isinstance(audio_bytes, (bytes, bytearray)):
                with io.BytesIO(audio_bytes) as bio:
                    audio, sr = sf.read(bio)
                    peak, rms_db, clip_pct, sil_pct = compute_audio_metrics(audio, sr)
                    records.append({
                        "duration": duration,
                        "primary_language": lang,
                        "gender": gender,
                        "native_place_state": state,
                        "sr": sr,
                        "peak_amp": peak,
                        "rms_dbfs": rms_db,
                        "clipping_pct": clip_pct,
                        "silence_pct": sil_pct
                    })
                    if lang not in sample_clips_by_lang and len(sample_clips_by_lang) < 4:
                        sample_clips_by_lang[lang] = (audio, sr, row["text"], state)

    df_sample = pd.DataFrame(records)

    # 1. Duration Distribution (All 6,656 records from metadata)
    all_durations = []
    for pf in parquet_files:
        t = pq.read_table(pf, columns=["duration"])
        all_durations.extend(t["duration"].to_pylist())
    
    plt.figure(figsize=(9, 5))
    sns.histplot(all_durations, bins=30, kde=True, color="#9467bd")
    plt.title("Svarah: Complete Test Split Audio Duration Distribution (N = 6,656)", fontsize=13, fontweight='bold')
    plt.xlabel("Duration (seconds)", fontsize=11)
    plt.ylabel("Number of Clips", fontsize=11)
    plt.savefig(fig_dir / "svarah_duration_distribution.png", dpi=300)
    plt.close()

    # 2. RMS Energy by Gender
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df_sample, x="gender", y="rms_dbfs", palette={"Female": "#e377c2", "Male": "#1f77b4"})
    plt.title("Svarah: Audio Signal Level (RMS dBFS) by Speaker Gender", fontsize=13, fontweight='bold')
    plt.xlabel("Speaker Gender", fontsize=11)
    plt.ylabel("RMS Energy (dBFS)", fontsize=11)
    plt.savefig(fig_dir / "svarah_rms_by_gender.png", dpi=300)
    plt.close()

    # 3. Waveform and Spectrogram of Indian Accent Samples
    fig, axes = plt.subplots(len(sample_clips_by_lang), 2, figsize=(14, 3 * len(sample_clips_by_lang)))
    for idx, (lang, (audio, sr, txt, state)) in enumerate(sample_clips_by_lang.items()):
        t_axis = np.linspace(0, len(audio)/sr, len(audio))
        axes[idx, 0].plot(t_axis, audio, color="#8c564b", lw=0.8)
        axes[idx, 0].set_title(f"Language: {lang} ({state}) | Text: \"{txt[:35]}...\"", fontsize=10, fontweight='bold')
        axes[idx, 0].set_ylabel("Amplitude")
        axes[idx, 0].set_ylim([-0.8, 0.8])
        if idx == len(sample_clips_by_lang) - 1:
            axes[idx, 0].set_xlabel("Time (s)")

        S = librosa.amplitude_to_db(np.abs(librosa.stft(audio.astype(np.float32))), ref=np.max)
        img = librosa.display.specshow(S, sr=sr, hop_length=512, x_axis='time', y_axis='log', ax=axes[idx, 1], cmap='plasma')
        axes[idx, 1].set_title(f"Log Spectrogram ({lang})", fontsize=10, fontweight='bold')
        axes[idx, 1].set_ylabel("Freq (Hz)")
        fig.colorbar(img, ax=axes[idx, 1], format="%+2.0f dB")
        if idx == len(sample_clips_by_lang) - 1:
            axes[idx, 1].set_xlabel("Time (s)")

    plt.tight_layout()
    plt.savefig(fig_dir / "svarah_accent_waveforms_spectrograms.png", dpi=300)
    plt.close()

    return df_sample

def analyze_ms_snsd(base_dir: Path, fig_dir: Path):
    print(">>> Analyzing MS-SNSD Noise & Speech Audio...")
    snsd_dir = base_dir / "ms_snsd"
    noise_files = sorted((snsd_dir / "noise_train").glob("*.wav")) + sorted((snsd_dir / "noise_test").glob("*.wav"))
    
    records = []
    # Analyze all 179 noise files
    sample_noises = {}
    key_categories = ["AirConditioner", "Babble", "Traffic", "Typing", "NeighborSpeaking", "VacuumCleaner"]
    
    for nf in noise_files:
        info = sf.info(nf)
        audio, sr = sf.read(nf)
        peak, rms_db, clip_pct, sil_pct = compute_audio_metrics(audio, sr)
        cat = nf.stem.split("_")[0] if "_" in nf.stem else nf.stem
        records.append({
            "file": nf.name,
            "category": cat,
            "split": "test" if "noise_test" in str(nf) else "train",
            "duration": info.duration,
            "sr": info.samplerate,
            "peak_amp": peak,
            "rms_dbfs": rms_db,
            "clipping_pct": clip_pct,
            "silence_pct": sil_pct
        })
        if cat in key_categories and cat not in sample_noises:
            sample_noises[cat] = (audio, sr, info.duration)

    df_noise = pd.DataFrame(records)

    # 1. Noise Duration & RMS by Category (Top 10)
    top_cats = df_noise["category"].value_counts().head(10).index
    df_top = df_noise[df_noise["category"].isin(top_cats)]

    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df_top, x="category", y="rms_dbfs", palette="tab10")
    plt.xticks(rotation=35, ha='right')
    plt.title("MS-SNSD: Noise Soundscape RMS Energy by Ambient Category", fontsize=13, fontweight='bold')
    plt.xlabel("Noise Category", fontsize=11)
    plt.ylabel("RMS Energy (dBFS)", fontsize=11)
    plt.savefig(fig_dir / "ms_snsd_noise_rms_by_category.png", dpi=300)
    plt.close()

    # 2. Spectrograms of Key Clinical Acoustic Distractors (Babble, AC, Traffic, Typing)
    fig, axes = plt.subplots(4, 1, figsize=(12, 11), sharex=True)
    distractors = ["Babble", "AirConditioner", "Typing", "NeighborSpeaking"]
    for idx, d_name in enumerate(distractors):
        if d_name in sample_noises:
            audio, sr, dur = sample_noises[d_name]
            # Take 5-second slice
            slice_audio = audio[:int(5.0 * sr)].astype(np.float32)
            S = librosa.amplitude_to_db(np.abs(librosa.stft(slice_audio)), ref=np.max)
            img = librosa.display.specshow(S, sr=sr, hop_length=512, x_axis='time', y_axis='log', ax=axes[idx], cmap='inferno')
            axes[idx].set_title(f"Clinical Distractor: {d_name} (5-second snapshot, 16 kHz)", fontsize=11, fontweight='bold')
            axes[idx].set_ylabel("Freq (Hz)")
            fig.colorbar(img, ax=axes[idx], format="%+2.0f dB")
            if idx == 3:
                axes[idx].set_xlabel("Time (s)")

    plt.savefig(fig_dir / "ms_snsd_distractor_spectrograms.png", dpi=300)
    plt.close()

    return df_noise

def generate_comparison_plots(primock_df, eka_df, svarah_df, snsd_df, fig_dir: Path):
    print(">>> Generating Cross-Dataset Comparative Visualizations...")
    
    # 1. Duration comparison across datasets
    plt.figure(figsize=(10, 6))
    data_durs = [
        pd.DataFrame({"Dataset": "PriMock57 (Consultations)", "Duration (s)": primock_df["duration"]}),
        pd.DataFrame({"Dataset": "Eka Medical (Dictations)", "Duration (s)": eka_df["duration"]}),
        pd.DataFrame({"Dataset": "Svarah (Accented Speech)", "Duration (s)": svarah_df["duration"]}),
        pd.DataFrame({"Dataset": "MS-SNSD (Noise Audio)", "Duration (s)": snsd_df["duration"]})
    ]
    comb_df = pd.concat(data_durs, ignore_index=True)
    
    ax = sns.boxplot(data=comb_df, x="Dataset", y="Duration (s)", palette="Set3", showfliers=False)
    plt.title("Cross-Dataset Audio Duration Comparison (Without Outliers)", fontsize=13, fontweight='bold')
    plt.xlabel("Benchmark Dataset", fontsize=11)
    plt.ylabel("Audio Duration (seconds)", fontsize=11)
    plt.savefig(fig_dir / "cross_dataset_duration_comparison.png", dpi=300)
    plt.close()

    # 2. RMS Energy Levels (dBFS) Comparison
    plt.figure(figsize=(10, 6))
    data_rms = [
        pd.DataFrame({"Dataset": "PriMock57", "RMS (dBFS)": primock_df["rms_dbfs"]}),
        pd.DataFrame({"Dataset": "Eka Medical", "RMS (dBFS)": eka_df["rms_dbfs"]}),
        pd.DataFrame({"Dataset": "Svarah", "RMS (dBFS)": svarah_df["rms_dbfs"]}),
        pd.DataFrame({"Dataset": "MS-SNSD Noise", "RMS (dBFS)": snsd_df["rms_dbfs"]})
    ]
    comb_rms = pd.concat(data_rms, ignore_index=True)
    sns.violinplot(data=comb_rms, x="Dataset", y="RMS (dBFS)", palette="Pastel1", inner="quartile")
    plt.title("Cross-Dataset Audio Signal Energy (RMS dBFS) Distribution", fontsize=13, fontweight='bold')
    plt.xlabel("Benchmark Dataset", fontsize=11)
    plt.ylabel("RMS Energy (dBFS)", fontsize=11)
    plt.savefig(fig_dir / "cross_dataset_rms_comparison.png", dpi=300)
    plt.close()

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    base_data = repo_root / "voice_scribe_data"
    fig_root = repo_root / "eda" / "figures"
    reports_root = repo_root / "eda" / "reports"

    df_pri = analyze_primock57(base_data, fig_root / "primock57")
    df_eka = analyze_eka_medical(base_data, fig_root / "eka_medical_asr")
    df_sva = analyze_svarah(base_data, fig_root / "svarah")
    df_snsd = analyze_ms_snsd(base_data, fig_root / "ms_snsd")

    generate_comparison_plots(df_pri, df_eka, df_sva, df_snsd, fig_root / "comparison")

    # Save summary statistics JSON
    summary_stats = {
        "primock57": {
            "count": len(df_pri),
            "duration": {
                "min": float(df_pri["duration"].min()),
                "max": float(df_pri["duration"].max()),
                "mean": float(df_pri["duration"].mean()),
                "median": float(df_pri["duration"].median()),
                "std": float(df_pri["duration"].std()),
                "total_hours": float(df_pri["duration"].sum() / 3600)
            },
            "rms_dbfs": {
                "mean": float(df_pri["rms_dbfs"].mean()),
                "median": float(df_pri["rms_dbfs"].median()),
                "std": float(df_pri["rms_dbfs"].std())
            },
            "silence_pct": {
                "mean": float(df_pri["silence_pct"].mean()),
                "median": float(df_pri["silence_pct"].median())
            },
            "clipping_pct_mean": float(df_pri["clipping_pct"].mean())
        },
        "eka_medical_asr": {
            "sample_analyzed": len(df_eka),
            "duration": {
                "min": float(df_eka["duration"].min()),
                "max": float(df_eka["duration"].max()),
                "mean": float(df_eka["duration"].mean()),
                "median": float(df_eka["duration"].median()),
                "std": float(df_eka["duration"].std())
            },
            "rms_dbfs": {
                "mean": float(df_eka["rms_dbfs"].mean()),
                "median": float(df_eka["rms_dbfs"].median()),
                "std": float(df_eka["rms_dbfs"].std())
            },
            "silence_pct": {
                "mean": float(df_eka["silence_pct"].mean()),
                "median": float(df_eka["silence_pct"].median())
            },
            "clipping_pct_mean": float(df_eka["clipping_pct"].mean())
        },
        "svarah": {
            "sample_analyzed": len(df_sva),
            "duration": {
                "min": float(df_sva["duration"].min()),
                "max": float(df_sva["duration"].max()),
                "mean": float(df_sva["duration"].mean()),
                "median": float(df_sva["duration"].median()),
                "std": float(df_sva["duration"].std())
            },
            "rms_dbfs": {
                "mean": float(df_sva["rms_dbfs"].mean()),
                "median": float(df_sva["rms_dbfs"].median()),
                "std": float(df_sva["rms_dbfs"].std())
            },
            "silence_pct": {
                "mean": float(df_sva["silence_pct"].mean()),
                "median": float(df_sva["silence_pct"].median())
            },
            "clipping_pct_mean": float(df_sva["clipping_pct"].mean())
        },
        "ms_snsd_noise": {
            "count": len(df_snsd),
            "duration": {
                "min": float(df_snsd["duration"].min()),
                "max": float(df_snsd["duration"].max()),
                "mean": float(df_snsd["duration"].mean()),
                "median": float(df_snsd["duration"].median()),
                "std": float(df_snsd["duration"].std()),
                "total_hours": float(df_snsd["duration"].sum() / 3600)
            },
            "rms_dbfs": {
                "mean": float(df_snsd["rms_dbfs"].mean()),
                "median": float(df_snsd["rms_dbfs"].median()),
                "std": float(df_snsd["rms_dbfs"].std())
            },
            "silence_pct": {
                "mean": float(df_snsd["silence_pct"].mean()),
                "median": float(df_snsd["silence_pct"].median())
            },
            "clipping_pct_mean": float(df_snsd["clipping_pct"].mean())
        }
    }

    with open(reports_root / "audio_signal_summary.json", "w") as f:
        json.dump(summary_stats, f, indent=2)

    print("\nAudio Signal Analysis Complete! Summary saved to eda/reports/audio_signal_summary.json")

if __name__ == "__main__":
    main()
