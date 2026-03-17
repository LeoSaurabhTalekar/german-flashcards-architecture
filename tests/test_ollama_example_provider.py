from app.models.flashcard import Flashcard
from app.providers.ollama_example_provider import OllamaExampleProvider


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200
        self.text = ""

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_ollama_provider_parses_json_response(monkeypatch):
    def fake_post(*args, **kwargs):
        return FakeResponse(
            {
                "response": """
                {
                  "examples": [
                    {
                      "german": "Das ist ein grundlegendes Konzept.",
                      "english": "That is a fundamental concept."
                    },
                    {
                      "german": "Ich habe grundlegende Kenntnisse in Python.",
                      "english": "I have basic knowledge in Python."
                    }
                  ]
                }
                """
            }
        )

    monkeypatch.setattr("app.providers.ollama_example_provider.requests.post", fake_post)

    provider = OllamaExampleProvider()
    flashcard = Flashcard(german="grundlegend", english="basic / fundamental")

    examples = provider.generate_examples(flashcard, count=2)

    assert len(examples) == 2
    assert examples[0].german == "Das ist ein grundlegendes Konzept."
    assert examples[0].english == "That is a fundamental concept."