import os
from io import BytesIO
from typing import List, Tuple

from dotenv import load_dotenv
import streamlit as st

from app.core.exceptions import FlashcardAppError, ExampleProviderError
from app.providers.local_example_provider import LocalTemplateExampleProvider
from app.providers.openai_example_provider import OpenAIExampleProvider
from app.providers.ollama_example_provider import OllamaExampleProvider
from app.repositories.flashcard_repository import ExcelFlashcardRepository
from app.services.example_service import ExampleService
from app.services.flashcard_service import FlashcardService
from app.services.s3_storage_service import S3StorageService

load_dotenv()


class InMemoryUploadedExcelFile(BytesIO):
    """
    Small adapter so downloaded S3 bytes behave enough like Streamlit UploadedFile
    for ExcelFlashcardRepository to process them.
    """

    def __init__(self, file_bytes: bytes, name: str, mime_type: str = "application/vnd.ms-excel"):
        super().__init__(file_bytes)
        self.name = name
        self.type = mime_type
        self.size = len(file_bytes)


def build_example_service(provider_name: str) -> ExampleService:
    if provider_name == "Ollama Local":
        return ExampleService(OllamaExampleProvider())
    if provider_name == "OpenAI API":
        return ExampleService(OpenAIExampleProvider())
    return ExampleService(LocalTemplateExampleProvider())


def build_s3_service(bucket_name: str) -> S3StorageService:
    return S3StorageService(
        bucket_name=bucket_name.strip(),
        region_name=os.getenv("AWS_REGION", "eu-central-1"),
    )


def upload_files_to_s3(uploaded_files, bucket_name: str, prefix: str) -> Tuple[List[str], List[str]]:
    if not bucket_name.strip():
        return [], ["S3 bucket name is empty."]

    try:
        s3_service = build_s3_service(bucket_name)
        return s3_service.upload_streamlit_files(
            uploaded_files=uploaded_files,
            prefix=prefix,
        )
    except Exception as exc:
        return [], [str(exc)]


def load_s3_excel_files(bucket_name: str, selected_keys: List[str]) -> Tuple[List[InMemoryUploadedExcelFile], List[str]]:
    downloaded_files: List[InMemoryUploadedExcelFile] = []
    errors: List[str] = []

    if not bucket_name.strip():
        return [], ["S3 bucket name is empty."]

    try:
        s3_service = build_s3_service(bucket_name)

        for key in selected_keys:
            try:
                file_bytes = s3_service.download_file_bytes(key)
                filename = key.split("/")[-1] or key
                downloaded_files.append(
                    InMemoryUploadedExcelFile(
                        file_bytes=file_bytes,
                        name=filename,
                    )
                )
            except Exception as exc:
                errors.append(f"{key}: {exc}")

    except Exception as exc:
        return [], [str(exc)]

    return downloaded_files, errors


def load_flashcards_from_files(file_objects):
    repository = ExcelFlashcardRepository(file_objects)
    flashcard_service = FlashcardService(repository)
    return flashcard_service.load_flashcards()


def reset_flashcard_state(load_result):
    st.session_state.flashcards = load_result.flashcards
    st.session_state.load_stats = load_result.stats
    st.session_state.current_card = FlashcardService.select_random_flashcard(
        load_result.flashcards
    )
    st.session_state.show_answer = False
    st.session_state.show_stored_example = False
    st.session_state.generated_examples = []


def show_flashcard_ui():
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

    st.caption(f"Processed {stats.total_rows} row(s), {stats.valid_rows} valid row(s).")

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


st.set_page_config(page_title="German Flashcards", layout="centered")
st.title("German Flashcards App")
st.write("Practice from local Excel uploads or files stored in AWS S3.")

# ---------------------------------
# Sidebar: AWS S3 config
# ---------------------------------
st.sidebar.header("AWS S3")

default_bucket_name = os.getenv("S3_BUCKET_NAME", "")
s3_bucket_name = st.sidebar.text_input(
    "S3 bucket name",
    value=default_bucket_name,
)

s3_prefix = st.sidebar.text_input(
    "S3 folder prefix",
    value="uploads/",
)

data_source = st.radio(
    "Choose data source",
    options=["Local Upload", "S3 Bucket"],
    horizontal=True,
)

