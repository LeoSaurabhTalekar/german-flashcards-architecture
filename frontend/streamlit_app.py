import streamlit as st

st.set_page_config(
    page_title="German Flashcards App",
    page_icon="📘",
    layout="centered"
)

st.title("German Flashcards App")
st.subheader("Day 1 Setup")
st.write("The frontend is running successfully.")

st.markdown("### Project Goal")
st.write(
    "This app will help users practice German vocabulary while demonstrating "
    "software architecture and system design concepts such as modularity, "
    "API design, database integration, Docker, and cloud readiness."
)

st.markdown("### Day 1 Status")
st.success("Frontend initialized")