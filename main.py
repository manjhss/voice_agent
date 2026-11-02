"""Record audio from the mic, save it as WAV, and inspect or play it on demand."""

import wave
from pathlib import Path

import numpy as np
import sounddevice as sd

RECORDINGS_DIR = Path("recordings")
DEFAULT_WAV = RECORDINGS_DIR / "recording.wav"


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
    path = Path(ask("Save as", DEFAULT_WAV))

    audio = record(rate, channels, duration)
    print(f"Captured array -> shape: {audio.shape} | dtype: {audio.dtype}")
    save_wav(audio, path, rate, channels)
    inspect_wav(path)


def play_flow() -> None:
    """Ask for playback configs (path, rate, channels), then play the file."""
    path = Path(ask("WAV file to play", DEFAULT_WAV))
    rate = ask_int("Sample rate (Hz)", 16_000)
    channels = ask_int("Channels", 1)
    play(path, rate, channels)


def main() -> None:
    """Show a menu and dispatch to the record or play flow until quit."""
    RECORDINGS_DIR.mkdir(exist_ok=True)
    while True:
        print("\n=== Voice Agent ===")
        print("1. Record  2. Play  3. Quit")
        choice = input("Choose: ").strip()
        if choice == "1":
            record_flow()
        elif choice == "2":
            play_flow()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
