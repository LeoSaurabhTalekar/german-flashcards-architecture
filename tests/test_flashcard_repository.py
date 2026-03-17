from pathlib import Path
from typing import Dict

import pandas as pd
import pytest

from app.core.exceptions import FlashcardNotFoundError, RepositoryError
from app.repositories.flashcard_repository import ExcelFlashcardRepository


def write_excel_file(path: Path, sheets: Dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def test_loads_valid_rows_from_single_excel_file(tmp_path: Path) -> None:
    file_path = tmp_path / "adjectives.xlsx"

    df = pd.DataFrame(
        {
            "German adjective": ["grundlegend", "wichtig"],
            "English word": ["basic", "important"],
            "Meaning (simple)": ["forming the basis", "very useful"],
            "German example sentence": [
                "Ich habe grundlegende Erfahrung.",
                "Das ist ein wichtiger Punkt.",
            ],
            "English example sentence": [
                "I have basic experience.",
                "That is an important point.",
            ],
        }
    )

    write_excel_file(file_path, {"Adjectives_Master": df})

    repository = ExcelFlashcardRepository([file_path])
    result = repository.get_load_result()

    assert len(result.flashcards) == 2
    assert result.stats.files_processed == 1
    assert result.stats.sheets_processed == 1
    assert result.stats.total_rows == 2
    assert result.stats.valid_rows == 2
    assert result.stats.loaded_flashcards == 2
    assert result.stats.duplicates_skipped == 0
    assert result.stats.invalid_rows_skipped == 0

    first = result.flashcards[0]
    assert first.german == "grundlegend"
    assert first.english == "basic"
    assert first.meaning_simple == "forming the basis"
    assert first.german_example == "Ich habe grundlegende Erfahrung."
    assert first.english_example == "I have basic experience."
    assert first.source_file.endswith("adjectives.xlsx")
    assert first.sheet_name == "Adjectives_Master"


def test_loads_multiple_files_and_deduplicates(tmp_path: Path) -> None:
    file1 = tmp_path / "file1.xlsx"
    file2 = tmp_path / "file2.xlsx"

    df1 = pd.DataFrame(
        {
            "German adjective": ["grundlegend", "wichtig"],
            "English word": ["basic", "important"],
        }
    )

    df2 = pd.DataFrame(
        {
            "German adjective": [" Grundlegend ", "neu"],
            "English word": ["Basic", "new"],
        }
    )

    write_excel_file(file1, {"Sheet1": df1})
    write_excel_file(file2, {"Sheet1": df2})

    repository = ExcelFlashcardRepository([file1, file2])
    result = repository.get_load_result()

    assert len(result.flashcards) == 3
    assert result.stats.files_processed == 2
    assert result.stats.sheets_processed == 2
    assert result.stats.total_rows == 4
    assert result.stats.valid_rows == 4
    assert result.stats.loaded_flashcards == 3
    assert result.stats.duplicates_skipped == 1
    assert result.stats.invalid_rows_skipped == 0

    german_words = {card.german for card in result.flashcards}
    assert german_words == {"grundlegend", "wichtig", "neu"}


def test_skips_rows_with_missing_required_values(tmp_path: Path) -> None:
    file_path = tmp_path / "mixed.xlsx"

    df = pd.DataFrame(
        {
            "German adjective": ["grundlegend", None, "klar", ""],
            "English word": ["basic", "empty-german", None, "clear"],
        }
    )

    write_excel_file(file_path, {"Sheet1": df})

    repository = ExcelFlashcardRepository([file_path])
    result = repository.get_load_result()

    assert len(result.flashcards) == 1
    assert result.stats.total_rows == 4
    assert result.stats.valid_rows == 1
    assert result.stats.loaded_flashcards == 1
    assert result.stats.invalid_rows_skipped == 3
    assert result.flashcards[0].german == "grundlegend"
    assert result.flashcards[0].english == "basic"


def test_raises_error_when_required_columns_are_missing(tmp_path: Path) -> None:
    file_path = tmp_path / "broken.xlsx"

    df = pd.DataFrame(
        {
            "German adjective": ["grundlegend", "wichtig"],
            "Meaning (simple)": ["forming the basis", "important"],
        }
    )

    write_excel_file(file_path, {"Sheet1": df})

    repository = ExcelFlashcardRepository([file_path])

    with pytest.raises(RepositoryError, match="Missing required columns"):
        repository.get_load_result()


def test_supports_column_aliases_for_nouns_and_examples(tmp_path: Path) -> None:
    file_path = tmp_path / "nouns.xlsx"

    df = pd.DataFrame(
        {
            "German noun": ["der Tisch"],
            "English": ["table"],
            "German example": ["Der Tisch ist groß."],
            "English example": ["The table is big."],
            "Meaning": ["a piece of furniture"],
        }
    )

    write_excel_file(file_path, {"Nouns_Master": df})

    repository = ExcelFlashcardRepository([file_path])
    result = repository.get_load_result()

    assert len(result.flashcards) == 1
    card = result.flashcards[0]
    assert card.german == "der Tisch"
    assert card.english == "table"
    assert card.german_example == "Der Tisch ist groß."
    assert card.english_example == "The table is big."
    assert card.meaning_simple == "a piece of furniture"


def test_raises_when_no_valid_flashcards_are_found(tmp_path: Path) -> None:
    file_path = tmp_path / "empty_valid.xlsx"

    df = pd.DataFrame(
        {
            "German adjective": [None, ""],
            "English word": [None, ""],
        }
    )

    write_excel_file(file_path, {"Sheet1": df})

    repository = ExcelFlashcardRepository([file_path])

    with pytest.raises(FlashcardNotFoundError, match="No flashcards found"):
        repository.get_load_result()