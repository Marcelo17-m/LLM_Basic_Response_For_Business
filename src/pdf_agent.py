"""
pdf_agent.py
Construye un pipeline de RAG (Retrieval-Augmented Generation) clásico sobre un PDF:

    PDF -> texto -> fragmentos (chunks) -> embeddings -> índice vectorial (FAISS)
    pregunta -> embedding -> fragmentos más relevantes -> LLM redacta la respuesta
"""

import os
from typing import Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# En LangChain 1.x, RetrievalQA vive en el paquete de compatibilidad langchain-classic
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from src.config import settings

PROMPT_TEMPLATE = """Sos un asistente interno que responde preguntas de colaboradores de la empresa
usando ÚNICAMENTE la información del contexto entregado, que proviene de documentos internos.

Reglas:
- Si la respuesta no está en el contexto, decí explícitamente que no la encontraste en los documentos.
- Sé claro, directo y breve.
- Si es útil, citá de qué parte del documento sale la respuesta (por ejemplo, la sección o página).

Contexto:
{context}

Pregunta: {question}

Respuesta:"""


def _build_vectorstore(pdf_path: str, embeddings: GoogleGenerativeAIEmbeddings) -> FAISS:
    """Indexa el PDF si no existe un índice guardado, o lo carga desde disco si ya existe."""
    index_dir = settings.VECTORSTORE_DIR

    if os.path.isdir(index_dir) and os.listdir(index_dir):
        return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"No se encontró el PDF en '{pdf_path}'. Configurá PDF_PATH en tu .env "
            "o colocá el archivo en esa ruta."
        )

    loader = PyPDFLoader(pdf_path)
    raw_docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(raw_docs)

    vectorstore = FAISS.from_documents(chunks, embeddings)
    os.makedirs(index_dir, exist_ok=True)
    vectorstore.save_local(index_dir)
    return vectorstore


def build_pdf_qa_chain(pdf_path: Optional[str] = None) -> RetrievalQA:
    """Devuelve una cadena de RetrievalQA lista para responder preguntas sobre el PDF."""
    settings.validate()
    pdf_path = pdf_path or settings.PDF_PATH

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.GEMINI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
    )
    vectorstore = _build_vectorstore(pdf_path, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": settings.RETRIEVER_TOP_K})

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_CHAT_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0,
    )

    prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return qa_chain


def answer_pdf_question(question: str, pdf_path: Optional[str] = None) -> str:
    """Función de conveniencia: recibe una pregunta en texto plano y devuelve la respuesta."""
    chain = build_pdf_qa_chain(pdf_path)
    result = chain.invoke({"query": question})
    return result["result"]


if __name__ == "__main__":
    # Prueba rápida por consola: python -m src.pdf_agent
    q = "¿De qué trata este documento?"
    print(f"Pregunta: {q}")
    print(f"Respuesta: {answer_pdf_question(q)}")
