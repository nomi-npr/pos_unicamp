# Pós-graduação Unicamp

Repositório de atividades de Naomi Pomella. Cada atividade fica em sua própria pasta, com código, dependências, documentação e evidências.

| Atividade | Descrição | Entrega |
| --- | --- | --- |
| [Atividade 01](atividade_01/README.md) | Cadastro de pacientes com Gradio e Streamlit | [Links e evidências](atividade_01/docs/entrega.md) |
| [Atividade 02](atividade_02/README.md) | TechFix: ordens de serviço com Gradio, Supabase e Streamlit | [Entrega e verificação](atividade_02/techfix/evidencias/entrega.md) |

App público da atividade 01: [Cadastro de Pacientes](https://nomi-unicamp-atividade-01.streamlit.app/).

Cada entrega mantém seu código e suas dependências na pasta da respectiva atividade. Consulte o documento de entrega de cada uma para o estado da integração e os testes realizados.

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
