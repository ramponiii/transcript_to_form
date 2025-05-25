from pathlib import Path

SYSTEM = (Path(__file__).parent / "system.txt").read_text()
USER = (Path(__file__).parent / "user.txt").read_text()

SYSTEM_MODEL = (Path(__file__).parent / "system_model.txt").read_text()
USER_MODEL = (Path(__file__).parent / "user_model.txt").read_text()

SYSTEM_VERIFICATION = (Path(__file__).parent / "system_verification.txt").read_text()
USER_VERIFICATION = (Path(__file__).parent / "user_verification.txt").read_text()
