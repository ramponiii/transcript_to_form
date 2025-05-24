from pathlib import Path

SYSTEM = (Path(__file__).parent / "system.txt").read_text()
USER_INTRO = (Path(__file__).parent / "user_intro.txt").read_text()
USER_OUTRO = (Path(__file__).parent / "user_outro.txt").read_text()
