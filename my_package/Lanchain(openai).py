from langchain.prompts import PromptTemplate
# from langchain.llms import OpenAI
from langchain_community.llms import OpenAI

from dotenv import load_dotenv
from pathlib import Path
from langchain.chains import LLMChain
from .Searchquery import export_movie_search

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
# Your vector search function (already returns movie info in formatted style)

# Step 1: Create the prompt
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant who understands movie information.

Given the following movie data context:

{context}

Answer the user question:
{question}

Be concise and accurate.
"""
)

# Step 2: Initialize LLM
llm = OpenAI(temperature=0.5)  # You can use ChatOpenAI or other LLMs too

# Step 3: Build the LangChain
chain = LLMChain(llm=llm, prompt=prompt_template)

# Step 4: Create an action function
def ask_movie_question(user_input: str):
    context = export_movie_search(user_input)
    response = chain.run({"context": context, "question": user_input})
    return response

# Example usage
if __name__ == "__main__":
    user_question = input("Ask about a movie: ")
    answer = ask_movie_question(user_question)
    print("\nAnswer:\n", answer)  