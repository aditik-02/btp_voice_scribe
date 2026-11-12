#!/usr/bin/env python3
"""
Generate the 5 required Jupyter notebooks for the Voice Scribe EDA.
Uses relative paths and executable code cells.
"""

import json
from pathlib import Path

def create_notebook(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source if isinstance(source, list) else source.splitlines(keepends=True)
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source if isinstance(source, list) else source.splitlines(keepends=True)
    }

def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    nb_dir = repo_root / "eda" / "notebooks"
    nb_dir.mkdir(parents=True, exist_ok=True)

    # 1. 01_primock57_eda.ipynb
    nb1_cells = [
        md_cell("# PriMock57 Exploratory Data Analysis\n**Medical Voice Scribe BTP Project**\n\nThis notebook evaluates the **PriMock57** dataset of primary care mock doctor-patient consultations."),
        code_cell("""import os
import json
from pathlib import Path
import soundfile as sf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
base_dir = Path('../../voice_scribe_data/primock57')
audio_dir = base_dir / 'audio'
print("Scanning PriMock57 audio directory:", audio_dir)
wavs = sorted(audio_dir.glob('*.wav'))
print(f"Total audio tracks found: {len(wavs)}")
"""),
        md_cell("## 1. Dual-Channel Doctor & Patient Consultation Pairing\nInvestigating duration synchronization between doctor and patient tracks."),
        code_cell("""consultations = {}
for w in wavs:
    name = w.stem
    if name.endswith('_doctor'):
        cid = name[:-7]
        consultations.setdefault(cid, {})['doctor'] = w
    elif name.endswith('_patient'):
        cid = name[:-8]
        consultations.setdefault(cid, {})['patient'] = w

print(f"Total paired consultations: {len(consultations)}")

durations = []
for cid, tracks in consultations.items():
    if 'doctor' in tracks and 'patient' in tracks:
        d_dur = sf.info(tracks['doctor']).duration
        p_dur = sf.info(tracks['patient']).duration
        durations.append({'cid': cid, 'doc_dur': d_dur, 'pat_dur': p_dur, 'diff': abs(d_dur - p_dur)})

df_dur = pd.DataFrame(durations)
print(df_dur[['doc_dur', 'pat_dur', 'diff']].describe())
"""),
        md_cell("## 2. TextGrid Alignment & Utterance Distribution"),
        code_cell("""from collections import Counter
tg_dir = base_dir / 'transcripts'
tgs = sorted(tg_dir.glob('*.TextGrid'))
print(f"Total TextGrid alignment files: {len(tgs)}")

# Display sample lines from the first TextGrid
sample_tg = tgs[0].read_text(errors='ignore').splitlines()
print("\\n".join(sample_tg[:20]))
"""),
        md_cell("## 3. Audio & Spectrogram Visualization"),
        code_cell("""fig_path = Path('../figures/primock57/primock57_sample_waveform_spectrogram.png')
if fig_path.exists():
    from IPython.display import Image, display
    display(Image(filename=str(fig_path)))
""")
    ]
    with open(nb_dir / "01_primock57_eda.ipynb", "w") as f:
        json.dump(create_notebook(nb1_cells), f, indent=2)

    # 2. 02_eka_medical_asr_eda.ipynb
    nb2_cells = [
        md_cell("# Eka Medical ASR Exploratory Data Analysis\n**Medical Voice Scribe BTP Project**\n\nThis notebook evaluates the **Eka Medical ASR** benchmark dataset."),
        code_cell("""import io
import json
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
base_dir = Path('../../voice_scribe_data/eka_medical_asr')
en_parquets = sorted((base_dir / 'en').glob('*.parquet'))
hi_parquets = sorted((base_dir / 'hi').glob('*.parquet'))

print(f"English parquet shards: {len(en_parquets)}")
print(f"Hindi parquet shards: {len(hi_parquets)}")
"""),
        md_cell("## 1. Verified Record Counts & Discrepancy Resolution\nChecking exact row counts across all shards to verify the 3,619 English records."),
        code_cell("""en_counts = [pq.read_table(p).num_rows for p in en_parquets]
hi_counts = [pq.read_table(p).num_rows for p in hi_parquets]
print(f"Verified English records: {sum(en_counts)} (Shards: {en_counts})")
print(f"Verified Hindi records: {sum(hi_counts)} (Shards: {hi_counts})")
assert sum(en_counts) == 3619, "Discrepancy: English count does not match 3,619!"
print("Assertion Passed: Exactly 3,619 English evaluation records confirmed.")
"""),
        md_cell("## 2. Recording Context & Medical Vocabulary Analysis"),
        code_cell("""df_list = [pq.read_table(p, columns=['type_concept', 'recording_context', 'duration', 'medical_entities']).to_pandas() for p in en_parquets]
df_en = pd.concat(df_list, ignore_index=True)

print("Recording context breakdown:")
print(df_en['recording_context'].value_counts())

print("\\nType concept breakdown:")
print(df_en['type_concept'].value_counts())
"""),
        md_cell("## 3. Visualization Display"),
        code_cell("""fig_path = Path('../figures/eka_medical_asr/eka_sample_waveforms_spectrograms.png')
if fig_path.exists():
    from IPython.display import Image, display
    display(Image(filename=str(fig_path)))
""")
    ]
    with open(nb_dir / "02_eka_medical_asr_eda.ipynb", "w") as f:
        json.dump(create_notebook(nb2_cells), f, indent=2)

    # 3. 03_svarah_eda.ipynb
    nb3_cells = [
        md_cell("# Svarah Indic Accented English Speech EDA\n**Medical Voice Scribe BTP Project**\n\nThis notebook analyzes the **Svarah** benchmark dataset containing 6,656 Indian English test utterances across 19 native language backgrounds."),
        code_cell("""from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style='whitegrid')
base_dir = Path('../../voice_scribe_data/svarah/data')
parquets = sorted(base_dir.glob('*.parquet'))
print(f"Found {len(parquets)} Svarah parquet shards:")

tables = [pq.read_table(p, columns=['duration', 'gender', 'age-group', 'primary_language', 'native_place_state']) for p in parquets]
df_sva = pd.concat([t.to_pandas() for t in tables], ignore_index=True)
print(f"Total verified Svarah records: {len(df_sva):,}")
assert len(df_sva) == 6656, "Expected exactly 6,656 records!"
"""),
        md_cell("## 1. Demographic & Accent Distribution"),
        code_cell("""print("Gender distribution:")
print(df_sva['gender'].value_counts(normalize=True) * 100)

print("\\nAge-group distribution:")
print(df_sva['age-group'].value_counts(normalize=True) * 100)

print(f"\\nPrimary native language backgrounds ({df_sva['primary_language'].nunique()} languages):")
print(df_sva['primary_language'].value_counts().head(10))
"""),
        md_cell("## 2. Duration Statistics & Figures"),
        code_cell("""print("Duration statistics (seconds):")
print(df_sva['duration'].describe())

fig_path = Path('../figures/svarah/svarah_duration_distribution.png')
if fig_path.exists():
    from IPython.display import Image, display
    display(Image(filename=str(fig_path)))
""")
    ]
    with open(nb_dir / "03_svarah_eda.ipynb", "w") as f:
        json.dump(create_notebook(nb3_cells), f, indent=2)

    # 4. 04_ms_snsd_eda.ipynb
    nb4_cells = [
        md_cell("# MS-SNSD Noise & Speech Corpus EDA\n**Medical Voice Scribe BTP Project**\n\nThis notebook analyzes background noise and speech characteristics in the **MS-SNSD** dataset."),
        code_cell("""from pathlib import Path
import soundfile as sf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

base_dir = Path('../../voice_scribe_data/ms_snsd')
noise_train = sorted((base_dir / 'noise_train').glob('*.wav'))
noise_test = sorted((base_dir / 'noise_test').glob('*.wav'))
clean_test = sorted((base_dir / 'clean_test').glob('*.wav'))

print(f"Noise train files: {len(noise_train)}")
print(f"Noise test files: {len(noise_test)}")
print(f"Clean test files: {len(clean_test)}")
"""),
        md_cell("## 1. Ambient Acoustic Noise Classification"),
        code_cell("""from collections import Counter
cats_train = Counter(w.stem.split('_')[0] if '_' in w.stem else w.stem for w in noise_train)
cats_test = Counter(w.stem.split('_')[0] if '_' in w.stem else w.stem for w in noise_test)

print("Top noise categories in training split:")
for cat, count in cats_train.most_common(12):
    print(f"  {cat}: {count} files")
"""),
        md_cell("## 2. Visualizing Clinical Distractors (Babble, AC, Typing)"),
        code_cell("""fig_path = Path('../figures/ms_snsd/ms_snsd_distractor_spectrograms.png')
if fig_path.exists():
    from IPython.display import Image, display
    display(Image(filename=str(fig_path)))
""")
    ]
    with open(nb_dir / "04_ms_snsd_eda.ipynb", "w") as f:
        json.dump(create_notebook(nb4_cells), f, indent=2)

    # 5. 05_cross_dataset_analysis.ipynb
    nb5_cells = [
        md_cell("# Cross-Dataset Comparison & Project Alignment\n**Medical Voice Scribe BTP Project**\n\nComparative analysis across PriMock57, Eka Medical ASR, Svarah, and MS-SNSD."),
        code_cell("""import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Markdown

reports_dir = Path('../reports')
with open(reports_dir / 'audio_signal_summary.json') as f:
    audio_summary = json.load(f)

with open(reports_dir / 'transcript_lexical_summary.json') as f:
    lex_summary = json.load(f)

print("Audio signal summary keys:", list(audio_summary.keys()))
print("Lexical summary keys:", list(lex_summary.keys()))
"""),
        md_cell("## 1. Cross-Dataset Comparison Matrix"),
        code_cell("""comp_matrix = [
    {"Dataset": "PriMock57", "Type": "Mock Consultation", "Speech Style": "Conversational (2-speaker)", "Clinical Relevance": "High (UK GP)", "Accent": "British English", "Total Audio": "17.27 h (dual-ch)", "Role Labels": "Yes (Doctor/Patient)"},
    {"Dataset": "Eka Medical", "Type": "Clinical Terms & Dictations", "Speech Style": "Single terms & dictations", "Clinical Relevance": "High (Indian Pharma)", "Accent": "Indian English", "Total Audio": "~8.5 h", "Role Labels": "No (Clinician dictation)"},
    {"Dataset": "Svarah", "Type": "Accented Speech Benchmark", "Speech Style": "Read / Spontaneous", "Clinical Relevance": "Zero (General)", "Accent": "Indian English (19 langs)", "Total Audio": "9.61 h", "Role Labels": "No (Single speaker)"},
    {"Dataset": "MS-SNSD", "Type": "Acoustic Noise Corpus", "Speech Style": "Ambient soundscapes", "Clinical Relevance": "High (Noise simulation)", "Accent": "N/A (Noise)", "Total Audio": "3.95 h noise", "Role Labels": "N/A"}
]
df_comp = pd.DataFrame(comp_matrix)
display(df_comp)
"""),
        md_cell("## 2. Visual Comparison"),
        code_cell("""fig1 = Path('../figures/comparison/cross_dataset_duration_comparison.png')
fig2 = Path('../figures/comparison/cross_dataset_rms_comparison.png')
from IPython.display import Image, display
if fig1.exists():
    display(Image(filename=str(fig1)))
if fig2.exists():
    display(Image(filename=str(fig2)))
""")
    ]
    with open(nb_dir / "05_cross_dataset_analysis.ipynb", "w") as f:
        json.dump(create_notebook(nb5_cells), f, indent=2)

    print("Successfully generated all 5 Jupyter notebooks in eda/notebooks/!")

if __name__ == "__main__":
    main()
