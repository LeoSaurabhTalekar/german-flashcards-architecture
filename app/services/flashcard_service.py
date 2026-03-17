from __future__ import annotations

import random
from typing import List

from app.core.exceptions import FlashcardNotFoundError
from app.models.flashcard import Flashcard
from app.repositories.flashcard_repository import FlashcardRepository


class FlashcardService:
    def __init__(self, repository: FlashcardRepository) -> None:
        self.repository = repository

    def list_flashcards(self) -> List[Flashcard]:
        return self.repository.get_all_flashcards()

    def get_random_flashcard(self) -> Flashcard:
        flashcards = self.repository.get_all_flashcards()
        if not flashcards:
            raise FlashcardNotFoundError("No flashcards available.")
        return random.choice(flashcards)