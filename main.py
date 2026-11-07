"""Voice Agent entry point: menu that dispatches to the feature flows."""

from src.config import RECORDINGS_DIR, RESAMPLED_DIR
from src.flows.play_flow import play_flow
from src.flows.record_flow import record_flow
from src.flows.resample_flow import resample_flow
from src.flows.transcribe_flow import transcribe_flow


def main() -> None:
    """Show a menu and dispatch to a flow until quit."""
    RECORDINGS_DIR.mkdir(exist_ok=True)
    RESAMPLED_DIR.mkdir(exist_ok=True)
    while True:
        print("\n=== Voice Agent ===")
        print("1. Record  2. Play  3. Resample  4. Transcribe  5. Quit")
        choice = input("Choose: ").strip()
        if choice == "1":
            record_flow()
        elif choice == "2":
            play_flow()
        elif choice == "3":
            resample_flow()
        elif choice == "4":
            transcribe_flow()
        elif choice == "5":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
