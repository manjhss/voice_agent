"""WAV lookup helpers shared by the interactive flows."""

from pathlib import Path


def find_wav(name: str, folders: tuple[Path, ...]) -> Path | None:
    """Look up a wav by name in the given folders, in order."""
    for folder in folders:
        path = folder / name
        if path.exists():
            return path
    return None


def pick_wav(prompt: str, folders: tuple[Path, ...]) -> Path | None:
    """List wavs in the given folders and return the user's choice, or None on quit."""
    files = sorted({f for folder in folders for f in folder.glob("*.wav")})
    if not files:
        print(f"No WAV files found in {[str(f) + '/' for f in folders]}. Record something first.")
        return None
    print("\nAvailable files:")
    for f in files:
        print(f"  - {f.parent.name}/{f.name}")
    while True:
        name = input(f"{prompt}: ").strip()
        if not name:
            print("File name can't be empty.")
            continue
        # Accept folder-qualified paths like "recordings/s1.wav" as-is.
        if "/" in name or "\\" in name:
            path = Path(name)
            if path.exists():
                return path
            print(f"'{name}' not found.")
            continue
        path = find_wav(name, folders)
        if path is None:
            print(f"'{name}' not found in {[str(f) + '/' for f in folders]}.")
            continue
        return path
