"""Configuração sem credenciais no código ou no Git."""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from supabase import create_client


class ErroConfiguracao(ValueError):
    pass


@dataclass(frozen=True)
class Configuracao:
    url: str
    chave: str

    @classmethod
    def carregar(cls, secrets=None):
        load_dotenv(Path(__file__).parent / ".env", override=False)
        secrets = secrets or {}
        url = (os.environ.get("SUPABASE_URL") or secrets.get("SUPABASE_URL", "")).strip()
        chave = (os.environ.get("SUPABASE_KEY") or secrets.get("SUPABASE_KEY", "")).strip()
        if not url or not chave:
            raise ErroConfiguracao("Configure SUPABASE_URL e SUPABASE_KEY no .env ou nos secrets do Streamlit.")
        if urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc:
            raise ErroConfiguracao("SUPABASE_URL deve ser a URL HTTP(S) do projeto Supabase.")
        return cls(url, chave)

    def criar_cliente(self):
        return create_client(self.url, self.chave)
