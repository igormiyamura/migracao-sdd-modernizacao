"""Configuração do processo, carregada de config.yaml -- ver
guardrails/codigo.md ("nenhum valor de configuração hardcoded no meio da
lógica"). Os valores abaixo eram constantes fixas na planilha/macro original
(ver riscos_pontos_atencao em entrada/discovery.yaml)."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class ConfiguracaoProcesso(BaseModel):
    caminho_carteira: str
    caminho_saida: str
    email_alerta: str
    credencial_email: str = "mesa_equities"
    fator_confianca: float
    limite_var: float


def carregar_config(caminho: str | Path = "config.yaml") -> ConfiguracaoProcesso:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = yaml.safe_load(arquivo)
    return ConfiguracaoProcesso(**dados)
