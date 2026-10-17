"""Execute na raiz: python -m gradio_app.app."""

import os
from pathlib import Path

import gradio as gr

from cadastro.dados import CONVENIOS, criar_registro, ler_registros, salvar_registro

ARQUIVO_CSV = Path(os.environ.get("GRADIO_CSV", Path(__file__).parent / "pacientes.csv"))


def cadastrar_paciente(nome, idade, convenio, prioridade, motivo):
    try:
        registro = criar_registro(nome, idade, convenio, prioridade, motivo)
        salvar_registro(registro, ARQUIVO_CSV)
    except ValueError as erro:
        return f"Não foi possível cadastrar: {erro}", gr.skip()
    except OSError:
        return "Não foi possível gravar o CSV. Verifique a permissão da pasta e tente novamente.", gr.skip()
    return "Paciente cadastrado com sucesso!", ler_registros(ARQUIVO_CSV).tail(5)


with gr.Blocks(title="Cadastro de Pacientes | Gradio") as demo:
    gr.Markdown("# Cadastro de Pacientes\nRecepção · Atividade Aula 1 · Gradio")
    gr.Markdown("Demonstração acadêmica: utilize apenas dados fictícios.")
    nome = gr.Textbox(label="Nome do paciente", placeholder="Ex.: Ana Exemplo")
    idade = gr.Number(label="Idade", value=0, minimum=0, maximum=120, precision=0)
    convenio = gr.Dropdown(CONVENIOS, label="Convênio", value=CONVENIOS[0])
    prioridade = gr.Slider(1, 5, value=1, step=1, label="Prioridade do atendimento (5 = urgente)")
    motivo = gr.Textbox(label="Motivo da consulta / observações", lines=3)
    botao = gr.Button("Cadastrar", variant="primary")
    saida = gr.Textbox(label="Status", interactive=False)
    tabela = gr.Dataframe(
        value=ler_registros(ARQUIVO_CSV).tail(5),
        label="Últimos 5 pacientes cadastrados", interactive=False,
    )
    botao.click(
        cadastrar_paciente, [nome, idade, convenio, prioridade, motivo],
        [saida, tabela], api_name="cadastrar_paciente",
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(primary_hue="teal"), share=False)
