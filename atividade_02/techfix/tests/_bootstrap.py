"""Permite executar os mesmos testes no repositório e no ZIP independente."""

import sys
from pathlib import Path

PASTA_PAI = str(Path(__file__).resolve().parents[2])
if PASTA_PAI not in sys.path:
    sys.path.insert(0, PASTA_PAI)
