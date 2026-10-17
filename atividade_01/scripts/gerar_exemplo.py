"""Gera a entrega CSV usando a mesma rotina de cadastro das interfaces."""

from pathlib import Path

from atividade_01.cadastro.dados import criar_registro, salvar_registro

DESTINO = Path(__file__).resolve().parents[1] / "exemplos" / "pacientes.csv"
EXEMPLOS = [
    ("Ana Exemplo", 29, "Particular", 1, "Consulta de rotina (dado fictício)"),
    ("Bruno Exemplo", 42, "Unimed", 2, "Retorno (dado fictício)"),
    ("Carla Exemplo", 65, "Bradesco Saúde", 3, "Avaliação (dado fictício)"),
    ("Diego Exemplo", 18, "SulAmérica", 4, "Observação (dado fictício)"),
    ("Eva Exemplo", 35, "Outro", 5, "Urgência simulada (dado fictício)"),
    ("Fábio Exemplo", 51, "Particular", 2, "Acompanhamento (dado fictício)"),
    ("Gabriela Exemplo", 37, "Unimed", 1, "Consulta de rotina (dado fictício)"),
    ("Henrique Exemplo", 73, "Bradesco Saúde", 3, "Retorno de avaliação (dado fictício)"),
    ("Isabela Exemplo", 22, "SulAmérica", 2, "Primeira consulta (dado fictício)"),
    ("João Exemplo", 46, "Outro", 4, "Avaliação simulada (dado fictício)"),
    ("Karina Exemplo", 60, "Unimed", 3, "Acompanhamento periódico (dado fictício)"),
    ("Larissa Exemplo", 24, "Particular", 1, "Consulta de rotina (dado fictício)"),
]

if __name__ == "__main__":
    if DESTINO.exists():
        raise SystemExit(f"O exemplo já existe: {DESTINO}. Remova-o se quiser regenerar.")
    for valores in EXEMPLOS:
        salvar_registro(criar_registro(*valores), DESTINO)
    print(f"CSV de exemplo gerado: {DESTINO}")
