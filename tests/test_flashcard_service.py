from dataclasses import dataclass

import pytest

from app.core.exceptions import FlashcardNotFoundError
from app.core.load_stats import FlashcardLoadResult, LoadStats
from app.models.flashcard import Flashcard
from app.repositories.flashcard_repository import FlashcardRepository
from app.services.flashcard_service import FlashcardService


@dataclass
class FakeFlashcardRepository(FlashcardRepository):
    load_result: FlashcardLoadResult

    def get_load_result(self) -> FlashcardLoadResult:
        return self.load_result


def test_load_flashcards_returns_result() -> None:
    flashcards = [
        Flashcard(german="grundlegend", english="basic"),
        Flashcard(german="wichtig", english="important"),
    ]
    stats = LoadStats(
        files_processed=1,
        sheets_processed=1,
        total_rows=2,
        valid_rows=2,
        loaded_flashcards=2,
    )
    repository = FakeFlashcardRepository(
        load_result=FlashcardLoadResult(flashcards=flashcards, stats=stats)
    )
    service = FlashcardService(repository)

    result = service.load_flashcards()

    assert len(result.flashcards) == 2
    assert result.stats.loaded_flashcards == 2
    assert result.flashcards[0].german == "grundlegend"


def test_list_flashcards_returns_flashcards_only() -> None:
    flashcards = [
        Flashcard(german="klar", english="clear"),
        Flashcard(german="neu", english="new"),
    ]
    repository = FakeFlashcardRepository(
        load_result=FlashcardLoadResult(flashcards=flashcards, stats=LoadStats())
    )
    service = FlashcardService(repository)

    result = service.list_flashcards()

    assert len(result) == 2
    assert result[0].german == "klar"
    assert result[1].english == "new"


def test_select_random_flashcard_returns_one_of_available_cards() -> None:
    flashcards = [
        Flashcard(german="grundlegend", english="basic"),
        Flashcard(german="wichtig", english="important"),
        Flashcard(german="neu", english="new"),
    ]

    card = FlashcardService.select_random_flashcard(flashcards)

    assert card in flashcards


def test_select_random_flashcard_raises_for_empty_list() -> None:
    with pytest.raises(FlashcardNotFoundError, match="No flashcards available"):
        FlashcardService.select_random_flashcard([])