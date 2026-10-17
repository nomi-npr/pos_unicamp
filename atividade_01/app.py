"""Ponto de entrada para o Streamlit Community Cloud."""

import sys
from pathlib import Path

# O Community Cloud adiciona a pasta deste script ao caminho de importação.
# Incluímos também a raiz do repositório para resolver o pacote da atividade.
RAIZ = str(Path(__file__).resolve().parents[1])
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from atividade_01.streamlit_app.app import main

main()
