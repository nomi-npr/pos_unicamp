# Atividade Aula 1 · Gradio × Streamlit

Cadastro de pacientes para a disciplina Aplicações em Data Science, implementado em duas interfaces Python. Autora: Naomi Pomella.

As duas versões coletam nome, idade, convênio, prioridade de 1 a 5 (5 = urgente) e motivo/observações. Cada cadastro inclui data e hora de São Paulo, é acrescentado a um CSV e aparece entre os cinco últimos registros.

**Demonstração acadêmica: utilize apenas dados fictícios.**

[Abrir Streamlit publicado](https://nomi-unicamp-atividade-01.streamlit.app/) · [Repositório GitHub](https://github.com/nomi-npr/pos_unicamp) · [Evidências e entrega](docs/entrega.md)

## Executar

Requer Python 3.12 em macOS ou Linux. Execute os comandos na raiz deste repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r atividade_01/requirements.txt
```

Gradio local:

```bash
python -m atividade_01.gradio_app.app
```

Abra <http://127.0.0.1:7860>. O arquivo `atividade_01/gradio_app/pacientes.csv` será criado no primeiro cadastro, com cabeçalho, e os próximos envios acrescentarão linhas. Para escolher outro destino, defina a variável `GRADIO_CSV` antes de executar.

Streamlit:

```bash
python -m streamlit run atividade_01/app.py
```

Abra <http://localhost:8501>. O formulário usa `st.form`, mantém os registros em `st.session_state` e grava um `pacientes.csv` temporário exclusivo para cada sessão. O botão **Baixar CSV** exporta todos os cadastros da sessão, mesmo que a tabela exiba somente os últimos cinco. Os campos permanecem preenchidos após o envio para permitir correções; altere-os antes de cadastrar outra pessoa.

O disco do Streamlit Community Cloud é efêmero. Baixe o CSV antes de encerrar a sessão; recarregar a página pode iniciar outra sessão. Visitantes não compartilham a mesma tabela ou arquivo. A aplicação é uma demonstração sem autenticação para uso com dados fictícios.

## Estrutura

```text
app.py                      Entrada do Streamlit Community Cloud
gradio_app/app.py           Interface Gradio em coluna única
streamlit_app/app.py        Interface Streamlit e exportação
cadastro/dados.py           Validação, timestamp e persistência CSV
requirements.txt           Gradio, Streamlit e pandas
exemplos/pacientes.csv      Exemplo com 12 pacientes fictícios
docs/evidencias/            Capturas das interfaces em execução
docs/entrega.md             Links e conferência da entrega
scripts/gerar_exemplo.py    Geração reproduzível do CSV
tests/                     Testes de persistência e Streamlit
```

Os CSVs gerados durante o uso, o ambiente virtual e segredos ficam fora do Git. Somente o CSV fictício de exemplo é versionado.

## Publicar no Streamlit Community Cloud

1. Envie este projeto para um repositório público no GitHub.
2. Acesse [Streamlit Community Cloud](https://share.streamlit.io/) e entre com GitHub.
3. Escolha **Create app**, **Yup, I have an app**, e informe repositório, branch `main` e arquivo `atividade_01/app.py`.
4. Em **Advanced settings**, selecione Python 3.12. Não há segredos a configurar.
5. Clique em **Deploy**, aguarde a instalação e teste cadastro e download no endereço público.
6. Abra o mesmo endereço no celular e confira os cinco campos, cadastro, tabela e download.

Referência: [documentação oficial de publicação](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Testar

```bash
python -m unittest discover -s atividade_01/tests -v
```

Os testes verificam criação e acréscimo no CSV, cabeçalho único, acentos e quebras de linha, validação, gravações simultâneas, acumulação da sessão, isolamento entre visitantes e exibição dos últimos cinco cadastros.

Para gerar novamente o CSV de exemplo, remova apenas `atividade_01/exemplos/pacientes.csv` e execute:

```bash
python -m atividade_01.scripts.gerar_exemplo
```

## Comparação prática

| Aspecto | Gradio | Streamlit |
| --- | --- | --- |
| Organização | `gr.Blocks` com componentes em coluna única | `st.form` agrupa os cinco campos |
| Envio | Evento `.click()` chama a função de cadastro | `st.form_submit_button` envia o formulário e reexecuta o script |
| Estado | CSV local conserva os cadastros entre execuções | `st.session_state` acumula os registros de cada sessão |
| Feedback | Mensagem e `gr.Dataframe` atualizadas pelo evento | `st.success`, tabela e botão de download |
| Persistência | Arquivo local permanece no computador | CSV temporário; exportação necessária na nuvem |
| Publicação nesta atividade | Execução local, sem link de compartilhamento | GitHub conectado ao Community Cloud |
| Vantagem observada | Ligação direta entre entradas, função e saídas | Formulário, estado, tabela e exportação integrados |
| Limitação | Estado de vários componentes exige encadear eventos | Reexecuções exigem cuidado com estado e gravações duplicadas |

As interfaces usam coluna única para acomodar telas estreitas. A prioridade é apenas um campo didático informado pelo usuário, sem classificação clínica automática.
