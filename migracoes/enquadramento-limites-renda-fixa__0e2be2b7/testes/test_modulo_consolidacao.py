"""Testes de src/enquadramento_limites_renda_fixa/logica/modulo_consolidacao.py."""

import pandas as pd

from enquadramento_limites_renda_fixa.logica.modulo_consolidacao import (
    consolidar_dv01_por_book,
)


def test_soma_duas_posicoes_do_mesmo_book():
    posicoes = pd.DataFrame(
        [
            {"ativo": "A1", "book": "BOOK1", "quantidade": 100, "dv01_unitario": 2.0},
            {"ativo": "A2", "book": "BOOK1", "quantidade": 50, "dv01_unitario": 4.0},
        ]
    )
    resultado = consolidar_dv01_por_book(posicoes)
    assert resultado.loc[resultado["book"] == "BOOK1", "dv01"].iloc[0] == 400.0


def test_book_com_uma_unica_posicao():
    posicoes = pd.DataFrame(
        [{"ativo": "A1", "book": "BOOK2", "quantidade": 10, "dv01_unitario": 3.0}]
    )
    resultado = consolidar_dv01_por_book(posicoes)
    assert resultado.loc[resultado["book"] == "BOOK2", "dv01"].iloc[0] == 30.0
