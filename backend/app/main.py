from fastapi import FastAPI
from backend.app.api.chat import router


app = FastAPI(
    title="AI Assistant API",
    description="Backend API using Ollama and Mistral 7B",
    version="1.0.0"
)


app.include_router(router)