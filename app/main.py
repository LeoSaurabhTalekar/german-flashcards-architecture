from app.repositories.flashcard_repository import InMemoryFlashcardRepository
from app.services.flashcard_service import FlashcardService


def main() -> None:
    repository = InMemoryFlashcardRepository()
    service = FlashcardService(repository)

    flashcards = service.list_flashcards()

    print("German Flashcards Architecture - Backend Entry Point")
    print(f"Loaded {len(flashcards)} flashcards")


if __name__ == "__main__":
    main()