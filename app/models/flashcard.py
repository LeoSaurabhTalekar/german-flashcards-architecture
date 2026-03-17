from dataclasses import dataclass
from typing import Optional


@dataclass
class Flashcard:
    german: str
    english: str
    meaning_simple: Optional[str] = None
    german_example: Optional[str] = None
    english_example: Optional[str] = None
    source_file: Optional[str] = None
    sheet_name: Optional[str] = None