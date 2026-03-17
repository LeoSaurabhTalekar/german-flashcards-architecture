from __future__ import annotations

import os
from typing import List

import openai
from openai import OpenAI
from pydantic import BaseModel, Field

from app.core.config import OPENAI_MODEL, OPENAI_TIMEOUT_SECONDS
from app.core.exceptions import (
    ExampleProviderConfigurationError,
    ExampleProviderError,
)
from app.models.flashcard import Flashcard
from app.models.generated_example import GeneratedExample
from app.providers.base import ExampleProvider


class ExampleItemSchema(BaseModel):
    german: str = Field(description="A natural German example sentence.")
    english: str = Field(description="A natural English translation of the German sentence.")


class ExampleListSchema(BaseModel):
    examples: List[ExampleItemSchema]


class OpenAIExampleProvider(ExampleProvider):
    """
    Generates fresh examples using the OpenAI Responses API with structured outputs.
    """

    def __init__(
        self,
        client: OpenAI | None = None,
        model: str = OPENAI_MODEL,
    ) -> None:
        self.model = model

        if client is not None:
            self.client = client
            return

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ExampleProviderConfigurationError(
                "OPENAI_API_KEY is not set. Add it as an environment variable first."
            )

        self.client = OpenAI(
            api_key=api_key,
            timeout=OPENAI_TIMEOUT_SECONDS,
        )

    def generate_examples(
        self,
        flashcard: Flashcard,
        count: int = 5,
    ) -> List[GeneratedExample]:
        if count <= 0:
            return []

        prompt = self._build_prompt(flashcard=flashcard, count=count)

        try:
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are a German language tutor. "
                            "Generate natural, correct, short-to-medium German example sentences "
                            "with English translations. Keep them useful for interview preparation, "
                            "professional conversation, and daily life."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                text_format=ExampleListSchema,
            )
        except openai.APIConnectionError as exc:
            raise ExampleProviderError(
                "Could not reach the OpenAI API. Check your internet connection and try again."
            ) from exc
        except openai.RateLimitError as exc:
            message = getattr(exc, "message", str(exc))
            raise ExampleProviderError(
                f"OpenAI rate/quota error: {message}"
            ) from exc
        except openai.APIStatusError as exc:
            raise ExampleProviderError(
                f"OpenAI API returned an error (status {exc.status_code})."
            ) from exc
        except openai.APIError as exc:
            raise ExampleProviderError("OpenAI API request failed.") from exc
        except Exception as exc:
            raise ExampleProviderError(
                f"Unexpected error while generating AI examples: {type(exc).__name__}: {exc}"
            ) from exc

        parsed = response.output_parsed
        if parsed is None or not parsed.examples:
            raise ExampleProviderError("OpenAI did not return any examples.")

        return [
            GeneratedExample(
                german=item.german.strip(),
                english=item.english.strip(),
            )
            for item in parsed.examples[:count]
        ]

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
1. Return exactly {count} examples.
2. Each example must include the target word or a natural inflected form.
3. German must sound natural and grammatically correct.
4. English must be a faithful, natural translation.
5. Prefer B1-B2 level, interview-friendly, professional, or daily-life contexts.
6. Avoid repeating the same sentence pattern.
7. Keep the examples useful for speaking practice.
""".strip()