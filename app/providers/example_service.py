from typing import List

from app.models.flashcard import Flashcard
from app.models.generated_example import GeneratedExample
from app.providers.base import ExampleProvider


class ExampleService:
    def __init__(self, provider: ExampleProvider) -> None:
        self.provider = provider

    def get_examples_for_flashcard(
        self,
        flashcard: Flashcard,
        count: int = 5,
    ) -> List[GeneratedExample]:
        return self.provider.generate_examples(flashcard, count=count)