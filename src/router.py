

from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI
# En LangChain 1.x, el AgentExecutor "clásico" vive en el paquete de compatibilidad langchain-classic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.config import settings
from src.csv_agent import answer_csv_question
from src.pdf_agent import answer_pdf_question

SYSTEM_PROMPT = """Sos el asistente interno de la empresa. Tu trabajo es responder preguntas de
colaboradores sobre dos fuentes de información:

1. "consultar_datos_csv": datos tabulares (por ejemplo, ventas, métricas, registros).
2. "consultar_documento_pdf": documentación en texto (por ejemplo, políticas internas, manuales,
   documentación técnica).

Elegí la herramienta correcta según de qué trata la pregunta. Si la pregunta no tiene relación
con ninguna de las dos fuentes, decilo con honestidad en vez de inventar una respuesta.
Respondé siempre en el mismo idioma en el que te preguntan.
"""


def _csv_tool_fn(question: str) -> str:
    return answer_csv_question(question)


def _pdf_tool_fn(question: str) -> str:
    return answer_pdf_question(question)


@lru_cache(maxsize=1)
def build_router_agent() -> AgentExecutor:
    """Construye (una sola vez, cacheado) el agente principal con ambas herramientas."""
    settings.validate()

    tools = [
        Tool(
            name="consultar_datos_csv",
            func=_csv_tool_fn,
            description=(
                "Úsala para preguntas sobre datos tabulares/numéricos: ventas, cifras, "
                "totales, promedios, rankings, fechas, filas o columnas de una planilla."
            ),
        ),
        Tool(
            name="consultar_documento_pdf",
            func=_pdf_tool_fn,
            description=(
                "Úsala para preguntas sobre texto narrativo: políticas internas, procedimientos, "
                "manuales o documentación técnica."
            ),
        ),
    ]

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_CHAT_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)


def ask(question: str) -> str:
    """Punto de entrada único: le hacés una pregunta al agente y te devuelve la respuesta."""
    executor = build_router_agent()
    result = executor.invoke({"input": question})
    return result["output"]


if __name__ == "__main__":
    # Prueba rápida por consola: python -m src.router
    print(ask("¿De qué documentos podés responder preguntas?"))
