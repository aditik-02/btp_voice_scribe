# BTP Voice Scribe: Dataset Access & Retrieval Guide

This guide provides official, compliant step-by-step instructions for acquiring and downloading each dataset in the catalog. All commands adhere strictly to official APIs, terms of service, and ethical guidelines. Never hardcode API keys or credentials; always export them as environment variables.

---

## 1. Open Access Datasets (Direct Download)

### 1.1 PriMock57 (`primock57`)
* **Host**: GitHub (Git LFS) & GitHub CDN
* **License**: CC-BY-4.0
* **Prerequisites**: `git-lfs` (`brew install git-lfs` on macOS)
* **Method 1: Git LFS Clone**
  ```bash
  # Ensure git-lfs is initialized
  git lfs install

  # Clone into external storage outside the repo
  mkdir -p /Volumes/ExternalStorage/voice_scribe_data
  cd /Volumes/ExternalStorage/voice_scribe_data
  git clone https://github.com/babylonhealth/primock57.git
  ```
* **Method 2: Direct HTTP Audio Stream / Download**
  Audio files can be downloaded directly from GitHub's media CDN using the pattern:
  ```bash
  # Download consultation 1 (doctor & patient channels)
  curl -L -O https://media.githubusercontent.com/media/babylonhealth/primock57/main/audio/day1_consultation01_doctor.wav
  curl -L -O https://media.githubusercontent.com/media/babylonhealth/primock57/main/audio/day1_consultation01_patient.wav
  ```

---

### 1.2 MeDial-Speech (`medial_speech`)
* **Host**: Hugging Face Hub (`hcuayahu/MeDial-Speech`)
* **License**: CC-BY-NC-4.0
* **Method**: Download via `huggingface_hub` Python API or CLI:
  ```bash
  # Using Hugging Face CLI
  huggingface-cli download hcuayahu/MeDial-Speech --repo-type dataset --local-dir /Volumes/ExternalStorage/voice_scribe_data/medial_speech

  # Or using python
  python3 -c "
  from huggingface_hub import snapshot_download
  snapshot_download('hcuayahu/MeDial-Speech', repo_type='dataset', local_dir='/Volumes/ExternalStorage/voice_scribe_data/medial_speech')
  "
  ```

---

### 1.3 Synth-DoPaCo (`synth_dopaco`)
* **Host**: Hugging Face Hub (`Play-Your-Part/Synth-DoPaCo`)
* **License**: CC-BY-4.0
* **Format**: WebDataset TAR shards (Opus audio + JSON + SOAP notes)
* **Method: WebDataset Python Streaming / Download**
  ```python
  import webdataset as wds
  from huggingface_hub import hf_hub_download

  # Download the 469 MB dev shard
  dev_path = hf_hub_download(
      repo_id="Play-Your-Part/Synth-DoPaCo",
      filename="data/dev-00000.tar",
      repo_type="dataset",
      local_dir="/Volumes/ExternalStorage/voice_scribe_data/synth_dopaco"
  )

  # Read and decode samples
  dataset = wds.WebDataset(dev_path, shardshuffle=False)
  for sample in dataset:
      key = sample["__key__"]
      audio_bytes = sample["opus"]
      transcript = sample["transcript.txt"].decode("utf-8")
      soap_note = sample["soap.txt"].decode("utf-8")
      print(f"Sample {key}: {len(audio_bytes)} bytes audio")
      break
  ```

---

### 1.4 Eka Medical ASR Evaluation Dataset (`eka_medical_asr`)
* **Host**: Hugging Face Hub (`ekacare/eka-medical-asr-evaluation-dataset`)
* **License**: MIT
* **Method: Hugging Face `datasets` Library**
  ```python
  from datasets import load_dataset

  # Stream English clinical test split
  ds_en = load_dataset("ekacare/eka-medical-asr-evaluation-dataset", "en", split="test", streaming=True)
  sample = next(iter(ds_en))
  print("Transcript:", sample["text"])
  print("Medical Entities:", sample["medical_entities"])
  print("Audio sampling rate:", sample["audio"]["sampling_rate"])

  # Stream Hindi clinical test split
  ds_hi = load_dataset("ekacare/eka-medical-asr-evaluation-dataset", "hi", split="test", streaming=True)
  sample_hi = next(iter(ds_hi))
  print("Hindi text:", sample_hi["text"])
  ```

---

### 1.5 Synthetic Medical Dictation (`modulate_synthetic_dictation`)
* **Host**: Hugging Face Hub (`modulate/synthetic-medical-dictation`)
* **License**: CC-BY-4.0
* **Method: Official Export Script**
  ```bash
  # Install dependencies
  pip install datasets soundfile

  # Clone and run official exporter
  python3 -c "
  from datasets import load_dataset
  ds = load_dataset('modulate/synthetic-medical-dictation', split='test')
  print(f'Loaded {len(ds)} test dictations')
  "
  ```

