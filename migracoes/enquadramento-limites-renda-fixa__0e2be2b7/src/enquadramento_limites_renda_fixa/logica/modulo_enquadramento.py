"""Regra de negócio do módulo `modulo_enquadramento` de
entrada/discovery.yaml (origem: ModuloEnquadramento.bas)."""

from __future__ import annotations

import pandas as pd

from .classe_limite import Limite


def avaliar_enquadramento(
    limites_config: pd.DataFrame, dv01_por_book: pd.DataFrame
) -> list[Limite]:
    """Um Limite por linha de `limites_config` (não por book presente em
    `dv01_por_book`); book sem posição naquele dia recebe valor_utilizado=0.

    Original: Function AvaliarEnquadramento (discovery.yaml, etapa
    modulo_enquadramento__avaliar). Regra replicada tal como estava --
    ver riscos_pontos_atencao no discovery para a decisão de não alterar
    esse comportamento nesta migração."""
    exposicoes = dict(zip(dv01_por_book["book"], dv01_por_book["dv01"], strict=True))

    resultado = []
    for _, linha in limites_config.iterrows():
        book = linha["book"]
        resultado.append(
            Limite(
                book=book,
                valor_limite=linha["limite_dv01"],
                valor_utilizado=exposicoes.get(book, 0.0),
            )
        )
    return resultado
