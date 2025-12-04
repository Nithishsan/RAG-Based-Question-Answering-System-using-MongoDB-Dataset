import streamlit as st
from my_package.Lanchain import ask_movie_question
import os
import re

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# ----------------------------------
# PAGE CONFIG - Netflix Theme
# ----------------------------------
st.set_page_config(
    page_title="Movie Explorer AI",
    page_icon="🍿",
    layout="wide"
)

# ----------------------------------
# NETFLIX STYLE CSS
# ----------------------------------
st.markdown("""
<style>

body {
    background-color: #141414;
    color: #ffffff;
}

/* Chat bubbles */
.chat-user {
    background: #E50914;
    color: white;
    padding: 14px;
    border-radius: 10px;
    margin: 10px 0;
    max-width: 75%;
    font-weight: 500;
}

.chat-ai {
    background: #333333;
    color: white;
    padding: 14px;
    border-radius: 10px;
    margin: 10px 0;
    max-width: 75%;
    border-left: 4px solid #E50914;
}

/* Movie Card */
.movie-card {
    background-color: #1b1b1b;
    padding: 18px;
    border-radius: 12px;
    margin-top: 18px;
    border: 1px solid #333;
    transition: 0.2s;
}

.movie-card:hover {
    transform: scale(1.01);
    border-color: #E50914;
}

/* Headers */
.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #E50914;
    margin-top: 20px;
}

.movie-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
}

/* Bullet styling */
ul {
    margin-left: 1rem;
}

li {
    margin-bottom: 6px;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------
# HEADER
# ----------------------------------
st.markdown("<h1 class='section-title'>🍿 Movie Explorer AI</h1>", unsafe_allow_html=True)
st.write("Your AI-powered movie assistant — Cinematic-style UI, cleaner details, and cinematic vibes.")


# ----------------------------------
# Extract Movie Blocks
# ----------------------------------
def extract_movie_blocks(raw):
    blocks = raw.split("Movie ID:")
    results = []

    for block in blocks[1:]:
        entry = {"Movie ID": None}

        entry["Movie ID"] = re.search(r"(\w+)", block).group(1) if re.search(r"(\w+)", block) else None
        entry["Score"] = re.search(r"Score:\s*([\d\.]+)", block)
        entry["Score"] = entry["Score"].group(1) if entry["Score"] else None

        fields = {
            "Title": r"Title:\s*(.+)",
            "Plot": r"Plot:\s*(.+)",
            "Full Plot": r"Full Plot:\s*(.+?)(?=Last Updated:|Type:|Awards:|IMDb|Released:|$)",
            "Genres": r"Genres:\s*(.+)",
            "Cast": r"Cast:\s*(.+)",
            "IMDb Rating": r"IMDb Rating:\s*([\d\.]+)",
            "IMDb Votes": r"IMDb Votes:\s*(\d+)",
            "Awards": r"Awards:\s*(.+)",
            "Released": r"Released:\s*(.+)",
            "Year": r"Year:\s*(\d+)",
            "Countries": r"Countries:\s*(.+)",
            "Languages": r"Languages:\s*(.+)",
            "Tomatoes Viewer Rating": r"Tomatoes Viewer Rating:\s*([\d\.]+)",
        }

        for label, pattern in fields.items():
            m = re.search(pattern, block, flags=re.DOTALL)
            entry[label] = m.group(1).strip() if m else None

        results.append(entry)

    return results


# ----------------------------------
# SESSION STATE
# ----------------------------------
if "history" not in st.session_state:
    st.session_state.history = []


# ----------------------------------
# DISPLAY CHAT + MOVIE BLOCKS
# ----------------------------------
for turn in st.session_state.history:

    # User bubble
    st.markdown(f"<div class='chat-user'>🧑‍💬 {turn['question']}</div>", unsafe_allow_html=True)

    # AI bubble
    st.markdown(f"<div class='chat-ai'>🤖 {turn['answer']}</div>", unsafe_allow_html=True)

    movie_blocks = extract_movie_blocks(turn["context"])

    st.markdown("<h2 class='section-title'>🎞 Related Movies</h2>", unsafe_allow_html=True)

    for idx, movie in enumerate(movie_blocks, start=1):

        with st.container():
            st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

            st.markdown(f"<div class='movie-title'>#{idx}: {movie.get('Title','Unknown Movie')}</div>", unsafe_allow_html=True)

            bullet_list = "<ul>"
            for label, value in movie.items():
                if value and label != "Title":
                    bullet_list += f"<li><b>{label}:</b> {value}</li>"
            bullet_list += "</ul>"

            st.markdown(bullet_list, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------
# User Input (Chat bar)
# ----------------------------------
user_input = st.chat_input("Search for a movie…")

if user_input:
    answer = ask_movie_question(user_input, st.session_state.history)
    context = st.session_state.history[-1]["context"] if st.session_state.history else ""

    st.session_state.history.append({
        "question": user_input,
        "answer": answer,
        "context": context,
    })

    st.rerun()


# ----------------------------------
# CLEAR CHAT
# ----------------------------------
if st.button("Clear Chat"):
    st.session_state.history.clear()
    st.rerun()
