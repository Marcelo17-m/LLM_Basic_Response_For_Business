"""
main.py
Punto de entrada por consola. Uso:

    python -m src.main
    python -m src.main "¿Cuál fue el producto más vendido en diciembre de 2015?"
"""

import sys

from src.router import ask


def main() -> None:
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(ask(question))
        return

    print("Agente de documentos internos. Escribí 'salir' para terminar.\n")
    while True:
        question = input("Pregunta: ").strip()
        if question.lower() in {"salir", "exit", "quit"}:
            break
        if not question:
            continue
        try:
            answer = ask(question)
        except Exception as exc:  # noqa: BLE001 - queremos mostrarle el error tal cual al usuario
            answer = f"Ocurrió un error al procesar la pregunta: {exc}"
        print(f"Respuesta: {answer}\n")


if __name__ == "__main__":
    main()
