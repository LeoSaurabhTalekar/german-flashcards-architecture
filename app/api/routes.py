from app.repositories.flashcard_repository import InMemoryFlashcardRepository
from app.services.flashcard_service import FlashcardService


def get_flashcards():
    repository = InMemoryFlashcardRepository()
    service = FlashcardService(repository)
    return service.list_flashcards()