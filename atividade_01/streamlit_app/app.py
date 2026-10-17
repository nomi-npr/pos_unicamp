"""Formulário Streamlit com CSV e registros isolados por sessão."""

import tempfile
from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from atividade_01.cadastro.dados import COLUNAS, CONVENIOS, criar_registro, exportar_csv, salvar_registro


def main():
    st.set_page_config(page_title="Cadastro de Pacientes", page_icon="📋", layout="centered")
    st.caption("RECEPÇÃO · ATIVIDADE AULA 1 · STREAMLIT")
    st.title("Cadastro de Pacientes")
    st.info("Demonstração acadêmica. Utilize apenas dados fictícios.")
    st.caption("Preencha os dados do paciente. Prioridade: 1 a 5, sendo 5 = urgente.")

    if "pacientes" not in st.session_state:
        st.session_state.pacientes = pd.DataFrame(columns=COLUNAS)
    if "arquivo_csv" not in st.session_state:
        st.session_state.arquivo_csv = str(
            Path(tempfile.gettempdir()) / "cadastro_pacientes" / uuid4().hex / "pacientes.csv"
        )

    with st.form("cadastro"):
        nome = st.text_input("Nome do paciente", placeholder="Ex.: Ana Exemplo")
        idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
        convenio = st.selectbox("Convênio", CONVENIOS)
        prioridade = st.slider("Prioridade do atendimento (5 = urgente)", 1, 5)
        motivo = st.text_area("Motivo da consulta / observações")
        enviado = st.form_submit_button("Cadastrar", type="primary", width="stretch")

    if enviado:
        try:
            registro = criar_registro(nome, idade, convenio, prioridade, motivo)
            salvar_registro(registro, st.session_state.arquivo_csv)
        except ValueError as erro:
            st.error(str(erro))
        except OSError:
            st.error("Não foi possível gravar o CSV. Tente novamente.")
        else:
            st.session_state.pacientes = pd.concat(
                [st.session_state.pacientes, pd.DataFrame([registro])], ignore_index=True,
            )
            st.success("Paciente cadastrado com sucesso!")

    st.subheader("Últimos pacientes cadastrados")
    st.caption(f"{len(st.session_state.pacientes)} cadastro(s) nesta sessão · exibindo os últimos 5")
    st.dataframe(st.session_state.pacientes.tail(5), hide_index=True, width="stretch")
    st.download_button(
        "Baixar CSV", data=exportar_csv(st.session_state.pacientes),
        file_name="pacientes.csv", mime="text/csv", width="stretch",
        disabled=st.session_state.pacientes.empty,
    )
    st.caption(
        "O armazenamento na nuvem é temporário. Baixe o CSV antes de encerrar a sessão. "
        "Os cadastros desta sessão não aparecem para outros visitantes."
    )


if __name__ == "__main__":
    main()
