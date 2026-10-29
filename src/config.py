import os
from dotenv import load_dotenv

load_dotenv()


def get_required_setting(name: str) -> str:
    value = os.getenv(name)

    if not value or not value.strip():
        raise RuntimeError(
            f"Required configuration '{name}' is missing. "
            "Check your .env file."
        )

    return value.strip()


GEMINI_API_KEY = get_required_setting("GEMINI_API_KEY")
GEMINI_MODEL = get_required_setting("GEMINI_MODEL")
