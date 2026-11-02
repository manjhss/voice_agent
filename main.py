"""Record 5 s of audio from the mic, save it as WAV, inspect it, play it back."""

import wave

import numpy as np
import sounddevice as sd

WAV_PATH = "recording.wav"
SAMPLE_RATE = 16_000  # Hz
CHANNELS = 1  # mono
DURATION = 5  # seconds


def record() -> np.ndarray:
    """Capture DURATION seconds of audio from the default mic as 16-bit PCM samples."""
    print(f"Recording {DURATION}s ... speak now!")
    audio = sd.rec(
        frames=DURATION * SAMPLE_RATE,
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",  # 16-bit PCM
    )
    sd.wait()  # block until recording is done
    print("Done.\n")
    return audio


def save_wav(audio: np.ndarray) -> None:
    """Write raw PCM samples to WAV_PATH with the configured format."""
    with wave.open(WAV_PATH, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 2 bytes = 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    print(f"Saved to {WAV_PATH}")


def read_wav() -> tuple[np.ndarray, dict]:
    """Read samples and metadata from the WAV file."""
    with wave.open(WAV_PATH, "rb") as wf:
        meta = {
            "sample_rate": wf.getframerate(),
            "channels": wf.getnchannels(),
            "sample_width": wf.getsampwidth(),
            "frames": wf.getnframes(),
        }
        samples = np.frombuffer(wf.readframes(meta["frames"]), dtype="int16")
    return samples.reshape(-1, meta["channels"]), meta


def inspect_wav() -> None:
    """Print the WAV file's metadata, duration, and amplitude stats."""
    audio, meta = read_wav()

    duration = meta["frames"] / meta["sample_rate"]

    print(f"\nWAV metadata -> sample rate: {meta['sample_rate']} Hz | channels: {meta['channels']} "
          f"| sample width: {meta['sample_width']} bytes | frames: {meta['frames']}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Amplitude -> min: {audio.min()} | max: {audio.max()} | mean: {audio.mean():.1f}")


def play() -> None:
    """Play the saved WAV through the default speaker using the file's own sample rate."""
    samples, meta = read_wav()
    print(f"\nPlaying back at {meta['sample_rate']} Hz (from file) ...")
    sd.play(samples, samplerate=meta["sample_rate"])
    sd.wait()
    print("Playback finished.")


def main() -> None:
    """Run the full pipeline: record -> save -> inspect -> play."""
    audio = record()
    print(f"Captured array -> shape: {audio.shape} | dtype: {audio.dtype}")
    save_wav(audio)
    inspect_wav()
    play()


if __name__ == "__main__":
    main()
