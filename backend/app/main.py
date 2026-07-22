from services.chat_service import ChatService
import time


def main():
    assistant = ChatService()

    while True:
        question = input("\nYou: ")

        if question.lower() == "exit":
            break

        start = time.time()

        answer = assistant.ask(question)

        end = time.time()

        print("\nMistral:\n")
        print(answer)

        print(f"\nResponse time: {end-start:.2f} seconds")


if __name__ == "__main__":
    main()