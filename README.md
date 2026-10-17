# Pós-graduação Unicamp

Repositório de atividades de Naomi Pomella. Cada atividade fica em sua própria pasta, com código, dependências, documentação e evidências.

| Atividade | Descrição | Entrega |
| --- | --- | --- |
| [Atividade 01](atividade_01/README.md) | Cadastro de pacientes com Gradio e Streamlit | [Links e evidências](atividade_01/docs/entrega.md) |

Somente a atividade 01 foi implementada até o momento. As próximas atividades serão adicionadas em `atividade_02/`, `atividade_03/` e assim por diante.

## Executar a atividade 01

Python 3.12 em macOS ou Linux. Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m atividade_01.gradio_app.app
```

Streamlit:

```bash
python -m streamlit run atividade_01/app.py
```

O `app.py` e o `requirements.txt` na raiz são atalhos para a atividade 01. Cada atividade mantém seus próprios arquivos dentro da respectiva pasta.

## Testes

```bash
python -m unittest discover -s atividade_01/tests -v
```

Use apenas dados fictícios nesta demonstração acadêmica. Consulte o [README da atividade 01](atividade_01/README.md) para requisitos, comparação entre as bibliotecas e instruções de publicação.
