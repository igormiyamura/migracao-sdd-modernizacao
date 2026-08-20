"""Leitura/escrita de arquivos em caminho de rede local (fswcorp).

Implementação placeholder desta fase: acesso direto via sistema de arquivos
(o caminho \\\\fswcorp\\... é montado como caminho de rede padrão do Windows).
Quando o toolkit real for refatorado (etapa 1.5), só o corpo destas duas
funções muda -- a assinatura e o contrato descritos em
guardrails/interface_conectores.md não mudam, então nenhum código de negócio
que as chama precisa ser tocado.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pandas as pd

from .base import ErroConector, logger

_LEITORES: dict[str, Callable[[Path], pd.DataFrame]] = {
    ".csv": pd.read_csv,
    ".xlsx": pd.read_excel,
    ".parquet": pd.read_parquet,
}


def ler_arquivo(caminho: str) -> pd.DataFrame:
    """Lê um arquivo tabular (csv/xlsx/parquet) de um caminho fswcorp."""
    caminho_p = Path(caminho)
    leitor = _LEITORES.get(caminho_p.suffix.lower())
    if leitor is None:
        raise ErroConector(
            f"Formato '{caminho_p.suffix}' não suportado por fswcorp.ler_arquivo: {caminho}"
        )
    logger.info("lendo arquivo fswcorp caminho=%s", caminho)
    return leitor(caminho_p)


def escrever_arquivo(caminho: str, conteudo: pd.DataFrame, formato: str = "csv") -> None:
    """Escreve um DataFrame em um caminho fswcorp, criando diretórios pais se necessário."""
    caminho_p = Path(caminho)
    caminho_p.parent.mkdir(parents=True, exist_ok=True)
    logger.info("escrevendo arquivo fswcorp caminho=%s formato=%s", caminho, formato)
    if formato == "csv":
        conteudo.to_csv(caminho_p, index=False)
    elif formato == "xlsx":
        conteudo.to_excel(caminho_p, index=False)
    elif formato == "parquet":
        conteudo.to_parquet(caminho_p, index=False)
    else:
        raise ErroConector(f"Formato '{formato}' não suportado por fswcorp.escrever_arquivo")
