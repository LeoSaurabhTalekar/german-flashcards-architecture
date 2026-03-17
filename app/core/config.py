from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

APP_NAME = "German Flashcards Architecture"
DEFAULT_SAMPLE_FILE = DATA_DIR / "sample_flashcards.xlsx"