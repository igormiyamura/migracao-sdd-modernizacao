"""Testes das regras de negócio de entrada/discovery.yaml -- ver a
"Estratégia de testes" em plano/plano_implementacao.md."""

import pandas as pd

from consolidacao_var_equities.logica import (
    calcular_exposicao,
    calcular_var_individual,
    consolidar_var_total,
    montar_relatorio,
)


def _carteira_simples() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"ativo": "AAA1", "quantidade": 100, "preco_unitario": 10.0, "volatilidade": 0.02},
            {"ativo": "BBB1", "quantidade": 200, "preco_unitario": 5.0, "volatilidade": 0.0},
        ]
    )


def test_calcular_exposicao():
    resultado = calcular_exposicao(_carteira_simples())
    assert resultado.loc[resultado["ativo"] == "AAA1", "exposicao"].iloc[0] == 1000.0
    assert resultado.loc[resultado["ativo"] == "BBB1", "exposicao"].iloc[0] == 1000.0


def test_calcular_var_individual():
    carteira = calcular_exposicao(_carteira_simples())
    resultado = calcular_var_individual(carteira, fator_confianca=1.65)
    var_aaa1 = resultado.loc[resultado["ativo"] == "AAA1", "var_individual"].iloc[0]
    assert var_aaa1 == 1000.0 * 0.02 * 1.65

    var_bbb1 = resultado.loc[resultado["ativo"] == "BBB1", "var_individual"].iloc[0]
    assert var_bbb1 == 0.0, "volatilidade zero deve gerar VaR zero, nao erro"


def test_consolidar_var_total_excede_limite():
    carteira = calcular_var_individual(calcular_exposicao(_carteira_simples()), 1.65)
    resultado = consolidar_var_total(carteira, limite_var=1.0)
    assert (resultado["status"] == "EXCEDIDO").all()
    assert resultado["var_total"].iloc[0] == carteira["var_individual"].sum()


def test_consolidar_var_total_no_limite_exato_e_ok():
    """A formula original usa > estrito (IF(D>E,...)): empatar com o limite
    conta como OK, nao EXCEDIDO -- caso de borda explicito do discovery."""
    carteira = calcular_var_individual(calcular_exposicao(_carteira_simples()), 1.65)
    var_total = carteira["var_individual"].sum()
    resultado = consolidar_var_total(carteira, limite_var=var_total)
    assert (resultado["status"] == "OK").all()


def test_montar_relatorio_schema():
    carteira = consolidar_var_total(
        calcular_var_individual(calcular_exposicao(_carteira_simples()), 1.65), limite_var=1.0
    )
    relatorio = montar_relatorio(carteira)
    assert list(relatorio.columns) == [
        "ativo",
        "exposicao",
        "var_individual",
        "var_total",
        "limite_var",
        "status",
    ]
