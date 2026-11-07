"""Terminal prompting helpers shared by all flows."""

from pathlib import Path


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
