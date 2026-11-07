"""WAV reading, writing, and inspection."""
import wave
from pathlib import Path

import numpy as np


def save_wav(audio: np.ndarray, path: Path, rate: int, channels: int) -> None:
    """Write raw PCM samples to path, creating parent folders as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 2 bytes = 16-bit
        wf.setframerate(rate)
        wf.writeframes(audio.tobytes())
    print(f"Saved to {path}")


def read_wav(path: Path) -> tuple[np.ndarray, dict]:
    """Read flat int16 samples and metadata from the WAV file."""
    with wave.open(str(path), "rb") as wf:
        meta = {
            "sample_rate": wf.getframerate(),
            "channels": wf.getnchannels(),
            "sample_width": wf.getsampwidth(),
            "frames": wf.getnframes(),
        }
        samples = np.frombuffer(wf.readframes(meta["frames"]), dtype="int16")
    return samples, meta


def inspect_wav(path: Path) -> None:
    """Print the WAV file's metadata, duration, and amplitude stats."""
    samples, meta = read_wav(path)

    duration = meta["frames"] / meta["sample_rate"]

    print(f"\nWAV metadata -> sample rate: {meta['sample_rate']} Hz | channels: {meta['channels']} "
          f"| sample width: {meta['sample_width']} bytes | frames: {meta['frames']}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Amplitude -> min: {samples.min()} | max: {samples.max()} | mean: {samples.mean():.1f}")
