"""Speaker playback."""
from pathlib import Path

import sounddevice as sd

from src.audio.wav_io import read_wav


def play(path: Path, rate: int, channels: int) -> None:
    """Play the WAV file using the user-provided sample rate and channel count."""
    samples, meta = read_wav(path)
    print(f"(file says {meta['sample_rate']} Hz / {meta['channels']} ch)")
    sd.play(samples.reshape(-1, channels), samplerate=rate)
    sd.wait()
    print("Playback finished.")
