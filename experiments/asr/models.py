"""ASR model adapters. Every adapter exposes  transcribe(audio: np.ndarray 16 kHz mono) -> str.

Imports are lazy, so each model only needs its own packages (see requirements/).
Loading code follows each model's official card as of Nov 2026; confirm on the first smoke run
(`run_asr.py --model <name> --limit 3`) because these libraries change often.
"""
import os
import tempfile
import numpy as np
import soundfile as sf

from audio import SR, split_long

# language codes used on the command line -> each model's own convention
LANG_NAMES = {"en": "English", "hi": "Hindi", "kn": "Kannada"}


class ASRModel:
    name = "base"
    max_chunk_s = None          # if set, longer audio is split with audio.split_long before decoding
    languages = {"en", "hi", "kn"}

    def __init__(self, language="en", device="cuda:0"):
        if language not in self.languages:
            raise ValueError(f"{self.name} does not support language '{language}' (supports {sorted(self.languages)})")
        self.language, self.device = language, device

    def transcribe(self, x: np.ndarray) -> str:
        if self.max_chunk_s and len(x) > self.max_chunk_s * SR:
            return " ".join(t.strip() for t in (self._transcribe(c) for c in split_long(x, self.max_chunk_s)) if t.strip())
        return self._transcribe(x).strip()

    def _transcribe(self, x: np.ndarray) -> str:
        raise NotImplementedError


class _TmpWav:
    """Some toolkits (NeMo) want file paths: write the chunk to a temporary 16 kHz WAV."""
    def __init__(self, x): self.x = x
    def __enter__(self):
        fd, self.path = tempfile.mkstemp(suffix=".wav"); os.close(fd)
        sf.write(self.path, self.x, SR, subtype="PCM_16"); return self.path
    def __exit__(self, *a):
        try: os.remove(self.path)
        except OSError: pass


# ----------------------------------------------------------------------------- reference / testing
class Echo(ASRModel):
    """Returns the reference text: checks the pipeline end to end (WER must be 0). Not a real model."""
    name = "echo"
    def __init__(self, *a, **k): super().__init__(*a, **k); self.reference = ""
    def transcribe(self, x): return self.reference


# ----------------------------------------------------------------------------- Hugging Face transformers
class WhisperHF(ASRModel):
    name, hf_id = "whisper-large-v3", "openai/whisper-large-v3"
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        import torch
        from transformers import pipeline
        self.pipe = pipeline("automatic-speech-recognition", model=self.hf_id, torch_dtype=torch.float16,
                             device=self.device, chunk_length_s=30, batch_size=8)
    def _transcribe(self, x):
        return self.pipe({"raw": x, "sampling_rate": SR},
                         generate_kwargs={"language": self.language, "task": "transcribe"})["text"]


class WhisperTurbo(WhisperHF):
    name, hf_id = "whisper-large-v3-turbo", "openai/whisper-large-v3-turbo"


class Parrotlet(ASRModel):
    """Eka Care, Indian medical English. Gated: accept the terms on Hugging Face and `hf auth login` first.
    The card's transcribe() takes clips under 30 s, so long audio is chunked at 28 s."""
    name, hf_id, max_chunk_s, languages = "parrotlet-a-en-5b", "ekacare/parrotlet-a-en-5b", 28, {"en"}
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        import torch
        from transformers import AutoModel
        self.model = AutoModel.from_pretrained(self.hf_id, trust_remote_code=True, torch_dtype=torch.bfloat16).to(self.device).eval()
    def _transcribe(self, x):
        return self.model.transcribe(x, SR)


class MedASR(ASRModel):
    """Google MedASR (medical dictation, English). Needs transformers >= 5 -> its own environment."""
    name, hf_id, languages = "medasr", "google/medasr", {"en"}
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        from transformers import pipeline
        self.pipe = pipeline("automatic-speech-recognition", model=self.hf_id, device=self.device)
    def _transcribe(self, x):
        return self.pipe({"raw": x, "sampling_rate": SR}, chunk_length_s=20, stride_length_s=2)["text"]


