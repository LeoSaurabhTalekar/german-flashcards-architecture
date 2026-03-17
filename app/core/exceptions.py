class FlashcardAppError(Exception):
    """Base exception for the application."""


class RepositoryError(FlashcardAppError):
    """Raised when repository operations fail."""


class FlashcardNotFoundError(FlashcardAppError):
    """Raised when no flashcard can be found."""


class ExampleProviderError(FlashcardAppError):
    """Raised when example generation fails."""


class ExampleProviderConfigurationError(ExampleProviderError):
    """Raised when the example provider is not configured correctly."""