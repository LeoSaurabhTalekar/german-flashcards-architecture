from types import SimpleNamespace

from app.models.flashcard import Flashcard
from app.providers.openai_example_provider import OpenAIExampleProvider


class FakeResponsesAPI:
    def parse(self, **kwargs):
        parsed = SimpleNamespace(
            examples=[
                SimpleNamespace(german="Ich habe grundlegende Kenntnisse in Python.", english="I have basic knowledge in Python."),
                SimpleNamespace(german="Das ist ein grundlegendes Konzept.", english="That is a fundamental concept."),
            ]
        )
        return SimpleNamespace(output_parsed=parsed)


class FakeOpenAIClient:
    def __init__(self):
        self.responses = FakeResponsesAPI()


def test_openai_example_provider_maps_parsed_response() -> None:
    provider = OpenAIExampleProvider(
        client=FakeOpenAIClient(),
        model="gpt-5.4",
    )

    flashcard = Flashcard(
        german="grundlegend",
        english="basic / fundamental",
        meaning_simple="forming the basis",
    )

    examples = provider.generate_examples(flashcard, count=2)

    assert len(examples) == 2
    assert examples[0].german == "Ich habe grundlegende Kenntnisse in Python."
    assert examples[0].english == "I have basic knowledge in Python."