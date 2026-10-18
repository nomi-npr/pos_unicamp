"""Dentro de techfix/: python app_gradio.py."""

import os
import sys
from pathlib import Path

RAIZ = str(Path(__file__).resolve().parents[1])
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import gradio as gr

from techfix.config import Configuracao, ErroConfiguracao
from techfix.servicos import ErroTechfix, Techfix, validar_atendimento


def cadastrar(nome, endereco, email, celular, modelo, problema):
    try:
        validar_atendimento(nome, endereco, email, celular, modelo, problema)
        servico = Techfix(Configuracao.carregar().criar_cliente())
        numero = servico.cadastrar(nome, endereco, email, celular, modelo, problema)
    except (ValueError, ErroConfiguracao, ErroTechfix) as erro:
        return f"Não foi possível cadastrar: {erro}"
    except Exception:
        return "Não foi possível conectar ao Supabase. Confira a configuração e tente novamente."
    return f"Cadastro realizado! Ordem de serviço nº {numero}, com status Aberto."


def limpar():
    return ("",) * 7


with gr.Blocks(title="TechFix | Atendimento") as demo:
    gr.Markdown("# TechFix Informática\n### Novo atendimento\nCadastre o cliente e o equipamento. A OS será aberta automaticamente.")
    gr.Markdown("Demonstração acadêmica: use somente dados fictícios. Se o e-mail já existir, o cadastro do cliente será reaproveitado.")
    with gr.Row():
        with gr.Column(min_width=280):
            nome = gr.Textbox(label="Nome do Cliente", placeholder="Ana Exemplo", max_length=120)
            endereco = gr.Textbox(label="Endereço", placeholder="Rua Fictícia, 100, Bairro Exemplo", max_length=250)
            email = gr.Textbox(label="E-mail", placeholder="ana@example.invalid", max_length=254)
        with gr.Column(min_width=280):
            celular = gr.Textbox(label="Celular / WhatsApp", placeholder="11900000001 (somente números)", max_length=13)
            modelo = gr.Textbox(label="Modelo do Computador", placeholder="Notebook Modelo Exemplo", max_length=150)
            problema = gr.Textbox(label="Problema Apresentado", placeholder="Descreva o defeito e quando começou.", lines=3, max_length=4000)
    with gr.Row():
        enviar = gr.Button("Cadastrar", variant="primary")
        apagar = gr.Button("Limpar")
    status = gr.Textbox(label="Resultado do atendimento", interactive=False)
    campos = [nome, endereco, email, celular, modelo, problema]
    enviar.click(cadastrar, campos, status, api_name="cadastrar")
    apagar.click(limpar, outputs=campos + [status], api_name=False)

if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1", server_port=int(os.environ.get("TECHFIX_GRADIO_PORT", "7861")),
        share=os.environ.get("TECHFIX_SHARE", "true").lower() == "true",
        theme=gr.themes.Soft(primary_hue="blue"),
    )
