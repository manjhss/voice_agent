"""Record audio from the mic, save it as WAV, resample it, and play it on demand."""

import wave
from math import gcd
from pathlib import Path

import numpy as np
import sounddevice as sd
from scipy.signal import resample_poly

RECORDINGS_DIR = Path("recordings")
RESAMPLED_DIR = Path("resampled")


def ask(prompt: str, default) -> str:
    """Prompt the user for a value, returning the default on empty input."""
    return input(f"{prompt} [{default}]: ").strip() or str(default)


def ask_int(prompt: str, default: int) -> int:
    """Prompt for a positive integer, re-asking until the input is valid."""
    while True:
        try:
            value = int(ask(prompt, default))
            if value > 0:
                return value
        except ValueError:
            pass
        print("Please enter a positive integer.")


def ask_path(prompt: str, folder: Path) -> Path:
    """Prompt for a file name (required) and return it inside the given folder."""
    while True:
        name = input(f"{prompt} (saved in {folder}/): ").strip()
        if name:
            return folder / Path(name)
        print("File name can't be empty.")


def record(rate: int, channels: int, duration: int) -> np.ndarray:
    """Capture the given duration of audio from the default mic as 16-bit PCM samples."""
    print(f"\nRecording {duration}s ... speak now!")
    audio = sd.rec(frames=duration * rate, samplerate=rate, channels=channels, dtype="int16")
    sd.wait()  # block until recording is done
    print("Done.")
    return audio


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


def play(path: Path, rate: int, channels: int) -> None:
    """Play the WAV file using the user-provided sample rate and channel count."""
    samples, meta = read_wav(path)
    print(f"(file says {meta['sample_rate']} Hz / {meta['channels']} ch)")
    sd.play(samples.reshape(-1, channels), samplerate=rate)
    sd.wait()
    print("Playback finished.")


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


def find_wav(name: str) -> Path | None:
    """Look up a wav by name in recordings/ then resampled/."""
    for folder in (RECORDINGS_DIR, RESAMPLED_DIR):
        path = folder / name
        if path.exists():
            return path
    return None


def play_flow() -> None:
    """Ask which file to play and its playback configs, then play it."""
    path = None
    while path is None:
        name = input("WAV file to play (in recordings/ or resampled/): ").strip()
        if not name:
            print("File name can't be empty.")
            continue
        path = find_wav(name)
        if path is None:
            print(f"'{name}' not found in recordings/ or resampled/.")
    rate = ask_int("Sample rate (Hz)", 16_000)
    channels = ask_int("Channels", 1)
    play(path, rate, channels)


def resample_flow() -> None:
    """Pick an existing recording, resample it to a target rate, and compare both."""
    files = sorted(RECORDINGS_DIR.glob("*.wav"))
    if not files:
        print("No recordings found in recordings/. Record something first.")
        return
    print("\nAvailable recordings:")
    for f in files:
        print(f"  - {f.name}")

    path = None
    while path is None:
        name = input("Resample which file: ").strip()
        if not name:
            print("File name can't be empty.")
            continue
        candidate = RECORDINGS_DIR / name
        if candidate.exists():
            path = candidate
        else:
            print(f"'{name}' not found in recordings/.")
    down_rate = ask_int(f"Resample to (Hz)", 16_000)

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

    # Compare both files: metadata + duration side by side.
    for p in (path, down_path):
        inspect_wav(p)


def main() -> None:
    """Show a menu and dispatch to a flow until quit."""
    RECORDINGS_DIR.mkdir(exist_ok=True)
    RESAMPLED_DIR.mkdir(exist_ok=True)
    while True:
        print("\n=== Voice Agent ===")
        print("1. Record  2. Play  3. Resample  4. Quit")
        choice = input("Choose: ").strip()
        if choice == "1":
            record_flow()
        elif choice == "2":
            play_flow()
        elif choice == "3":
            resample_flow()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
