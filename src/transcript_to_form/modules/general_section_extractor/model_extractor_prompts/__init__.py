from pathlib import Path

SYSTEM_EXTRACT = (Path(__file__).parent / "system.txt").read_text()
USER_EXTRACT = (Path(__file__).parent / "user.txt").read_text()
