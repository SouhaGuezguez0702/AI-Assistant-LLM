import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "users.db"


class ConversationService:

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    title TEXT,
                    messages_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_conversation(self, username: str, messages: list):
        """Sauvegarde une conversation (liste de messages user/assistant, sans le system prompt)."""

        conversation_messages = [
            m for m in messages if m["role"] in ("user", "assistant")
        ]

        if not conversation_messages:
            return  # rien à sauvegarder

        # Titre = début de la première question de l'utilisateur
        first_question = next(
            (m["content"] for m in conversation_messages if m["role"] == "user"),
            "Conversation"
        )
        title = first_question[:60] + ("..." if len(first_question) > 60 else "")

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO conversations (username, title, messages_json) VALUES (?, ?, ?)",
                (username, title, json.dumps(conversation_messages, ensure_ascii=False))
            )

    def get_conversations(self, username: str) -> list:
        """Retourne l'historique des conversations sauvegardées pour un utilisateur, les plus récentes d'abord."""

        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                "SELECT id, title, messages_json, created_at FROM conversations "
                "WHERE username = ? ORDER BY created_at DESC",
                (username,)
            ).fetchall()

        return [
            {
                "id": row[0],
                "title": row[1],
                "messages": json.loads(row[2]),
                "created_at": row[3]
            }
            for row in rows
        ]

    def delete_conversation(self, conversation_id: int, username: str):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "DELETE FROM conversations WHERE id = ? AND username = ?",
                (conversation_id, username)
            )