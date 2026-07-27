"""
csv_agent.py
Construye un agente que responde preguntas sobre un archivo CSV usando Pandas.

A diferencia del PDF (texto libre -> RAG), acá los datos son tabulares, así que en vez de
"buscar el fragmento más parecido" dejamos que el LLM escriba y ejecute código Pandas
sobre el DataFrame para calcular la respuesta exacta (sumas, máximos, filtros, agrupaciones, etc).

Todavia esta en desarrollo no se ha probado a fondo
"""

from typing import Optional

import pandas as pd
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import settings

CSV_AGENT_PREFIX = """Sos un analista de datos interno. Respondé preguntas sobre el DataFrame `df`
escribiendo y ejecutando código Pandas. Reglas:
- Basate únicamente en los datos del DataFrame, no inventes valores.
- Si el cálculo requiere varias columnas, revisá primero sus nombres exactos (df.columns).
- Al final, dale al usuario una respuesta en lenguaje natural, clara y directa (no solo el código ni la tabla cruda).
"""


def load_dataframe(csv_path: Optional[str] = None) -> pd.DataFrame:
    csv_path = csv_path or settings.CSV_PATH
    try:
        return pd.read_csv(csv_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"No se encontró el CSV en '{csv_path}'. Configurá CSV_PATH en tu .env "
            "o colocá el archivo en esa ruta."
        ) from exc


def build_csv_agent(csv_path: Optional[str] = None):
    """Devuelve un agente de LangChain que puede razonar y ejecutar Pandas sobre el CSV."""
    settings.validate()
    df = load_dataframe(csv_path)

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_CHAT_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0,
    )

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        prefix=CSV_AGENT_PREFIX,
        verbose=False,
        allow_dangerous_code=True,  # necesario para que el agente ejecute el código Pandas que genera
        agent_type="tool-calling",
    )
    return agent


def answer_csv_question(question: str, csv_path: Optional[str] = None) -> str:
    """Función de conveniencia: recibe una pregunta en texto plano y devuelve la respuesta."""
    agent = build_csv_agent(csv_path)
    result = agent.invoke({"input": question})
    return result["output"]


if __name__ == "__main__":
    # Prueba rápida por consola: python -m src.csv_agent
    q = "¿Cuántas filas y columnas tiene el archivo, y qué representa cada columna?"
    print(f"Pregunta: {q}")
    print(f"Respuesta: {answer_csv_question(q)}")
