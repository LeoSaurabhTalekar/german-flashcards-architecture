import streamlit as st

from app.core.exceptions import FlashcardAppError
from app.repositories.flashcard_repository import ExcelFlashcardRepository
from app.services.flashcard_service import FlashcardService


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
        service = FlashcardService(repository)
        load_result = service.load_flashcards()
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
    st.session_state.show_example = False

flashcards = st.session_state.flashcards
stats = st.session_state.load_stats

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
    st.session_state.show_example = False

card = st.session_state.current_card

st.subheader("German Word")
st.write(card.german)

if card.meaning_simple:
    st.caption(f"Meaning hint: {card.meaning_simple}")

button_col1, button_col2 = st.columns(2)

with button_col1:
    if st.button("Show Answer"):
        st.session_state.show_answer = True

with button_col2:
    if st.button("Show Example"):
        st.session_state.show_example = True

if st.session_state.show_answer:
    st.write(f"**English:** {card.english}")

if st.session_state.show_example:
    if card.german_example:
        st.write(f"**German Example:** {card.german_example}")
    if card.english_example:
        st.write(f"**English Example:** {card.english_example}")

st.caption(f"Source file: {card.source_file} | Sheet: {card.sheet_name}")