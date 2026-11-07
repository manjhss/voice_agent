"""Speech-to-text with faster-whisper, using local models when available."""
from math import gcd
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel
from scipy.signal import resample_poly

from src.audio.wav_io import read_wav
from src.config import EXPECTED_MODEL_SIZE, MODEL_DIR


def load_model() -> WhisperModel:
    """Load the Whisper model (CPU, int8) from models/ when complete, else from HF."""
    model_file = MODEL_DIR / "model.bin"
    if model_file.exists():
        size = model_file.stat().st_size
        if size < EXPECTED_MODEL_SIZE:
            raise RuntimeError(
                f"Model file is incomplete (still downloading?): "
                f"got {size:,} bytes, need {EXPECTED_MODEL_SIZE:,}. "
                "Wait for the download, or delete models/ and rerun to redownload."
            )
        source = str(MODEL_DIR)
        print(f"\nLoading Whisper model from {MODEL_DIR} (CPU, int8) ...")
    else:
        source = MODEL_DIR.name.replace("faster-whisper-", "")
        print(f"\nLoading Whisper '{source}' model (CPU, int8) ... "
              "(first run downloads it)")
    return WhisperModel(source, device="cpu", compute_type="int8")


def wav_to_whisper_audio(path: Path) -> np.ndarray:
    """Decode a WAV to float32 mono 16 kHz in [-1, 1], what Whisper expects.

    This bypasses PyAV entirely (av 19 dropped the API faster-whisper's
    file-decoding path uses) — fine here since we only handle WAVs.
    """
    samples, meta = read_wav(path)
    audio = samples.reshape(-1, meta["channels"]).astype(np.float32) / 32768.0
    audio = audio.mean(axis=1)  # downmix; no-op flatten for mono
    if meta["sample_rate"] != 16_000:
        g = gcd(meta["sample_rate"], 16_000)
        audio = resample_poly(audio, up=16_000 // g, down=meta["sample_rate"] // g)
    return audio


def transcribe(model: WhisperModel, path: Path, language: str | None = None) -> None:
    """Transcribe path and print detected language plus time-aligned segments."""
    print(f"Transcribing {path.name} ...")
    audio = wav_to_whisper_audio(path)

    segments, info = model.transcribe(audio, beam_size=5, language=language)

    # Metadata: detected language and how confident the model is about it.
    print(f"\nDetected language: {info.language} "
          f"(probability: {info.language_probability:.2f})")

    # segments is a generator; drawing from it runs the actual transcription.
    print("\n--- Transcription ---")
    for seg in segments:
        print(f"[{seg.start:07.2f} -> {seg.end:07.2f}] {seg.text.strip()}")
    print("--- End ---")
