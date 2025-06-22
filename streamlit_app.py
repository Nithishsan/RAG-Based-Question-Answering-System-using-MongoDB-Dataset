import streamlit as st
from my_package.Lanchain import ask_movie_question
import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

st.set_page_config(page_title="Movie Q&A", page_icon="🎬")
st.title("🎬 Ask Me About Movies")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

# Show the conversation history
if st.session_state.history:
    st.subheader("Conversation History")
    for turn in st.session_state.history:
        st.markdown(f"**You:** {turn['question']}")
        st.markdown(f"**Assistant:** {turn['answer']}")

# User input
user_input = st.text_input("Ask a question about any movie:")

# Properly check and process new input
if user_input and ("last_question" not in st.session_state or user_input != st.session_state.get("last_question")):
    answer = ask_movie_question(user_input, st.session_state.history)
    st.session_state.history.append({
        "question": user_input,
        "answer": answer
    })
    st.session_state.last_question = user_input
    st.rerun()  # Immediately rerun to display the new answer only via history

# Clear history
if st.button("Clear Conversation"):
    st.session_state.history.clear()
    if "last_question" in st.session_state:
        del st.session_state.last_question
    st.rerun()
