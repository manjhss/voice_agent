"""Sample-rate conversion."""
from math import gcd

import numpy as np
from scipy.signal import resample_poly

from src.audio.wav_io import read_wav, save_wav
from src.config import RESAMPLED_DIR


def resample_wav(path, down_rate: int):
    """Resample an existing WAV to down_rate, save it in resampled/, return its path."""
    samples, meta = read_wav(path)
    up_rate, channels = meta["sample_rate"], meta["channels"]
    print(f"\nSource: {path.name} -> {up_rate} Hz, {channels} ch, "
          f"{meta['frames']} frames")

    # Changing only the WAV's sample-rate metadata would relabel the timeline
    # (5 s of audio would claim to be 1.67 s) and make playback 3x too fast.
    # Resampling actually recomputes the samples for the new rate.
    g = gcd(up_rate, down_rate)  # exact for any rate pair, e.g. 48000 -> 16000
    resampled = resample_poly(
        samples.reshape(-1, channels), up=down_rate // g, down=up_rate // g, axis=0
    )
    resampled = np.clip(resampled, -32768, 32767).astype("int16")
    down_path = RESAMPLED_DIR / f"{path.stem}_{down_rate}.wav"
    save_wav(resampled, down_path, down_rate, channels)
    return down_path
