"""Record flow: ask configs, record, save, inspect."""
from src.audio.recorder import record
from src.audio.wav_io import inspect_wav, save_wav
from src.config import RECORDINGS_DIR
from src.utils.files import pick_wav  # noqa: F401  (re-exported for parity)
from src.utils.prompts import ask_int, ask_path


def record_flow() -> None:
    """Ask for recording configs, then record, save, and inspect."""
    rate = ask_int("Sample rate (Hz)", 16_000)
    channels = ask_int("Channels", 1)
    duration = ask_int("Duration (seconds)", 5)
    path = ask_path("Save as", RECORDINGS_DIR)

    audio = record(rate, channels, duration)
    print(f"Captured array -> shape: {audio.shape} | dtype: {audio.dtype}")
    save_wav(audio, path, rate, channels)
    inspect_wav(path)
