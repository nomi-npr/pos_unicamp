import csv
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
from supabase import ClientOptions, create_client

import _bootstrap  # Importa o pacote techfix também fora do repositório.

from techfix.servicos import ErroTechfix, Techfix, exportar_csv, filtrar, tabela_ordens, validar_atendimento

CLIENTE = {"id": 1, "nome": "Ana Exemplo", "endereco": "Rua Fictícia, 100", "email": "ana@example.invalid", "celular_whatsapp": "11900000001"}


def ordem(id=1, status="Aberto", cliente=None):
    return {"id": id, "cliente_id": 1, "modelo_computador": "Notebook Exemplo", "problema_relatado": "Não liga", "status": status, "data_abertura": "2026-10-18T12:00:00+00:00", "data_atualizacao": "2026-10-18T12:00:00+00:00", "clientes": cliente or CLIENTE.copy()}


class ServicosTest(unittest.TestCase):
    def cliente_http(self, responder):
        http = httpx.Client(transport=httpx.MockTransport(responder))
        self.addCleanup(http.close)
        return create_client("https://techfix-test.supabase.co", "sb_publishable_test", options=ClientOptions(httpx_client=http))

    def test_rpc_valida_normaliza_e_nao_envia_invalido(self):
        chamadas = []
        def responder(req):
            chamadas.append(req)
            return httpx.Response(200, json=42)
        servico = Techfix(self.cliente_http(responder))
        self.assertEqual(servico.cadastrar(" Ana ", " Rua X ", " ANA@EXAMPLE.INVALID ", "11900000001", "Notebook", "Não liga"), 42)
        payload = json.loads(chamadas[0].content)
        self.assertEqual(chamadas[0].url.path, "/rest/v1/rpc/registrar_atendimento")
        self.assertEqual(payload["p_email"], "ana@example.invalid")
        self.assertEqual(payload["p_nome"], "Ana")
        for celular in ["(11)900000001", "abc", "123", "１２３４５６７８９０"]:
            with self.assertRaises(ValueError):
                servico.cadastrar("Ana", "Rua X", "ana@example.invalid", celular, "Notebook", "Não liga")
        self.assertEqual(len(chamadas), 1)
        with self.assertRaises(ValueError):
            validar_atendimento(" ", "Rua X", "email-invalido", "11900000001", "Notebook", "Teste")

    def test_consulta_paginada_nao_trunca_mais_de_500_registros(self):
        offsets = []
        def responder(req):
            inicio = int(req.url.params.get("offset", "0"))
            offsets.append(inicio)
            return httpx.Response(200, json=[{"id": i} for i in range(inicio, min(inicio + 500, 1002))])
        linhas = Techfix(self.cliente_http(responder)).listar_clientes()
        self.assertEqual(len(linhas), 1002)
        self.assertEqual(offsets, [0, 500, 1000])

    def test_alteracao_e_exclusao_sempre_limitadas_ao_id(self):
        chamadas = []
        def responder(req):
            chamadas.append(req)
            return httpx.Response(200, json=[{"id": 7}])
        servico = Techfix(self.cliente_http(responder))
        servico.alterar_status(7, "Concluído")
        servico.editar_cliente(7, "Ana", "Rua Atualizada", "nova@example.invalid", "11900000002")
        servico.excluir_os(7, confirmado=True)
        servico.excluir_cliente(7, confirmado=True)
        self.assertEqual([r.method for r in chamadas], ["PATCH", "PATCH", "DELETE", "DELETE"])
        self.assertTrue(all(r.url.params["id"] == "eq.7" for r in chamadas))
        for metodo in [servico.excluir_os, servico.excluir_cliente]:
            with self.assertRaises(ValueError):
                metodo(7)
        self.assertEqual(len(chamadas), 4)

    def test_erros_sao_amigaveis_e_nao_expoem_detalhes(self):
        def responder(req):
            return httpx.Response(409, json={"code":"23503","message":"segredo-interno","details":None,"hint":None})
        servico = Techfix(self.cliente_http(responder))
        with self.assertRaises(ErroTechfix) as erro:
            servico.excluir_cliente(1, confirmado=True)
        self.assertIn("possui ordens", str(erro.exception))
        self.assertNotIn("segredo-interno", str(erro.exception))

    def test_filtros_literais_metricas_e_exportacao(self):
        tabela = tabela_ordens([ordem(), ordem(2,"Concluído", {**CLIENTE, "nome":"Bruno [Exemplo]", "email":"bruno@example.invalid"})])
        self.assertEqual(tabela.iloc[0]["Abertura"], "18/10/2026 09:00:00")
        filtro = filtrar(tabela, "[exemplo]", "BRUNO@", ["Concluído"])
        self.assertEqual(list(filtro["OS"]), [2])
        self.assertTrue(filtrar(tabela, status=[]).empty)
        linhas = list(csv.DictReader(io.StringIO(exportar_csv(filtro).decode("utf-8-sig"))))
        self.assertEqual(len(linhas), 1)
        self.assertEqual(linhas[0]["Status"], "Concluído")
        tabela.loc[0,"Problema"] = '=HYPERLINK("https://example.invalid")'
        exportado = list(csv.DictReader(io.StringIO(exportar_csv(tabela).decode("utf-8-sig"))))
        self.assertTrue(exportado[0]["Problema"].startswith("'="))


if __name__ == "__main__":
    unittest.main()
