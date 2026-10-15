from backend.app.services.chat_service import ChatService
assistant = ChatService()

questions = [
    "hello",
    "What are the symptoms of hyperglycemia?",
    "Comment le prévenir ?",  # question de suivi, teste l'historique
]

for question in questions:
    print(f"\n{'='*60}")
    print("Question:", question)
    print("\nGenerating answer...\n")

    answer = assistant.ask(question)

    print("Mistral:")
    print(answer)