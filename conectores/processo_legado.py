"""Leitura do output de outro processo (planilha, CSV, parquet) como entrada.

Trata o caso comum de um processo consumir a saída de outro processo já
migrado (ou ainda legado). Reaproveita fswcorp.ler_arquivo quando o output
está em disco/rede; existe como conector próprio porque o *significado* da
leitura é diferente (uma dependência entre processos, não um dado bruto) e
porque a etapa 1.5 pode trocar isso por uma leitura via API/fila em vez de
arquivo.
"""

from __future__ import annotations

import pandas as pd

from . import fswcorp
from .base import logger


def ler_saida(caminho: str, formato: str = "csv") -> pd.DataFrame:
    """Lê o output de outro processo como DataFrame. `formato` documenta a
    expectativa mesmo quando inferido pela extensão, para deixar explícito
    no discovery.yaml qual contrato de saída está sendo consumido."""
    logger.info("lendo saida de processo legado caminho=%s formato=%s", caminho, formato)
    return fswcorp.ler_arquivo(caminho)
