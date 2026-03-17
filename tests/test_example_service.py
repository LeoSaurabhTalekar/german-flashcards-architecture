from typing import List

from app.models.flashcard import Flashcard
from app.models.generated_example import GeneratedExample
from app.providers.base import ExampleProvider
from app.providers.local_example_provider import LocalTemplateExampleProvider
from app.services.example_service import ExampleService


class FakeExampleProvider(ExampleProvider):
    def generate_examples(
        self,
        flashcard: Flashcard,
        count: int = 5,
    ) -> List[GeneratedExample]:
        return [
            GeneratedExample(
                german=f"Fake example for {flashcard.german} #{index}",
                english=f"Fake example for {flashcard.english} #{index}",
            )
            for index in range(1, count + 1)
        ]


def test_local_template_provider_returns_requested_number_of_examples() -> None:
    flashcard = Flashcard(
        german="grundlegend",
        english="basic / fundamental",
    )
    provider = LocalTemplateExampleProvider()

    examples = provider.generate_examples(flashcard, count=5)

    assert len(examples) == 5
    assert all(isinstance(example, GeneratedExample) for example in examples)
    assert any("grundlegend" in example.german for example in examples)


def test_example_service_uses_provider() -> None:
    flashcard = Flashcard(
        german="wichtig",
        english="important",
    )
    service = ExampleService(FakeExampleProvider())

    examples = service.get_examples_for_flashcard(flashcard, count=5)

    assert len(examples) == 5
    assert examples[0].german == "Fake example for wichtig #1"
    assert examples[0].english == "Fake example for important #1"