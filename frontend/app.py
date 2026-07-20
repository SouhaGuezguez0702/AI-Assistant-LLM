from ollama import chat


class ChatService:
    def ask(self, prompt: str) -> str:
        response = chat(
            model="mistral",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.message.content