from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

APP_NAME = "German Flashcards Architecture"
DEFAULT_SAMPLE_FILE = DATA_DIR / "sample_flashcards.xlsx"

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
OPENAI_TIMEOUT_SECONDS = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30"))

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))