"""Validação e persistência CSV compartilhadas pelas duas interfaces."""

import csv
import fcntl
import math
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

COLUNAS = ["timestamp", "nome", "idade", "convenio", "prioridade", "motivo"]
CONVENIOS = ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"]


def inteiro_no_intervalo(valor, minimo, maximo, campo):
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{campo}: informe um número inteiro de {minimo} a {maximo}.") from None
    if isinstance(valor, bool) or not math.isfinite(numero) or not numero.is_integer() or not minimo <= numero <= maximo:
        raise ValueError(f"{campo}: informe um número inteiro de {minimo} a {maximo}.")
    return int(numero)


def criar_registro(nome, idade, convenio, prioridade, motivo):
    nome = (nome or "").strip()
    if not nome:
        raise ValueError("Informe o nome do paciente.")
    if convenio not in CONVENIOS:
        raise ValueError("Selecione um convênio válido.")
    return {
        "timestamp": datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome,
        "idade": inteiro_no_intervalo(idade, 0, 120, "Idade"),
        "convenio": convenio,
        "prioridade": inteiro_no_intervalo(prioridade, 1, 5, "Prioridade"),
        "motivo": (motivo or "").strip(),
    }


def salvar_registro(registro, arquivo):
    """Acrescenta uma linha, criando cabeçalho só no primeiro envio.

    O bloqueio do arquivo evita cabeçalhos duplicados e linhas intercaladas
    quando há cadastros simultâneos (macOS/Linux, incluindo Community Cloud).
    """
    arquivo = Path(arquivo)
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    with arquivo.open("a+", encoding="utf-8", newline="") as destino:
        fcntl.flock(destino, fcntl.LOCK_EX)
        destino.seek(0)
        cabecalho = next(csv.reader(destino), None)
        if cabecalho is not None and cabecalho != COLUNAS:
            raise ValueError("O CSV existente tem um cabeçalho incompatível.")
        destino.seek(0, 2)
        escritor = csv.DictWriter(destino, fieldnames=COLUNAS)
        if cabecalho is None:
            escritor.writeheader()
        escritor.writerow(registro)
        destino.flush()


def ler_registros(arquivo):
    arquivo = Path(arquivo)
    if not arquivo.exists() or arquivo.stat().st_size == 0:
        return pd.DataFrame(columns=COLUNAS)
    with arquivo.open(encoding="utf-8", newline="") as origem:
        fcntl.flock(origem, fcntl.LOCK_SH)
        return pd.read_csv(origem, keep_default_na=False)


def exportar_csv(tabela):
    return tabela.to_csv(index=False).encode("utf-8-sig")
