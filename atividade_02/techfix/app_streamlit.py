"""Dentro de techfix/: streamlit run app_streamlit.py --server.port 8502."""

import sys
from pathlib import Path

RAIZ = str(Path(__file__).resolve().parents[1])
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import streamlit as st

from techfix.config import Configuracao, ErroConfiguracao
from techfix.servicos import STATUS, ErroTechfix, Techfix, exportar_csv, filtrar, tabela_ordens


def executar_acao(acao, mensagem):
    try:
        acao()
    except (ValueError, ErroTechfix) as erro:
        st.error(str(erro))
        return
    st.session_state["techfix_mensagem"] = mensagem
    st.rerun()


def login(config):
    st.subheader("Acesso da equipe")
    st.caption("Entre com uma conta criada no Supabase Auth deste projeto.")
    with st.form("techfix_login", clear_on_submit=True):
        email = st.text_input("E-mail da equipe", placeholder="Seu e-mail de acesso")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar", type="primary")
    if entrar:
        if not email.strip() or not senha:
            st.error("Informe e-mail e senha.")
            return
        try:
            cliente = config.criar_cliente()
            resposta = cliente.auth.sign_in_with_password({"email": email.strip(), "password": senha})
            if not resposta.session:
                raise ValueError("Sem sessão")
        except Exception:
            st.error("Não foi possível entrar. Confira suas credenciais e a conexão com o Supabase.")
        else:
            # Um cliente autenticado por sessão; nenhuma sessão é compartilhada.
            st.session_state["techfix_servico"] = Techfix(cliente)
            st.session_state["techfix_email"] = email.strip()
            st.rerun()


def formulario_cadastro(servico):
    st.subheader("Abrir ordem de serviço")
    st.caption("O e-mail identifica o cliente. Se já existir, seus dados cadastrados serão mantidos.")
    with st.form("techfix_cadastro", clear_on_submit=False):
        nome = st.text_input("Nome do Cliente", placeholder="Ana Exemplo", max_chars=120)
        endereco = st.text_input("Endereço", placeholder="Rua Fictícia, 100", max_chars=250)
        email = st.text_input("E-mail", placeholder="ana@example.invalid", max_chars=254)
        celular = st.text_input("Celular / WhatsApp", placeholder="11900000001", max_chars=13)
        modelo = st.text_input("Modelo do Computador", placeholder="Notebook Modelo Exemplo", max_chars=150)
        problema = st.text_area("Problema Apresentado", placeholder="Descreva o defeito.", max_chars=4000)
        cadastrar = st.form_submit_button("Cadastrar OS", type="primary")
    if cadastrar:
        try:
            numero = servico.cadastrar(nome, endereco, email, celular, modelo, problema)
        except (ValueError, ErroTechfix) as erro:
            st.error(str(erro))
        else:
            st.session_state["techfix_mensagem"] = f"Ordem de serviço nº {numero} cadastrada com status Aberto."
            st.rerun()


def editar_excluir(servico, ordens, clientes):
    st.subheader("Ordens de serviço")
    if ordens:
        ordens_por_id = {os["id"]: os for os in ordens}
        os_id = st.selectbox(
            "Selecione a OS", list(ordens_por_id), key="techfix_os_id",
            format_func=lambda id: f"OS #{id} · {(ordens_por_id[id].get('clientes') or {}).get('nome', '')} · {ordens_por_id[id]['modelo_computador']}",
        )
        with st.form(f"editar_os_{os_id}"):
            status = st.selectbox("Novo status", STATUS, index=STATUS.index(ordens_por_id[os_id]["status"]))
            salvar = st.form_submit_button("Salvar status", type="primary")
        if salvar:
            executar_acao(lambda: servico.alterar_status(os_id, status), f"Status da OS #{os_id} atualizado.")
        confirmar_os = st.checkbox(f"Confirmo excluir permanentemente a OS #{os_id}.", key=f"confirmar_os_{os_id}")
        if st.button("Excluir OS", disabled=not confirmar_os):
            executar_acao(lambda: servico.excluir_os(os_id, confirmado=confirmar_os), f"OS #{os_id} excluída.")
    else:
        st.info("Nenhuma ordem de serviço cadastrada.")

    st.divider()
    st.subheader("Clientes")
    if not clientes:
        st.info("Nenhum cliente cadastrado.")
        return
    clientes_por_id = {c["id"]: c for c in clientes}
    cliente_id = st.selectbox(
        "Selecione o cliente", list(clientes_por_id), key="techfix_cliente_id",
        format_func=lambda id: f"#{id} · {clientes_por_id[id]['nome']} · {clientes_por_id[id]['email']}",
    )
    cliente = clientes_por_id[cliente_id]
    with st.form(f"editar_cliente_{cliente_id}"):
        nome = st.text_input("Nome do cliente", value=cliente["nome"], max_chars=120)
        endereco = st.text_input("Endereço do cliente", value=cliente["endereco"], max_chars=250)
        email = st.text_input("E-mail do cliente", value=cliente["email"], max_chars=254)
        celular = st.text_input("Celular do cliente", value=cliente["celular_whatsapp"], max_chars=13)
        salvar = st.form_submit_button("Salvar cliente", type="primary")
    if salvar:
        executar_acao(lambda: servico.editar_cliente(cliente_id, nome, endereco, email, celular), f"Cliente #{cliente_id} atualizado.")
    vinculadas = sum(os["cliente_id"] == cliente_id for os in ordens)
    st.caption(f"Este cliente tem {vinculadas} OS vinculada(s). Para excluí-lo, remova primeiro todas as suas OS.")
    confirmar_cliente = st.checkbox(f"Confirmo excluir permanentemente o cliente #{cliente_id} ({cliente['nome']}).", key=f"confirmar_cliente_{cliente_id}")
    if st.button("Excluir cliente", disabled=not confirmar_cliente):
        executar_acao(lambda: servico.excluir_cliente(cliente_id, confirmado=confirmar_cliente), f"Cliente #{cliente_id} excluído.")


