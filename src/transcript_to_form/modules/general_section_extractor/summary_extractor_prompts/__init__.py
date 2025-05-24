from pathlib import Path

SYSTEM_SUMMARY = (Path(__file__).parent / "system.txt").read_text()
USER_SUMMARY = (Path(__file__).parent / "user.txt").read_text()
