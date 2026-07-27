"""
test_agent.py
Pruebas básicas que no requieren llamar a la API de Gemini (para poder correrlas en CI
sin gastar cuota). Validan la carga de datos y el manejo de errores, no la calidad de
las respuestas del LLM (eso se prueba manualmente, ver README).

Ejecutar con: pytest tests/
"""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.csv_agent import load_dataframe


def test_load_dataframe_reads_existing_csv(tmp_path):
    csv_file = tmp_path / "sample.csv"
    pd.DataFrame({"producto": ["A", "B"], "ventas": [10, 20]}).to_csv(csv_file, index=False)

    df = load_dataframe(str(csv_file))

    assert list(df.columns) == ["producto", "ventas"]
    assert len(df) == 2


def test_load_dataframe_missing_file_raises_clear_error():
    with pytest.raises(FileNotFoundError, match="No se encontró el CSV"):
        load_dataframe("data/no_existe.csv")


def test_settings_validate_requires_api_key(monkeypatch):
    from src.config import Settings

    monkeypatch.setattr(Settings, "GOOGLE_API_KEY", "", raising=False)
    with pytest.raises(EnvironmentError, match="GOOGLE_API_KEY"):
        Settings.validate()
