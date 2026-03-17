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

try:
    repository = ExcelFlashcardRepository(uploaded_files)
    service = FlashcardService(repository)
    flashcards = service.list_flashcards()
except FlashcardAppError as exc:
    st.error(str(exc))
    st.stop()

file_signature = tuple((file.name, file.size) for file in uploaded_files)

if "file_signature" not in st.session_state or st.session_state.file_signature != file_signature:
    st.session_state.file_signature = file_signature
    st.session_state.current_card = service.get_random_flashcard()
    st.session_state.show_answer = False
    st.session_state.show_example = False

st.success(f"Loaded {len(flashcards)} flashcards from {len(uploaded_files)} file(s).")

if st.button("Next Random Word"):
    st.session_state.current_card = service.get_random_flashcard()
    st.session_state.show_answer = False
    st.session_state.show_example = False

card = st.session_state.current_card

st.subheader("German Word")
st.write(card.german)

if card.meaning_simple:
    st.caption(f"Meaning hint: {card.meaning_simple}")

col1, col2 = st.columns(2)

with col1:
    if st.button("Show Answer"):
        st.session_state.show_answer = True

with col2:
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