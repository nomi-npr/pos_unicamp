"""A chave administrativa nunca deve substituir a identidade do visitante."""

import base64
import json
import unittest
from unittest.mock import patch

import _bootstrap  # Importa o pacote techfix também fora do repositório.

from techfix.config import Configuracao, ErroConfiguracao


class TestConfiguracao(unittest.TestCase):
    @patch("techfix.config.load_dotenv")
    def test_prioriza_publica_e_oculta_chave_no_repr(self, _):
        with patch.dict("os.environ", {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_KEY": "sb_secret_exemplo", "SUPABASE_PUBLIC_KEY": "sb_publishable_exemplo"}, clear=True):
            config = Configuracao.carregar()
        self.assertEqual(config.chave, "sb_publishable_exemplo")
        self.assertNotIn(config.chave, repr(config))

    @patch("techfix.config.load_dotenv")
    def test_recusa_chaves_administrativas(self, _):
        payload = base64.urlsafe_b64encode(json.dumps({"role": "service_role"}).encode()).decode().rstrip("=")
        for chave in ("sb_secret_exemplo", f"header.{payload}.signature"):
            with self.subTest(tipo=chave.split(".")[0]), patch.dict("os.environ", {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_KEY": chave}, clear=True):
                with self.assertRaises(ErroConfiguracao):
                    Configuracao.carregar()
