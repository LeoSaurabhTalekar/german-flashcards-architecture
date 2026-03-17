from __future__ import annotations

import json
from typing import List

import requests

from app.core.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT_SECONDS,
)
from app.core.exceptions import ExampleProviderError
from app.models.flashcard import Flashcard
from app.models.generated_example import GeneratedExample
from app.providers.base import ExampleProvider


class OllamaExampleProvider(ExampleProvider):
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout_seconds: float = OLLAMA_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate_examples(
        self,
        flashcard: Flashcard,
        count: int = 5,
    ) -> List[GeneratedExample]:
        if count <= 0:
            return []

        prompt = self._build_prompt(flashcard=flashcard, count=count)

        schema = {
            "type": "object",
            "properties": {
                "examples": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "german": {"type": "string"},
                            "english": {"type": "string"},
                        },
                        "required": ["german", "english"],
                    },
                }
            },
            "required": ["examples"],
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": schema,
        }

        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            raise ExampleProviderError(
                "Could not connect to Ollama at http://localhost:11434. "
                "Make sure Ollama is installed and running."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise ExampleProviderError(
                "Ollama took too long to respond. Try a smaller model or wait longer."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise ExampleProviderError(
                f"Ollama returned HTTP {response.status_code}: {response.text}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise ExampleProviderError(f"Ollama request failed: {exc}") from exc

        data = response.json()
        raw_text = data.get("response", "").strip()

        if not raw_text:
            raise ExampleProviderError("Ollama returned an empty response.")

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ExampleProviderError(
                f"Ollama returned non-JSON output: {raw_text[:300]}"
            ) from exc

        items = parsed.get("examples", [])
        if not items:
            raise ExampleProviderError("Ollama did not return any examples.")

        examples: List[GeneratedExample] = []
        for item in items[:count]:
            german = str(item.get("german", "")).strip()
            english = str(item.get("english", "")).strip()

            if german and english:
                examples.append(
                    GeneratedExample(
                        german=german,
                        english=english,
                    )
                )

        if not examples:
            raise ExampleProviderError("Ollama returned no valid example pairs.")

        return examples

    @staticmethod
    def _build_prompt(flashcard: Flashcard, count: int) -> str:
        meaning_hint = flashcard.meaning_simple or ""
        german_example = flashcard.german_example or ""
        english_example = flashcard.english_example or ""

        return f"""
Generate exactly {count} fresh example pairs for this German flashcard.

Target word: {flashcard.german}
English meaning: {flashcard.english}
Meaning hint: {meaning_hint}

Optional stored examples for context:
German stored example: {german_example}
English stored example: {english_example}

Rules:
1. Return valid JSON only.
2. JSON format:
{{
  "examples": [
    {{"german": "...", "english": "..."}}
  ]
}}
3. Return exactly {count} examples.
4. Each German sentence must use the target word or a natural inflected form.
5. German must be natural and grammatically correct.
6. English must be a faithful natural translation.
7. Prefer B1-B2 level, interview-friendly, professional, or daily-life contexts.
8. Avoid repeating the same sentence pattern.
""".strip()