def painel(servico):
    with st.sidebar:
        st.header("Consulta")
        st.caption("Sessão autenticada · Equipe TechFix")
        nome = st.text_input("Buscar por nome", placeholder="Parte do nome")
        email = st.text_input("Buscar por e-mail", placeholder="Parte do e-mail")
        status = st.multiselect("Status", STATUS, default=STATUS)
        st.button("Atualizar dados")
        if st.button("Sair"):
            try:
                servico.cliente.auth.sign_out()
            except Exception:
                pass  # A sessão local é encerrada mesmo se a rede estiver indisponível.
            for chave in ["techfix_servico", "techfix_email", "techfix_mensagem"]:
                st.session_state.pop(chave, None)
            st.rerun()

    if mensagem := st.session_state.pop("techfix_mensagem", None):
        st.success(mensagem)
    try:
        ordens = servico.listar_ordens()
        clientes = servico.listar_clientes()
    except ErroTechfix as erro:
        st.error(str(erro))
        return
    tabela = tabela_ordens(ordens)
    resultado = filtrar(tabela, nome, email, status)
    consultar, cadastrar, editar, indicadores = st.tabs(
        ["Consultar", "Cadastrar", "Editar / Excluir", "Indicadores"],
        key="techfix_aba", on_change="rerun",
    )
    with consultar:
        st.subheader("Ordens de serviço")
        st.caption(f"{len(resultado)} de {len(tabela)} OS · datas no horário de São Paulo")
        st.dataframe(resultado, hide_index=True, width="stretch")
        st.download_button(
            "Exportar dados filtrados em CSV", data=exportar_csv(resultado),
            file_name="techfix_ordens_filtradas.csv", mime="text/csv", disabled=resultado.empty,
        )
        if resultado.empty:
            st.info("Nenhuma ordem corresponde aos filtros. Ajuste a busca ou cadastre uma nova OS.")
    with cadastrar:
        formulario_cadastro(servico)
    with editar:
        editar_excluir(servico, ordens, clientes)
    with indicadores:
        st.subheader("Indicadores dos resultados filtrados")
        st.metric("Total de OS", len(resultado))
        contagens = resultado["Status"].value_counts().reindex(STATUS, fill_value=0)
        for grupo in [STATUS[:3], STATUS[3:]]:
            for coluna, item in zip(st.columns(len(grupo)), grupo):
                coluna.metric(item, int(contagens[item]))
        st.bar_chart(contagens.rename("Ordens de serviço"), color="#2563EB")
        st.caption("Os filtros de nome, e-mail e status da barra lateral também se aplicam a estes indicadores.")


def main():
    st.set_page_config(page_title="TechFix | Painel administrativo", page_icon="🛠️", layout="wide")
    st.caption("ATIVIDADE AULA 2 · GRADIO + SUPABASE + STREAMLIT")
    st.title("TechFix Informática")
    st.caption("Painel administrativo · demonstração acadêmica com dados fictícios")
    try:
        secrets = dict(st.secrets)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        secrets = {}
    try:
        config = Configuracao.carregar(secrets)
    except ErroConfiguracao as erro:
        st.error(str(erro))
        st.info("Siga a configuração do Supabase descrita no README da atividade 02.")
        return
    if "techfix_servico" not in st.session_state:
        login(config)
    else:
        painel(st.session_state["techfix_servico"])


if __name__ == "__main__":
    main()
