from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest

import _bootstrap  # Importa o pacote techfix também fora do repositório.

from techfix.app_gradio import cadastrar, limpar
from techfix.servicos import ErroTechfix
from test_servicos import CLIENTE, ordem

APP = Path(__file__).resolve().parents[1] / "app_streamlit.py"


def item(elementos, label):
    return next(elemento for elemento in elementos if elemento.label == label)


class InterfacesTest(unittest.TestCase):
    def setUp(self):
        self.config = Mock()
        self.config_patch = patch("techfix.app_streamlit.Configuracao.carregar", return_value=self.config)
        self.config_patch.start()
        self.addCleanup(self.config_patch.stop)
        self.ordens = [ordem(1), ordem(2, "Concluído", {**CLIENTE, "nome":"Bruno Exemplo", "email":"bruno@example.invalid"})]
        self.servico = Mock()
        self.servico.listar_ordens.side_effect = lambda: deepcopy(self.ordens)
        self.servico.listar_clientes.return_value = [CLIENTE.copy()]
        self.app = AppTest.from_file(str(APP), default_timeout=20)
        self.app.session_state["techfix_servico"] = self.servico
        self.app.session_state["techfix_email"] = "equipe@example.invalid"

    def test_consulta_filtros_indicadores_e_telas_vazias(self):
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual([t.label for t in self.app.tabs], ["Consultar", "Cadastrar", "Editar / Excluir", "Indicadores"])
        self.assertEqual(len(self.app.dataframe[0].value), 2)
        self.assertEqual(item(self.app.metric, "Total de OS").value, "2")
        item(self.app.sidebar.text_input, "Buscar por nome").set_value("BRUNO")
        self.app.run()
        self.assertEqual(list(self.app.dataframe[0].value["OS"]), [2])
        self.assertEqual(item(self.app.metric, "Concluído").value, "1")
        self.app.sidebar.multiselect[0].set_value([]).run()
        self.assertTrue(self.app.dataframe[0].value.empty)
        self.assertEqual(item(self.app.metric, "Total de OS").value, "0")
        self.assertFalse(self.app.exception)

    def test_status_e_exclusao_exigem_escolha_e_confirmacao(self):
        self.app.run()
        self.assertTrue(item(self.app.button,"Excluir OS").disabled)
        self.assertTrue(item(self.app.button,"Excluir cliente").disabled)
        item(self.app.selectbox,"Novo status").select("Em análise")
        item(self.app.button,"Salvar status").click().run()
        self.servico.alterar_status.assert_called_once_with(1,"Em análise")
        self.app.checkbox(key="confirmar_os_1").check().run()
        self.assertFalse(item(self.app.button,"Excluir OS").disabled)
        item(self.app.button,"Excluir OS").click().run()
        self.servico.excluir_os.assert_called_once_with(1,confirmado=True)
        self.servico.excluir_cliente.assert_not_called()

    def test_cadastro_e_edicao_de_cliente(self):
        self.servico.cadastrar.return_value = 42
        self.app.run()
        for label, valor in [
            ("Nome do Cliente","Carla Exemplo"),("Endereço","Rua Fictícia, 30"),
            ("E-mail","carla@example.invalid"),("Celular / WhatsApp","11900000003"),
            ("Modelo do Computador","Notebook C"),
        ]:
            item(self.app.text_input,label).set_value(valor)
        item(self.app.text_area,"Problema Apresentado").set_value("Tela não liga")
        item(self.app.button,"Cadastrar OS").click().run()
        self.servico.cadastrar.assert_called_once_with("Carla Exemplo","Rua Fictícia, 30","carla@example.invalid","11900000003","Notebook C","Tela não liga")
        self.assertTrue(any("42" in e.value for e in self.app.success))
        item(self.app.text_input,"Endereço do cliente").set_value("Rua Nova, 20")
        item(self.app.text_input,"E-mail do cliente").set_value("novo@example.invalid")
        item(self.app.text_input,"Celular do cliente").set_value("11900000009")
        item(self.app.button,"Salvar cliente").click().run()
        self.servico.editar_cliente.assert_called_once_with(1,"Ana Exemplo","Rua Nova, 20","novo@example.invalid","11900000009")

    def test_painel_sem_ordens_e_erro_do_banco(self):
        self.ordens.clear()
        self.servico.listar_clientes.return_value = []
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual(item(self.app.metric,"Total de OS").value,"0")
        self.servico.listar_ordens.side_effect = ErroTechfix("Conexão indisponível.")
        self.app.run()
        self.assertEqual(self.app.error[0].value,"Conexão indisponível.")
        self.assertFalse(self.app.exception)

    def test_login_invalido_nao_abre_painel(self):
        self.config.criar_cliente.return_value.auth.sign_in_with_password.side_effect = RuntimeError("detalhe interno")
        app = AppTest.from_file(str(APP),default_timeout=20).run()
        item(app.text_input,"E-mail da equipe").set_value("equipe@example.invalid")
        item(app.text_input,"Senha").set_value("senha-de-teste")
        item(app.button,"Entrar").click().run()
        self.assertTrue(app.error)
        self.assertFalse(app.tabs)
        self.assertNotIn("detalhe interno",app.error[0].value)

    def test_gradio_limpa_campos_e_informa_numero_da_os(self):
        with patch("techfix.app_gradio.Configuracao.carregar") as config, patch("techfix.app_gradio.Techfix") as classe:
            classe.return_value.cadastrar.return_value=12
            msg=cadastrar("Ana Exemplo","Rua Fictícia","ana@example.invalid","11900000001","Notebook","Não liga")
            self.assertIn("nº 12",msg)
            self.assertIn("Aberto",msg)
            config.reset_mock()
            self.assertIn("Não foi possível",cadastrar("","","","","",""))
            config.assert_not_called()
        self.assertEqual(limpar(),("",)*7)


if __name__ == "__main__":
    unittest.main()
