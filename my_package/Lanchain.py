from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from pathlib import Path
from .Searchquery import export_movie_search, fetch_movie_context_by_title

import os

# Load .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# --------------------------------------------------------
#   ⛔ REMOVED: ChatGoogleGenerativeAI (Gemini)
#   ✅ ADDED: ChatOpenAI (GPT-4o-mini)
# --------------------------------------------------------

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    max_tokens=300,
)

# --------------------------------------------------------
# Prompt template
# --------------------------------------------------------
prompt_template = PromptTemplate(
    input_variables=["history", "context", "question", "last_title"],
    template="""
You are a helpful assistant who understands movie information.

Conversation history:
{history}

Last known movie discussed: {last_title}

Given the following movie data context:
{context}

If the user's question is not related to the context or no answer can be found, respond with:
"I am sorry, I cannot answer the question about [user's topic] based on the context provided."

User's question:
{question}

Be concise and accurate.
"""
)

# Build pipeline
chain = prompt_template | llm


# --------------------------------------------------------
# Helper Functions
# --------------------------------------------------------

def is_related(user_input, last_question, last_answer):
    if not last_question or not last_answer:
        return False
    lw = (last_question + " " + last_answer).lower().split()
    iw = user_input.lower().split()
    return len(set(lw) & set(iw)) > 0


def is_fallback_response(response: str) -> bool:
    if not response:
        return False
    fallback_phrases = [
        "not related to the context",
        "i cannot answer",
        "no relevant information",
        "based on the context provided",
    ]
    R = response.lower()
    return any(p in R for p in fallback_phrases)


def get_last_movie(history):
    for turn in reversed(history):
        if turn.get("title"):
            return turn["title"]
    return ""


def extract_movie_title(context):
    for line in context.split("\n"):
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()
    return ""


# --------------------------------------------------------
# MAIN FUNCTION: Ask Movie Question
# --------------------------------------------------------

def ask_movie_question(user_input: str, session_history: list, retry: bool = False):

    # Context selection logic
    if session_history and is_related(
        user_input, session_history[-1]["question"], session_history[-1]["answer"]
    ):
        context = session_history[-1]["context"]
        last_title = get_last_movie(session_history)

    elif any(x in user_input.lower() for x in ["that movie", "previous movie", "we talked"]):
        last_title = get_last_movie(session_history)
        context = (
            fetch_movie_context_by_title(last_title)
            if last_title
            else export_movie_search(user_input)
        )

    else:
        context = export_movie_search(user_input)
        last_title = extract_movie_title(context)

    # Build formatted history text
    history_text = ""
    for turn in session_history:
        history_text += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    # Run the LLM pipeline
    response = chain.invoke({
        "history": history_text,
        "context": context,
        "question": user_input,
        "last_title": last_title or "None"
    })

    clean_answer = str(response)

    # If fallback / irrelevant → retry once with no history
    if is_fallback_response(clean_answer):
        if not retry:
            return ask_movie_question(user_input, [], retry=True)
        return clean_answer

    # Save turn to history
    session_history.append({
        "question": user_input,
        "answer": clean_answer,
        "context": context,
        "title": last_title
    })

    return clean_answer
