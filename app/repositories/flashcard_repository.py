from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, List, Sequence, Union

import pandas as pd

from app.core.exceptions import FlashcardNotFoundError, RepositoryError
from app.models.flashcard import Flashcard


ExcelSource = Union[str, Path, BinaryIO]


class FlashcardRepository(ABC):
    @abstractmethod
    def get_all_flashcards(self) -> List[Flashcard]:
        """Return all flashcards."""


class ExcelFlashcardRepository(FlashcardRepository):
    COLUMN_ALIASES = {
        "german": [
            "German adjective",
            "German word",
            "German",
            "Deutsch",
            "Wort",
        ],
        "english": [
            "English word",
            "English",
            "Englisch",
        ],
        "meaning_simple": [
            "Meaning (simple)",
            "Meaning",
            "Simple meaning",
        ],
        "german_example": [
            "German example sentence",
            "German example",
            "Example sentence",
            "Beispielsatz",
        ],
        "english_example": [
            "English example sentence",
            "English example",
            "Example translation",
        ],
    }

    REQUIRED_COLUMNS = ["german", "english"]

    def __init__(self, sources: Sequence[ExcelSource]) -> None:
        self.sources = list(sources)

    def get_all_flashcards(self) -> List[Flashcard]:
        flashcards: List[Flashcard] = []

        for source in self.sources:
            source_name = getattr(source, "name", str(source))

            try:
                if hasattr(source, "seek"):
                    source.seek(0)

                workbook = pd.read_excel(
                    source,
                    sheet_name=None,
                    engine="openpyxl",
                )
            except Exception as exc:
                raise RepositoryError(f"Could not read Excel file: {source_name}") from exc

            for sheet_name, df in workbook.items():
                normalized_df = self._normalize_dataframe(df, source_name, sheet_name)

                for _, row in normalized_df.iterrows():
                    german = self._clean_value(row.get("german"))
                    english = self._clean_value(row.get("english"))

                    if not german or not english:
                        continue

                    flashcards.append(
                        Flashcard(
                            german=german,
                            english=english,
                            meaning_simple=self._clean_value(row.get("meaning_simple")),
                            german_example=self._clean_value(row.get("german_example")),
                            english_example=self._clean_value(row.get("english_example")),
                            source_file=source_name,
                            sheet_name=sheet_name,
                        )
                    )

        if not flashcards:
            raise FlashcardNotFoundError("No flashcards found in the selected Excel file(s).")

        return flashcards

    def _normalize_dataframe(
        self,
        df: pd.DataFrame,
        source_name: str,
        sheet_name: str,
    ) -> pd.DataFrame:
        rename_map = {}

        for logical_name, aliases in self.COLUMN_ALIASES.items():
            match = self._find_matching_column(df.columns, aliases)
            if match is not None:
                rename_map[match] = logical_name

        normalized_df = df.rename(columns=rename_map)

        missing = [col for col in self.REQUIRED_COLUMNS if col not in normalized_df.columns]
        if missing:
            raise RepositoryError(
                f"Missing required columns {missing} in file '{source_name}', sheet '{sheet_name}'."
            )

        return normalized_df

    @staticmethod
    def _find_matching_column(columns, aliases):
        alias_lookup = {alias.strip().lower() for alias in aliases}
        for column in columns:
            if str(column).strip().lower() in alias_lookup:
                return column
        return None

    @staticmethod
    def _clean_value(value) -> str | None:
        if pd.isna(value):
            return None
        text = str(value).strip()
        return text if text else None