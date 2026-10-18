"""Validação e operações Supabase usadas pelas duas interfaces."""

import re

import pandas as pd

STATUS = ["Aberto", "Em análise", "Aguardando peça", "Concluído", "Entregue"]
COLUNAS = ["OS", "Cliente ID", "Cliente", "Endereço", "E-mail", "Celular/WhatsApp", "Equipamento", "Problema", "Status", "Abertura", "Atualização"]


class ErroTechfix(RuntimeError):
    """Erro seguro para exibição; não inclui tokens ou detalhes da conexão."""


def obrigatorio(valor, campo, limite):
    valor = str(valor or "").strip()
    if not valor:
        raise ValueError(f"Preencha {campo}.")
    if len(valor) > limite:
        raise ValueError(f"{campo}: limite de {limite} caracteres.")
    return valor


def validar_cliente(nome, endereco, email, celular):
    email = obrigatorio(email, "o e-mail", 254).lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ValueError("Informe um e-mail válido, por exemplo cliente@example.invalid.")
    celular = obrigatorio(celular, "o celular/WhatsApp", 13)
    if not re.fullmatch(r"[0-9]{10,13}", celular):
        raise ValueError("O celular deve conter somente números, de 10 a 13 dígitos.")
    return {
        "nome": obrigatorio(nome, "o nome do cliente", 120),
        "endereco": obrigatorio(endereco, "o endereço", 250),
        "email": email, "celular_whatsapp": celular,
    }


def validar_atendimento(nome, endereco, email, celular, modelo, problema):
    dados = validar_cliente(nome, endereco, email, celular)
    dados["modelo_computador"] = obrigatorio(modelo, "o modelo do computador", 150)
    dados["problema_relatado"] = obrigatorio(problema, "o problema apresentado", 4000)
    return dados


def executar(requisicao):
    try:
        return requisicao().data
    except Exception as erro:
        codigo = str(getattr(erro, "code", ""))
        mensagens = {
            "23505": "Este e-mail já pertence a outro cliente. Use um e-mail diferente.",
            "23503": "O cliente possui ordens de serviço. Exclua essas ordens antes de excluir o cliente.",
            "23001": "O cliente possui ordens de serviço. Exclua essas ordens antes de excluir o cliente.",
            "23514": "O banco rejeitou um campo inválido. Confira os dados do formulário.",
            "23502": "Há um campo obrigatório ausente. Confira os dados do formulário.",
            "42501": "Sem permissão. Entre com uma conta da equipe e confira as políticas do banco.",
            "PGRST202": "A função de cadastro não está instalada. Execute sql/schema.sql no Supabase.",
            "PGRST205": "As tabelas não estão instaladas. Execute sql/schema.sql no Supabase.",
        }
        raise ErroTechfix(mensagens.get(codigo, "Não foi possível concluir a operação no Supabase. Verifique a conexão e entre novamente se a sessão expirou.")) from None


class Techfix:
    def __init__(self, cliente):
        self.cliente = cliente

    def cadastrar(self, nome, endereco, email, celular, modelo, problema):
        dados = validar_atendimento(nome, endereco, email, celular, modelo, problema)
        numero = executar(lambda: self.cliente.rpc("registrar_atendimento", {f"p_{k}": v for k, v in dados.items()}).execute())
        if not isinstance(numero, int) or isinstance(numero, bool):
            raise ErroTechfix("O banco não retornou o número da OS. Confira a instalação de sql/schema.sql.")
        return numero

    def _listar(self, tabela, campos):
        registros = []
        inicio = 0
        while True:
            pagina = executar(lambda: self.cliente.table(tabela).select(campos).order("id").range(inicio, inicio + 499).execute())
            registros.extend(pagina)
            if len(pagina) < 500:
                return registros
            inicio += 500

    def listar_ordens(self):
        return self._listar("ordens_servico", "id,cliente_id,modelo_computador,problema_relatado,status,data_abertura,data_atualizacao,clientes(id,nome,endereco,email,celular_whatsapp)")

    def listar_clientes(self):
        return self._listar("clientes", "id,nome,endereco,email,celular_whatsapp,data_cadastro")

    def alterar_status(self, os_id, status):
        if status not in STATUS:
            raise ValueError("Selecione um status válido.")
        dados = executar(lambda: self.cliente.table("ordens_servico").update({"status": status}).eq("id", os_id).execute())
        self._exigir_registro(dados)

    def editar_cliente(self, cliente_id, nome, endereco, email, celular):
        dados = validar_cliente(nome, endereco, email, celular)
        resultado = executar(lambda: self.cliente.table("clientes").update(dados).eq("id", cliente_id).execute())
        self._exigir_registro(resultado)

    def excluir_os(self, os_id, confirmado=False):
        if not confirmado:
            raise ValueError("Confirme a exclusão da ordem de serviço.")
        dados = executar(lambda: self.cliente.table("ordens_servico").delete().eq("id", os_id).execute())
        self._exigir_registro(dados)

    def excluir_cliente(self, cliente_id, confirmado=False):
        if not confirmado:
            raise ValueError("Confirme a exclusão do cliente.")
        dados = executar(lambda: self.cliente.table("clientes").delete().eq("id", cliente_id).execute())
        self._exigir_registro(dados)

    @staticmethod
    def _exigir_registro(dados):
        if not dados:
            raise ErroTechfix("Registro não encontrado ou sem permissão. Atualize a consulta.")


def tabela_ordens(ordens):
    linhas = []
    for os in ordens:
        cliente = os.get("clientes") or {}
        linhas.append({
            "OS": os["id"], "Cliente ID": os["cliente_id"],
            "Cliente": cliente.get("nome", ""), "Endereço": cliente.get("endereco", ""),
            "E-mail": cliente.get("email", ""), "Celular/WhatsApp": cliente.get("celular_whatsapp", ""),
            "Equipamento": os["modelo_computador"], "Problema": os["problema_relatado"],
            "Status": os["status"], "Abertura": os["data_abertura"], "Atualização": os["data_atualizacao"],
        })
    tabela = pd.DataFrame(linhas, columns=COLUNAS)
    for coluna in ["Abertura", "Atualização"]:
        if not tabela.empty:
            tabela[coluna] = pd.to_datetime(tabela[coluna], utc=True).dt.tz_convert("America/Sao_Paulo").dt.strftime("%d/%m/%Y %H:%M:%S")
    return tabela


def filtrar(tabela, nome="", email="", status=None):
    filtro = tabela["Cliente"].str.contains(nome.strip(), case=False, regex=False, na=False)
    filtro &= tabela["E-mail"].str.contains(email.strip(), case=False, regex=False, na=False)
    if status is not None:
        filtro &= tabela["Status"].isin(status)
    return tabela.loc[filtro].copy()


def exportar_csv(tabela):
    # Prefixo protege texto digitado pelo usuário contra fórmulas em planilhas.
    tabela = tabela.copy()
    for coluna in tabela.select_dtypes(include=["object", "string"]).columns:
        tabela[coluna] = tabela[coluna].map(lambda valor: "'" + valor if isinstance(valor, str) and valor.lstrip().startswith(("=", "+", "-", "@")) else valor)
    return tabela.to_csv(index=False).encode("utf-8-sig")
