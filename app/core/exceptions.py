class FlashcardAppError(Exception):
    """Base exception for the application."""


class RepositoryError(FlashcardAppError):
    """Raised when repository operations fail."""


class FlashcardNotFoundError(FlashcardAppError):
    """Raised when no flashcard can be found."""