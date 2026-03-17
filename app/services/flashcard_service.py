from __future__ import annotations

import random
from typing import List

from app.core.exceptions import FlashcardNotFoundError
from app.core.load_stats import FlashcardLoadResult
from app.models.flashcard import Flashcard
from app.repositories.flashcard_repository import FlashcardRepository


class FlashcardService:
    def __init__(self, repository: FlashcardRepository) -> None:
        self.repository = repository

    def load_flashcards(self) -> FlashcardLoadResult:
        return self.repository.get_load_result()

    def list_flashcards(self) -> List[Flashcard]:
        return self.load_flashcards().flashcards

    @staticmethod
    def select_random_flashcard(flashcards: List[Flashcard]) -> Flashcard:
        if not flashcards:
            raise FlashcardNotFoundError("No flashcards available.")
        return random.choice(flashcards)