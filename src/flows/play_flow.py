"""Play flow: pick a file, ask playback configs, play."""
from src.audio.player import play
from src.config import RECORDINGS_DIR, RESAMPLED_DIR
from src.utils.files import pick_wav
from src.utils.prompts import ask_int


def play_flow() -> None:
    """Ask which file to play and its playback configs, then play it."""
    path = pick_wav("WAV file to play", (RECORDINGS_DIR, RESAMPLED_DIR))
    if path is None:
        return
    rate = ask_int("Sample rate (Hz)", 16_000)
    channels = ask_int("Channels", 1)
    play(path, rate, channels)
