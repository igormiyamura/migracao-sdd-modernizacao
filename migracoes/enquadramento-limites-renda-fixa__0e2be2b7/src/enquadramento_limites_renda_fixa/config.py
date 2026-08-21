"""Configuração do processo, carregada de config.yaml -- ver
guardrails/codigo.md. Os limiares e caminhos abaixo eram constantes fixas no
VBA original (ver riscos_pontos_atencao em entrada/discovery.yaml)."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class ConfiguracaoProcesso(BaseModel):
    caminho_posicoes: str
    caminho_limites: str
    caminho_log: str
    email_head_risco: str
    email_head_mesa: str
    credencial_email: str = "padrao"
    limiar_alerta: float
    limiar_excedido: float


def carregar_config(caminho: str | Path = "config.yaml") -> ConfiguracaoProcesso:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = yaml.safe_load(arquivo)
    return ConfiguracaoProcesso(**dados)
