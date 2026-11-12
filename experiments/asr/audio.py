"""Audio loading and long-audio chunking shared by all ASR adapters."""
from pathlib import Path
import numpy as np
import soundfile as sf

SR = 16000


def load_sample(data_root: Path, row: dict) -> np.ndarray:
    """Load one manifest row as 16 kHz mono float32.
    Utterance manifests carry start_s / end_s offsets into the full track; other manifests are whole files."""
    path = Path(data_root) / row["relative_audio_path"]
    start, end = row.get("start_s"), row.get("end_s")
    if start not in (None, "") and end not in (None, ""):
        info = sf.info(str(path))
        a, b = int(float(start) * info.samplerate), int(float(end) * info.samplerate)
        x, sr = sf.read(str(path), start=a, stop=b, dtype="float32")
    else:
        x, sr = sf.read(str(path), dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != SR:
        raise ValueError(f"{path}: expected {SR} Hz, got {sr} (the benchmark is 16 kHz throughout)")
    return x


def split_long(x: np.ndarray, max_s: float, search_s: float = 5.0, frame_s: float = 0.1):
    """Split audio into chunks of at most max_s seconds, cutting at the quietest 100 ms frame
    in the last `search_s` seconds of each window so words are rarely cut in half."""
    max_n, out, pos = int(max_s * SR), [], 0
    frame = int(frame_s * SR)
    while len(x) - pos > max_n:
        lo, hi = pos + max_n - int(search_s * SR), pos + max_n
        seg = x[lo:hi]
        nf = len(seg) // frame
        energy = (seg[: nf * frame].reshape(nf, frame) ** 2).mean(axis=1)
        cut = lo + int(np.argmin(energy)) * frame + frame // 2
        out.append(x[pos:cut]); pos = cut
    out.append(x[pos:])
    return out
