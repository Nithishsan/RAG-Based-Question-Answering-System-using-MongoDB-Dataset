from my_package.Lanchain import ask_movie_question;

session_history = []
print("Ask about movies! (Type 'exit' to quit)")
while True:
    user_question = input("You: ")
    if user_question.lower() == "exit":
        break
    answer = ask_movie_question(user_question, session_history)
    print("\nAssistant:", answer)
