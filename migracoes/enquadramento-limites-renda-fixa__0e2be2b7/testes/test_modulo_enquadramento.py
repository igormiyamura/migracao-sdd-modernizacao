"""Testes de src/enquadramento_limites_renda_fixa/logica/modulo_enquadramento.py."""

import pandas as pd

from enquadramento_limites_renda_fixa.logica.modulo_enquadramento import (
    avaliar_enquadramento,
)


def test_book_sem_posicao_recebe_valor_utilizado_zero():
    """Replica o comportamento original (discovery.yaml, riscos_pontos_atencao):
    book presente em Limites mas sem posição em Posicoes não é erro, vira 0."""
    limites_config = pd.DataFrame([{"book": "BOOK_SEM_POSICAO", "limite_dv01": 1000}])
    dv01_por_book = pd.DataFrame(columns=["book", "dv01"])

    resultado = avaliar_enquadramento(limites_config, dv01_por_book)

    assert len(resultado) == 1
    assert resultado[0].book == "BOOK_SEM_POSICAO"
    assert resultado[0].valor_utilizado == 0.0


def test_book_com_posicao_usa_dv01_consolidado():
    limites_config = pd.DataFrame([{"book": "BOOK1", "limite_dv01": 1000}])
    dv01_por_book = pd.DataFrame([{"book": "BOOK1", "dv01": 400.0}])

    resultado = avaliar_enquadramento(limites_config, dv01_por_book)

    assert resultado[0].valor_utilizado == 400.0
    assert resultado[0].valor_limite == 1000
