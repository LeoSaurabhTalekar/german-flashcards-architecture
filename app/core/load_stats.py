from dataclasses import dataclass, field
from typing import List

from app.models.flashcard import Flashcard


@dataclass
class LoadStats:
    files_processed: int = 0
    sheets_processed: int = 0
    total_rows: int = 0
    valid_rows: int = 0
    loaded_flashcards: int = 0
    duplicates_skipped: int = 0
    invalid_rows_skipped: int = 0


@dataclass
class FlashcardLoadResult:
    flashcards: List[Flashcard] = field(default_factory=list)
    stats: LoadStats = field(default_factory=LoadStats)