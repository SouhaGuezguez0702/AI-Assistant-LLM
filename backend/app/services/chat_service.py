from ollama import chat
from backend.app.services.rag_service import RAGService


class ChatService:

    GREETING_PATTERNS = {
        "hello", "hi", "hey", "salut", "bonjour", "bonsoir",
        "merci", "thanks", "thank you", "ok", "d'accord", "bye",
        "au revoir", "ça va", "cv"
    }

    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        self.rag = RAGService()
        self.max_history_turns = 3

    def _is_health_question(self, question: str) -> bool:
        cleaned = question.strip().lower().strip("!?.,")
        if len(cleaned.split()) <= 3 and cleaned in self.GREETING_PATTERNS:
            return False
        return True

    def _build_search_query(self, question: str, history: list) -> str:
        last_user_question = None
        for message in reversed(history):
            if message["role"] == "user":
                last_user_question = message["content"]
                break

        if last_user_question:
            return f"{last_user_question} {question}"

        return question

    def _build_grounded_prompt(self, question: str, context: str) -> str:
        return f"""Tu es un assistant d'information santé.

Réponds à la question en te basant PRINCIPALEMENT sur les informations
médicales ci-dessous. Tu peux compléter avec tes connaissances générales
en santé si c'est utile, mais ne contredis jamais le contexte fourni.

Règles :
- Ne pas diagnostiquer.
- Pour toute situation médicale personnelle, recommander de consulter un professionnel de santé.
- Réponse claire, concise, dans la même langue que la question de l'utilisateur.
- Ne pas mentionner "le contexte" ou "les documents fournis".

INFORMATIONS MÉDICALES :
{context}

QUESTION :
{question}

RÉPONSE :
"""

    def _build_general_prompt(self, question: str) -> str:
        return f"""Tu es un assistant d'information santé généraliste.

Aucune information spécifique n'a été trouvée dans la base documentaire
pour cette question. Réponds avec tes connaissances générales en santé,
de façon prudente et factuelle.

Règles :
- Précise brièvement que cette réponse n'est pas basée sur un document vérifié.
- Ne pas diagnostiquer, recommander de consulter un professionnel pour tout cas personnel.
- Réponse dans la même langue que la question.

QUESTION :
{question}

RÉPONSE :
"""

    def _build_casual_prompt(self, question: str) -> str:
        return f"""Tu es un assistant d'information santé, amical et concis.

L'utilisateur envoie un message de politesse ou une salutation, pas une
question médicale. Réponds brièvement et naturellement, sans disclaimer
médical, dans la même langue que le message.

MESSAGE :
{question}

RÉPONSE :
"""

    def ask(self, question: str, history: list = None) -> str:
        if history is None:
            history = []

        if not self._is_health_question(question):
            prompt = self._build_casual_prompt(question)
        else:
            search_query = self._build_search_query(question, history)
            documents = self.rag.search(search_query, k=4)

            if documents:
                context = "\n\n".join(d.page_content for d in documents)
                prompt = self._build_grounded_prompt(question, context)
            else:
                prompt = self._build_general_prompt(question)

        max_messages = self.max_history_turns * 2
        recent_history = history[-max_messages:]

        messages = list(recent_history)
        messages.append({"role": "user", "content": prompt})

        response = chat(
            model=self.model_name,
            messages=messages
        )

        return response.message.content