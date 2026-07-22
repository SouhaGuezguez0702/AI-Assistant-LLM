from ollama import chat


class ChatService:
    """
    Service responsible for communicating with Ollama.
    """

    def __init__(self, model_name="mistral"):
        self.model_name = model_name

    def ask(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return its response.
        """

        response = chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.message.content