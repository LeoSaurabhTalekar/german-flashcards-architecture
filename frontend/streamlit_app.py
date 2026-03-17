import streamlit as st

from app.core.exceptions import FlashcardAppError, ExampleProviderError
from app.providers.local_example_provider import LocalTemplateExampleProvider
from app.providers.openai_example_provider import OpenAIExampleProvider
from app.providers.ollama_example_provider import OllamaExampleProvider
from app.repositories.flashcard_repository import ExcelFlashcardRepository
from app.services.example_service import ExampleService
from app.services.flashcard_service import FlashcardService


def build_example_service(provider_name: str) -> ExampleService:
    if provider_name == "Ollama Local":
        return ExampleService(OllamaExampleProvider())
    if provider_name == "OpenAI API":
        return ExampleService(OpenAIExampleProvider())
    return ExampleService(LocalTemplateExampleProvider())


st.set_page_config(page_title="German Flashcards", layout="centered")
st.title("German Flashcards App")
st.write("Upload one or more Excel files and practice randomly.")

uploaded_files = st.file_uploader(
    "Select Excel file(s)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
)

if not uploaded_files:
    st.info("Please upload one or more Excel files to begin.")
    st.stop()

file_signature = tuple(sorted((file.name, file.size) for file in uploaded_files))

if st.session_state.get("file_signature") != file_signature:
    try:
        repository = ExcelFlashcardRepository(uploaded_files)
        flashcard_service = FlashcardService(repository)
        load_result = flashcard_service.load_flashcards()
    except FlashcardAppError as exc:
        st.error(str(exc))
        st.stop()

    st.session_state.file_signature = file_signature
    st.session_state.flashcards = load_result.flashcards
    st.session_state.load_stats = load_result.stats
    st.session_state.current_card = FlashcardService.select_random_flashcard(
        load_result.flashcards
    )
    st.session_state.show_answer = False
    st.session_state.show_stored_example = False
    st.session_state.generated_examples = []

flashcards = st.session_state.flashcards
stats = st.session_state.load_stats
card = st.session_state.current_card

provider_name = st.selectbox(
    "Example generator",
    options=["Local Template", "Ollama Local", "OpenAI API"],
    index=1,
    help="Use Local Template for offline examples or OpenAI API for fresh AI-generated examples.",
)

st.success(
    f"Loaded {stats.loaded_flashcards} flashcards from {stats.files_processed} file(s)."
)

col1, col2, col3 = st.columns(3)
col1.metric("Sheets", stats.sheets_processed)
col2.metric("Duplicates skipped", stats.duplicates_skipped)
col3.metric("Invalid rows skipped", stats.invalid_rows_skipped)

st.caption(
    f"Processed {stats.total_rows} row(s), {stats.valid_rows} valid row(s)."
)

if st.button("Next Random Word"):
    st.session_state.current_card = FlashcardService.select_random_flashcard(flashcards)
    st.session_state.show_answer = False
    st.session_state.show_stored_example = False
    st.session_state.generated_examples = []
    card = st.session_state.current_card

st.subheader("German Word")
st.write(card.german)

if card.meaning_simple:
    st.caption(f"Meaning hint: {card.meaning_simple}")

button_col1, button_col2, button_col3 = st.columns(3)

with button_col1:
    if st.button("Show Answer"):
        st.session_state.show_answer = True

with button_col2:
    if st.button("Show Stored Example"):
        st.session_state.show_stored_example = True

with button_col3:
    if st.button("Generate 5 New Examples"):
        try:
            example_service = build_example_service(provider_name)
            st.session_state.generated_examples = example_service.get_examples_for_flashcard(
                card,
                count=5,
            )
        except ExampleProviderError as exc:
            st.error(str(exc))
            st.exception(exc)
            st.session_state.generated_examples = []

if st.session_state.show_answer:
    st.write(f"**English:** {card.english}")

if st.session_state.show_stored_example:
    st.markdown("**Stored Example**")
    has_stored_example = False

    if card.german_example:
        st.write(f"**German Example:** {card.german_example}")
        has_stored_example = True

    if card.english_example:
        st.write(f"**English Example:** {card.english_example}")
        has_stored_example = True

    if not has_stored_example:
        st.info("No stored example is available for this flashcard.")

generated_examples = st.session_state.get("generated_examples", [])

if generated_examples:
    st.markdown("**Generated Examples**")
    st.caption(f"Source: {provider_name}")

    for index, example in enumerate(generated_examples, start=1):
        st.write(f"{index}. {example.german}")
        st.caption(example.english)

st.caption(f"Source file: {card.source_file} | Sheet: {card.sheet_name}")