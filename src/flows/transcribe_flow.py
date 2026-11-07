"""Transcribe flow: pick a recording, run it through faster-whisper."""
from src.config import RECORDINGS_DIR, RESAMPLED_DIR
from src.speech.stt import load_model, transcribe
from src.utils.files import pick_wav


def transcribe_flow() -> None:
    """Pick an existing recording and transcribe it with faster-whisper (CPU, int8)."""
    path = pick_wav("Transcribe which file", (RECORDINGS_DIR, RESAMPLED_DIR))
    if path is None:
        return

    try:
        model = load_model()
    except RuntimeError as exc:
        print(f"\n{exc}")
        return

    transcribe(model, path, language="all")
