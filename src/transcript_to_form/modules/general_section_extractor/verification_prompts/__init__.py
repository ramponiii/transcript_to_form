from pathlib import Path

SYSTEM_VERIFICATION = (Path(__file__).parent / "system.txt").read_text()
USER_VERIFICATION = (Path(__file__).parent / "user.txt").read_text()
