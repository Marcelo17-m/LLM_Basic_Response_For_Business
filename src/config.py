"""
config.py
Carga la configuración de la aplicación desde variables de entorno (.env).
Centralizar la configuración aquí evita repetir os.getenv(...) por todo el código
y facilita cambiar de modelo o de documentos sin tocar la lógica del agente.
"""

import os
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env ubicado en la raíz del proyecto
load_dotenv()


class Settings:
    # --- Gemini / LLM ---
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")

    # --- Documentos fuente ---
    CSV_PATH: str = os.getenv("CSV_PATH", "data/sales.csv")
    PDF_PATH: str = os.getenv("PDF_PATH", "data/policies.pdf")

    # --- RAG (fragmentación de texto para el PDF) ---
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    RETRIEVER_TOP_K: int = int(os.getenv("RETRIEVER_TOP_K", "4"))

    # --- Vector store persistido en disco (evita re-indexar el PDF en cada arranque) ---
    VECTORSTORE_DIR: str = os.getenv("VECTORSTORE_DIR", "data/faiss_index")

    @classmethod
    def validate(cls) -> None:
        if not cls.GOOGLE_API_KEY:
            raise EnvironmentError(
                "Falta GOOGLE_API_KEY. Copiá .env.example a .env y agregá tu API key de Gemini "
                "(https://aistudio.google.com/apikey)."
            )


settings = Settings()