# Initialize shared session state holders
st.session_state.setdefault("s3_uploaded_keys", [])
st.session_state.setdefault("s3_upload_errors", [])
st.session_state.setdefault("s3_download_errors", [])
st.session_state.setdefault("s3_available_keys", [])
st.session_state.setdefault("flashcards", None)
st.session_state.setdefault("load_stats", None)
st.session_state.setdefault("current_card", None)
st.session_state.setdefault("show_answer", False)
st.session_state.setdefault("show_stored_example", False)
st.session_state.setdefault("generated_examples", [])

# ---------------------------------
# Local Upload Mode
# ---------------------------------
if data_source == "Local Upload":
    uploaded_files = st.file_uploader(
        "Select Excel file(s)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
    )

    enable_s3_upload = st.checkbox("Also upload selected files to S3", value=False)

    if not uploaded_files:
        st.info("Please upload one or more Excel files to begin.")
    else:
        file_signature = tuple(sorted((file.name, file.size) for file in uploaded_files))
        upload_signature = (enable_s3_upload, s3_bucket_name, s3_prefix)

        if (
            st.session_state.get("local_file_signature") != file_signature
            or st.session_state.get("local_upload_signature") != upload_signature
        ):
            try:
                st.session_state.s3_uploaded_keys = []
                st.session_state.s3_upload_errors = []

                if enable_s3_upload:
                    uploaded_keys, upload_errors = upload_files_to_s3(
                        uploaded_files=uploaded_files,
                        bucket_name=s3_bucket_name,
                        prefix=s3_prefix,
                    )
                    st.session_state.s3_uploaded_keys = uploaded_keys
                    st.session_state.s3_upload_errors = upload_errors

                load_result = load_flashcards_from_files(uploaded_files)
                reset_flashcard_state(load_result)

                st.session_state.local_file_signature = file_signature
                st.session_state.local_upload_signature = upload_signature

            except FlashcardAppError as exc:
                st.error(str(exc))

        uploaded_keys = st.session_state.get("s3_uploaded_keys", [])
        upload_errors = st.session_state.get("s3_upload_errors", [])

        if enable_s3_upload:
            st.markdown("### S3 Upload Status")

            if uploaded_keys:
                st.success(f"{len(uploaded_keys)} file(s) uploaded to S3.")
                for key in uploaded_keys:
                    st.caption(f"S3 object: {key}")

            if upload_errors:
                st.error("Some S3 uploads failed.")
                for error_message in upload_errors:
                    st.caption(error_message)

# ---------------------------------
# S3 Bucket Mode
# ---------------------------------
else:
    refresh_list = st.button("Refresh S3 File List")

    if s3_bucket_name.strip():
        if refresh_list or not st.session_state.get("s3_available_keys"):
            try:
                s3_service = build_s3_service(s3_bucket_name)
                st.session_state.s3_available_keys = s3_service.list_excel_files(prefix=s3_prefix)
            except Exception as exc:
                st.error(f"Could not list S3 files: {exc}")
                st.session_state.s3_available_keys = []
    else:
        st.info("Enter your S3 bucket name to browse files.")

    available_keys = st.session_state.get("s3_available_keys", [])

    if available_keys:
        selected_keys = st.multiselect(
            "Select Excel file(s) from S3",
            options=available_keys,
        )

        if st.button("Load Selected S3 Files"):
            downloaded_files, download_errors = load_s3_excel_files(
                bucket_name=s3_bucket_name,
                selected_keys=selected_keys,
            )
            st.session_state.s3_download_errors = download_errors

            if downloaded_files:
                try:
                    load_result = load_flashcards_from_files(downloaded_files)
                    reset_flashcard_state(load_result)
                    st.success(f"Loaded {len(downloaded_files)} file(s) from S3.")
                except FlashcardAppError as exc:
                    st.error(str(exc))
            elif not download_errors:
                st.warning("Please select at least one S3 file.")

        download_errors = st.session_state.get("s3_download_errors", [])
        if download_errors:
            st.error("Some S3 downloads failed.")
            for error_message in download_errors:
                st.caption(error_message)
    elif s3_bucket_name.strip():
        st.info("No Excel files found in the selected bucket/prefix.")

# ---------------------------------
# Flashcard UI
# ---------------------------------
if st.session_state.get("flashcards"):
    show_flashcard_ui()