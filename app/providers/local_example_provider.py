from typing import List

from app.models.flashcard import Flashcard
from app.models.generated_example import GeneratedExample
from app.providers.base import ExampleProvider


class LocalTemplateExampleProvider(ExampleProvider):
    """
    Local mock provider for Day 4.
    It generates template-based examples without calling any external API.
    Later this can be replaced by an LLM/API-backed provider.
    """

    def generate_examples(
        self,
        flashcard: Flashcard,
        count: int = 5,
    ) -> List[GeneratedExample]:
        if count <= 0:
            return []

        word = flashcard.german.strip()
        english = flashcard.english.strip()

        templates = [
            GeneratedExample(
                german=f"Im Interview möchte ich '{word}' sicher verwenden.",
                english=f"In the interview, I want to use '{english}' confidently.",
            ),
            GeneratedExample(
                german=f"Für mein nächstes Gespräch übe ich heute besonders '{word}'.",
                english=f"For my next conversation, I am especially practicing '{english}' today.",
            ),
            GeneratedExample(
                german=f"Kannst du mir erklären, wann man '{word}' am besten benutzt?",
                english=f"Can you explain when '{english}' is best used?",
            ),
            GeneratedExample(
                german=f"Ich wiederhole '{word}', damit ich es später flüssig sagen kann.",
                english=f"I repeat '{english}' so that I can say it fluently later.",
            ),
            GeneratedExample(
                german=f"In meinen Notizen habe ich '{word}' mit einem eigenen Beispiel markiert.",
                english=f"In my notes, I marked '{english}' with my own example.",
            ),
            GeneratedExample(
                german=f"Beim Lernen hilft mir '{word}', meinen Wortschatz systematisch zu erweitern.",
                english=f"While learning, '{english}' helps me expand my vocabulary systematically.",
            ),
            GeneratedExample(
                german=f"Ich möchte '{word}' nicht nur erkennen, sondern auch aktiv im Satz verwenden.",
                english=f"I want not only to recognize '{english}', but also to use it actively in a sentence.",
            ),
        ]

        return templates[:count]