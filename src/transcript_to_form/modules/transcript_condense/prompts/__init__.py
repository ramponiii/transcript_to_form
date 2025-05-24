from pathlib import Path

SYSTEM = (Path(__file__).parent / "system.txt").read_text()
USER = (Path(__file__).parent / "user.txt").read_text()