class IndicConformer(ASRModel):
    """AI4Bharat IndicConformer 600M (Hindi, Kannada; no English). Gated on Hugging Face."""
    name, hf_id, languages = "indicconformer-600m", "ai4bharat/indic-conformer-600m-multilingual", {"hi", "kn"}
    decoding = "ctc"
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        from transformers import AutoModel
        self.model = AutoModel.from_pretrained(self.hf_id, trust_remote_code=True)
        self.max_chunk_s = 60
    def _transcribe(self, x):
        import torch
        return self.model(torch.from_numpy(x).unsqueeze(0), self.language, self.decoding)


class IndicWhisper(ASRModel):
    """AI4Bharat IndicWhisper (Vistaar): download the per-language checkpoint zip, unzip, and pass
    its folder with --checkpoint (Hindi and Kannada are separate checkpoints)."""
    name, languages = "indicwhisper", {"hi", "kn"}
    def __init__(self, *a, checkpoint=None, **k):
        super().__init__(*a, **k)
        if not checkpoint:
            raise ValueError("indicwhisper needs --checkpoint <unzipped Vistaar checkpoint folder>")
        import torch
        from transformers import pipeline
        self.pipe = pipeline("automatic-speech-recognition", model=checkpoint, torch_dtype=torch.float16,
                             device=self.device, chunk_length_s=30)
    def _transcribe(self, x):
        return self.pipe({"raw": x, "sampling_rate": SR})["text"]


# ----------------------------------------------------------------------------- qwen-asr package
class Qwen3ASR(ASRModel):
    """Alibaba Qwen3-ASR 1.7B (English, Hindi; no Kannada). `pip install -U qwen-asr`."""
    name, hf_id, languages = "qwen3-asr-1.7b", "Qwen/Qwen3-ASR-1.7B", {"en", "hi"}
    max_chunk_s = 300           # long audio is supported; 5-min chunks keep memory and max_new_tokens bounded
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        import torch
        from qwen_asr import Qwen3ASRModel
        self.model = Qwen3ASRModel.from_pretrained(self.hf_id, dtype=torch.bfloat16, device_map=self.device,
                                                   max_inference_batch_size=8, max_new_tokens=2048)
    def _transcribe(self, x):
        return self.model.transcribe(audio=(x, SR), language=LANG_NAMES[self.language])[0].text


# ----------------------------------------------------------------------------- NVIDIA NeMo
class Parakeet(ASRModel):
    """NVIDIA Parakeet TDT 0.6B v2 (English). `pip install -U "nemo_toolkit[asr]"`.
    Handles up to ~24 min in one pass; 10-min chunks keep GPU memory modest."""
    name, hf_id, languages, max_chunk_s = "parakeet-tdt-0.6b-v2", "nvidia/parakeet-tdt-0.6b-v2", {"en"}, 600
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        import nemo.collections.asr as nemo_asr
        self.model = nemo_asr.models.ASRModel.from_pretrained(model_name=self.hf_id).to(self.device).eval()
    def _transcribe(self, x):
        with _TmpWav(x) as p:
            out = self.model.transcribe([p], verbose=False)
        o = out[0]
        return o.text if hasattr(o, "text") else str(o)


class CanaryQwen(ASRModel):
    """NVIDIA Canary-Qwen 2.5B (English). Needs NeMo from GitHub main + PyTorch >= 2.6:
    pip install "nemo_toolkit[asr,tts] @ git+https://github.com/NVIDIA/NeMo.git"
    Trained on clips up to 40 s, so long audio is chunked at 35 s."""
    name, hf_id, languages, max_chunk_s = "canary-qwen-2.5b", "nvidia/canary-qwen-2.5b", {"en"}, 35
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        from nemo.collections.speechlm2.models import SALM
        self.model = SALM.from_pretrained(self.hf_id).to(self.device).eval()
    def _transcribe(self, x):
        with _TmpWav(x) as p:
            ids = self.model.generate(prompts=[[{"role": "user", "audio": [p],
                                                 "content": f"Transcribe the following: {self.model.audio_locator_tag}"}]],
                                      max_new_tokens=256)
        return self.model.tokenizer.ids_to_text(ids[0].cpu())


REGISTRY = {m.name: m for m in (Echo, WhisperHF, WhisperTurbo, Parrotlet, MedASR, IndicConformer, IndicWhisper,
                                Qwen3ASR, Parakeet, CanaryQwen)}
