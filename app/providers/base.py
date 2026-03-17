from abc import ABC, abstractmethod
from typing import List

from app.models.flashcard import Flashcard
from app.models.generated_example import GeneratedExample


class ExampleProvider(ABC):
    @abstractmethod
    def generate_examples(
        self,
        flashcard: Flashcard,
        count: int = 5,
    ) -> List[GeneratedExample]:
        """Generate example sentences for the given flashcard."""