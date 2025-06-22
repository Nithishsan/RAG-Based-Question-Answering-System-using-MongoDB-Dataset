from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from pathlib import Path
import os

# Your vector search function (should return relevant movie context as string)
from .Searchquery import export_movie_search

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize Gemini LLM (free model)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

# Prompt template with history
prompt_template = PromptTemplate(
    input_variables=["history", "context", "question"],
    template="""
You are a helpful assistant who understands movie information.

Conversation history:
{history}

Given the following movie data context:
{context}

Answer the user question:
{question}

Be concise and accurate.
"""
)

chain = LLMChain(llm=llm, prompt=prompt_template)

# 
def is_related(user_input, last_question, last_answer):
    """Simple check: if the user input contains keywords from the last Q/A, treat as related."""
    if not last_question or not last_answer:
        return False
    if isinstance(last_answer, dict):
        # Try common keys, fallback to str
        answer_text = last_answer.get("text") or last_answer.get("output") or str(last_answer)
    else:
        answer_text = str(last_answer)
    last_words = set((last_question + " " + answer_text).lower().split())
    input_words = set(user_input.lower().split())
    overlap = last_words & input_words
    return len(overlap) > 0

def ask_movie_question(user_input: str, session_history: list):
    # Determine if the question is related to the previous turn
    if session_history and is_related(user_input, session_history[-1]['question'], session_history[-1]['answer']):
        context = session_history[-1]['context']  # Reuse previous context
    else:
        context = export_movie_search(user_input) # New vector search

    # Format history for prompt
    formatted_history = ""
    for turn in session_history:
        formatted_history += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"

    response = chain.invoke({
        "history": formatted_history.strip(),
        "context": context,
        "question": user_input
    })

    # Store context for potential reuse
    session_history.append({"question": user_input, "answer": response, "context": context})
    return response

# Example usage
if __name__ == "__main__":
    session_history = []
    print("Ask about movies! (Type 'exit' to quit)")
    while True:
        user_question = input("You: ")
        if user_question.lower() == "exit":
            break
        answer = ask_movie_question(user_question, session_history)
        print("\nAssistant:", answer)
