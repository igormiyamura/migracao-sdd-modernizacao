"""Regra de negócio do módulo `modulo_consolidacao` de entrada/discovery.yaml
(origem: ModuloConsolidacao.bas)."""

from __future__ import annotations

import pandas as pd


def consolidar_dv01_por_book(posicoes: pd.DataFrame) -> pd.DataFrame:
    """DV01 da posição = quantidade * dv01_unitario; DV01 do book = soma do
    DV01 de todas as posições daquele book.

    Original: Function ConsolidarDV01PorBook (discovery.yaml, etapa
    modulo_consolidacao__consolidar_dv01)."""
    resultado = posicoes.copy()
    resultado["dv01"] = resultado["quantidade"] * resultado["dv01_unitario"]
    return resultado.groupby("book", as_index=False)[["dv01"]].sum()
