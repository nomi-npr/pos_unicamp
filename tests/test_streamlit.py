import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from cadastro.dados import ler_registros

RAIZ = Path(__file__).resolve().parents[1]


class StreamlitTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.app = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=20).run()
        self.app.session_state["arquivo_csv"] = str(Path(self.pasta.name) / "pacientes.csv")

    def cadastrar(self, nome):
        self.app.text_input[0].set_value(nome)
        self.app.number_input[0].set_value(32)
        self.app.selectbox[0].select("SulAmérica")
        self.app.slider[0].set_value(4)
        self.app.text_area[0].set_value("Consulta simulada")
        self.app.button[0].click().run()

    def test_cadastra_em_csv_acumula_sessao_e_exibe_ultimos_cinco(self):
        for i in range(6):
            self.cadastrar(f"Paciente fictício {i}")
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.session_state["pacientes"]), 6)
        self.assertEqual(len(ler_registros(self.app.session_state["arquivo_csv"])), 6)
        self.assertEqual(len(self.app.dataframe[0].value), 5)
        self.assertEqual(self.app.dataframe[0].value.iloc[0]["nome"], "Paciente fictício 1")
        self.assertEqual(self.app.success[0].value, "Paciente cadastrado com sucesso!")
        self.app.run()
        self.assertEqual(len(self.app.session_state["pacientes"]), 6)

    def test_nome_vazio_nao_grava_e_nova_sessao_nao_herda_dados(self):
        self.cadastrar(" ")
        self.assertTrue(self.app.error)
        self.assertTrue(self.app.session_state["pacientes"].empty)
        self.assertFalse(Path(self.app.session_state["arquivo_csv"]).exists())
        self.cadastrar("Paciente Exemplo")
        segunda = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=20).run()
        self.assertTrue(segunda.session_state["pacientes"].empty)
        self.assertNotEqual(segunda.session_state["arquivo_csv"], self.app.session_state["arquivo_csv"])


if __name__ == "__main__":
    unittest.main()
