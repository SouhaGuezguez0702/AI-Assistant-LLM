import sqlite3
import hashlib
from pathlib import Path
from backend.app.services.conversation_service import ConversationService

conversation_service = ConversationService()
DB_PATH = Path(__file__).resolve().parents[3] / "data" / "users.db"


class AuthService:

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> tuple[bool, str]:
        username = username.strip()

        if not username or not password:
            return False, "Nom d'utilisateur et mot de passe requis."

        if len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caractères."

        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, self._hash_password(password))
                )
            return True, "Compte créé avec succès."
        except sqlite3.IntegrityError:
            return False, "Ce nom d'utilisateur existe déjà."

    def check_credentials(self, username: str, password: str) -> bool:
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if row is None:
            return False

        return row[0] == self._hash_password(password)