from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from pathlib import Path
import os

# Your vector search function (should return relevant movie context as string)
from .Searchquery import export_movie_search, fetch_movie_context_by_title  # Add fetch_movie_context_by_title

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize Gemini LLM (free model)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

# Prompt template with history and last title
prompt_template = PromptTemplate(
    input_variables=["history", "context", "question", "last_title"],
    template="""
You are a helpful assistant who understands movie information.

Conversation history:
{history}

Last known movie discussed: {last_title}

Given the following movie data context:
{context}

If the user's question is **not related** to the context or you cannot find a relevant answer, respond with:
"I am sorry, I cannot answer the question about [user's topic] based on the context provided."

Otherwise, answer the user's question concisely and accurately.

User's question:
{question}

Be concise and accurate.
"""
)

chain = LLMChain(llm=llm, prompt=prompt_template)

# Utilities

def is_related(user_input, last_question, last_answer):
    if not last_question or not last_answer:
        return False
    if isinstance(last_answer, dict):
        answer_text = last_answer.get("text") or last_answer.get("output") or str(last_answer)
    else:
        answer_text = str(last_answer)
    last_words = set((last_question + " " + answer_text).lower().split())
    input_words = set(user_input.lower().split())
    overlap = last_words & input_words
    return len(overlap) > 0

def is_fallback_response(response: str) -> bool:
    fallback_phrases = [
        "i cannot answer",
        "not related to the context",
        "no relevant information",
        "based on the context provided"
    ]
    return any(phrase in response.lower() for phrase in fallback_phrases)

def get_last_movie(session_history: list) -> str:
    for turn in reversed(session_history):
        if "title" in turn:
            return turn["title"]
    return ""

def extract_movie_title(context: str) -> str:
    # This is a basic extractor. You may replace it with regex/NLP logic.
    for line in context.split("\n"):
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()
    return ""

# Core function
def ask_movie_question(user_input: str, session_history: list, retry: bool = False):
    # Determine context
    if session_history and is_related(user_input, session_history[-1]['question'], session_history[-1]['answer']):
        context = session_history[-1].get('context', '')
        last_title = get_last_movie(session_history)
    elif any(x in user_input.lower() for x in ["that movie", "we talked", "we discussed", "previous movie", "these movie"]):
        last_title = get_last_movie(session_history)
        if last_title:
            context = fetch_movie_context_by_title(last_title)
        else:
            context = export_movie_search(user_input)
    else:
        context = export_movie_search(user_input)
        last_title = extract_movie_title(context)

    formatted_history = ""
    for turn in session_history:
        formatted_history += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    response = chain.invoke({
        "history": formatted_history.strip(),
        "context": context,
        "question": user_input,
        "last_title": last_title or "None"
    })

    clean_answer = response.get("text") if isinstance(response, dict) else str(response)

    if is_fallback_response(clean_answer):
        if not retry:
            return ask_movie_question(user_input, [], retry=True)
        else:
            return clean_answer
    else:
        session_history.append({
            "question": user_input,
            "answer": clean_answer,
            "context": context,
            "title": last_title
        })
        return clean_answer

# Example usage
# if __name__ == "__main__":
#     session_history = []
#     print("Ask about movies! (Type 'exit' to quit)")
#     while True:
#         user_question = input("You: ")
#         if user_question.lower() == "exit":
#             break
#         answer = ask_movie_question(user_question, session_history)
#         print("\nAssistant:", answer)
