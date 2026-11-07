"""Resample flow: pick a recording, resample it, compare both files."""
from src.audio.processor import resample_wav
from src.audio.wav_io import inspect_wav
from src.config import RECORDINGS_DIR
from src.utils.files import pick_wav
from src.utils.prompts import ask_int


def resample_flow() -> None:
    """Pick an existing recording, resample it to a target rate, and compare both."""
    path = pick_wav("Resample which file", (RECORDINGS_DIR,))
    if path is None:
        return
    down_rate = ask_int("Resample to (Hz)", 16_000)

    down_path = resample_wav(path, down_rate)

    # Compare both files: metadata + duration side by side.
    for p in (path, down_path):
        inspect_wav(p)
