from app.repositories.flashcard_repository import InMemoryFlashcardRepository
from app.services.flashcard_service import FlashcardService


def test_list_flashcards_returns_data():
    repository = InMemoryFlashcardRepository()
    service = FlashcardService(repository)

    result = service.list_flashcards()

    assert len(result) > 0
    assert result[0].german is not None
    assert result[0].english is not None