---

### 1.6 AMI Meeting Corpus (`ami_corpus`)
* **Host**: University of Edinburgh Inf
* **License**: CC-BY-4.0
* **Method: Official Download Script / Wget**
  ```bash
  # Download official AMI transcript and audio packages
  wget -r -np -nd -A "*Headset-*.wav" http://groups.inf.ed.ac.uk/ami/AMICorpusMirror/amicorpus/EN2001a/audio/
  ```

---

### 1.7 VoxConverse (`voxconverse`)
* **Host**: University of Oxford VGG & GitHub (`joonson/voxconverse`)
* **License**: CC-BY-4.0
* **Method**:
  ```bash
  # Download development audio zip (~8 GB)
  curl -O https://www.robots.ox.ac.uk/~vgg/data/voxconverse/data/voxconverse_dev_wav.zip

  # Clone RTTM annotations
  git clone https://github.com/joonson/voxconverse.git
  ```

---

### 1.8 OpenSLR Corpora (`openslr_mucs2021`, `openslr_hindi1111`, `librispeech`)
* **Host**: OpenSLR.org
* **Method**:
  ```bash
  # MUCS 2021 Sub-task 2 (SLR104)
  wget https://www.openslr.org/resources/104/mucs2021_subtask2.tar.gz

  # Gram Vaani Hindi 1111h (SLR118)
  wget https://www.openslr.org/resources/118/GramVaani_Hindi_ASR.tar.gz

  # LibriSpeech test-clean (SLR12)
  wget https://www.openslr.org/resources/12/test-clean.tar.gz
  ```

---

## 2. Gated Hugging Face Datasets (Click-Through Terms)

Datasets such as **`ai4bharat/Svarah`**, **`ai4bharat/IndicVoices`**, and **`WhissleAI/speech-simulated-medical-exams`** require an authenticated Hugging Face account and acceptance of their respective terms of use.

### Step-by-Step Gated Access Protocol:
1. Create a free account on [Hugging Face](https://huggingface.co).
2. Generate an Access Token with `read` permissions under **Settings $\rightarrow$ Access Tokens**.
3. Export the token in your local terminal environment:
   ```bash
   export HF_TOKEN="hf_your_personal_token_here"
   ```
4. Navigate to the dataset web page:
   - For Svarah: `https://huggingface.co/datasets/ai4bharat/Svarah`
   - For IndicVoices: `https://huggingface.co/datasets/ai4bharat/IndicVoices`
   - For WhissleAI: `https://huggingface.co/datasets/WhissleAI/speech-simulated-medical-exams`
5. Click **"Agree and access repository"** on the dataset page.
6. Once approved, authenticate via Python:
   ```python
   from huggingface_hub import login
   import os
   login(token=os.environ["HF_TOKEN"])
   ```

---

## 3. Credentialed Health Repositories (PhysioNet)

Datasets like **`physionet_egd_cxr`** (Eye Gaze and Dictation CXR) and **`physionet_b2ai_voice`** contain clinical data that fall under human subject research protocols.

### Step-by-Step PhysioNet Credentialing Protocol:
1. Register an account at [PhysioNet](https://physionet.org/).
2. Complete the required human subjects research ethics training course:
   - Course: **CITI "Data or Specimens Only Research"** or **"Human Research: Biomedical Researchers"**.
   - Training takes approximately 2–4 hours online.
3. Submit your CITI completion certificate to your PhysioNet user profile for verification.
4. Have your institutional affiliation (e.g., University / Department) verified by a faculty mentor or supervisor.
5. On the dataset page (`https://physionet.org/content/egd-cxr/1.0.0/`):
   - Review and digitally sign the **PhysioNet Credentialed Health Data License 1.5.0** (Data Use Agreement).
   - Specify the research purpose ("BTP Voice Scribe: Medical speech recognition benchmarking").
6. Once access is approved by the PhysioNet review board, download using `wfdb` or `wget` with PhysioNet authentication cookies:
   ```bash
   wget --user your_physionet_username --ask-password -r -N -c -np https://physionet.org/files/egd-cxr/1.0.0/
   ```

---

## 4. Gated Academic Consortiums (LDC)

The **Third DIHARD Challenge Clinical ADOS Subset** is distributed via the Linguistic Data Consortium (Catalog ID: `LDC2022S12`).

### Step-by-Step LDC Acquisition Protocol:
1. Check whether your academic institution holds an active **LDC Institutional Membership**.
2. If yes, request access through your university library or language engineering lab administrator.
3. If not an LDC member, non-member academic licenses can be ordered directly from the LDC catalog (`https://catalog.ldc.upenn.edu/LDC2022S12`).
4. Sign the standard LDC User Agreement restricting data to educational and non-commercial speech research.
5. Download via LDC's secure user portal.
