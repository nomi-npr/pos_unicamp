"""Configuração sem credenciais no código ou no Git."""

import os
import base64
import json
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from supabase import create_client


class ErroConfiguracao(ValueError):
    pass


@dataclass(frozen=True)
class Configuracao:
    url: str
    chave: str = field(repr=False)

    @classmethod
    def carregar(cls, secrets=None):
        load_dotenv(Path(__file__).parent / ".env", override=False)
        secrets = secrets or {}
        url = (os.environ.get("SUPABASE_URL") or secrets.get("SUPABASE_URL", "")).strip()
        chave = (
            os.environ.get("SUPABASE_PUBLIC_KEY")
            or secrets.get("SUPABASE_PUBLIC_KEY")
            or os.environ.get("SUPABASE_KEY")
            or secrets.get("SUPABASE_KEY", "")
        ).strip()
        if not url or not chave:
            raise ErroConfiguracao("Configure SUPABASE_URL e SUPABASE_PUBLIC_KEY no .env ou nos secrets do Streamlit.")
        role = None
        if chave.count(".") == 2:
            try:
                role = json.loads(base64.urlsafe_b64decode(chave.split(".")[1] + "===")).get("role")
            except (ValueError, UnicodeError, AttributeError):
                pass
        if chave.startswith("sb_secret_") or role == "service_role":
            raise ErroConfiguracao("Use a chave pública (SUPABASE_PUBLIC_KEY) nas interfaces TechFix.")
        if urlparse(url).scheme not in {"http", "https"} or not urlparse(url).netloc:
            raise ErroConfiguracao("SUPABASE_URL deve ser a URL HTTP(S) do projeto Supabase.")
        return cls(url, chave)

    def criar_cliente(self):
        return create_client(self.url, self.chave)
