import csv
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from atividade_01.cadastro.dados import COLUNAS, criar_registro, exportar_csv, ler_registros, salvar_registro


class PersistenciaTest(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.arquivo = Path(self.pasta.name) / "pacientes.csv"

    def registro(self, nome="João Exemplo", motivo='Retorno, com "observação"\nem duas linhas'):
        return criar_registro(nome, 31, "Unimed", 3, motivo)

    def test_cria_cabecalho_anexa_e_preserva_acentos_e_quebras(self):
        self.assertTrue(ler_registros(self.arquivo).empty)
        registro = self.registro()
        salvar_registro(registro, self.arquivo)
        salvar_registro(self.registro("Maria Exemplo", ""), self.arquivo)
        with self.arquivo.open(encoding="utf-8", newline="") as origem:
            linhas = list(csv.reader(origem))
        self.assertEqual(linhas[0], COLUNAS)
        self.assertEqual(len(linhas), 3)
        tabela = ler_registros(self.arquivo)
        self.assertEqual(tabela.iloc[0]["motivo"], registro["motivo"])
        self.assertEqual(tabela.iloc[1]["motivo"], "")
        self.assertEqual(tabela.iloc[0]["nome"], "João Exemplo")
        self.assertIn("timestamp,nome,idade,convenio,prioridade,motivo", exportar_csv(tabela).decode("utf-8-sig"))

    def test_rejeita_dados_invalidos(self):
        casos = [
            (" ", 20, "Unimed", 1, ""),
            ("Teste", -1, "Unimed", 1, ""),
            ("Teste", 121, "Unimed", 1, ""),
            ("Teste", 20.5, "Unimed", 1, ""),
            ("Teste", float("nan"), "Unimed", 1, ""),
            ("Teste", 20, "Inválido", 1, ""),
            ("Teste", 20, "Unimed", 6, ""),
        ]
        for valores in casos:
            with self.subTest(valores=valores), self.assertRaises(ValueError):
                criar_registro(*valores)
        self.assertFalse(self.arquivo.exists())

    def test_cadastros_simultaneos_nao_duplicam_cabecalho(self):
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(lambda i: salvar_registro(self.registro(f"Teste {i}"), self.arquivo), range(20)))
        tabela = ler_registros(self.arquivo)
        self.assertEqual(len(tabela), 20)
        self.assertEqual(tabela.nome.nunique(), 20)

    def test_nao_mistura_csv_com_esquema_incompativel(self):
        self.arquivo.write_text("outra,coluna\n1,2\n", encoding="utf-8")
        antes = self.arquivo.read_bytes()
        with self.assertRaises(ValueError):
            salvar_registro(self.registro(), self.arquivo)
        self.assertEqual(self.arquivo.read_bytes(), antes)


if __name__ == "__main__":
    unittest.main()
