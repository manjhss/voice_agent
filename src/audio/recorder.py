"""Microphone capture."""
import numpy as np
import sounddevice as sd


def record(rate: int, channels: int, duration: int) -> np.ndarray:
    """Capture the given duration of audio from the default mic as 16-bit PCM samples."""
    print(f"\nRecording {duration}s ... speak now!")
    audio = sd.rec(frames=duration * rate, samplerate=rate, channels=channels, dtype="int16")
    sd.wait()  # block until recording is done
    print("Done.")
    return audio
