from services.chat_service import ChatService

assistant = ChatService()

question = input("You: ")

answer = assistant.ask(question)

print("\nMistral:\n")
print(answer)