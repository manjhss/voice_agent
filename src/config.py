"""Shared paths and model settings for the voice agent."""

from pathlib import Path

RECORDINGS_DIR = Path("recordings")
RESAMPLED_DIR = Path("resampled")
MODEL_DIR = Path("models") / "faster-whisper-small"
EXPECTED_MODEL_SIZE = 483_546_902  # bytes; ctranslate2 crashes on a partial file
