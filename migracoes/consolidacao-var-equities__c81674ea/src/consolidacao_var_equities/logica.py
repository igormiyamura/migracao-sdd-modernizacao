"""Regras de negócio extraídas em entrada/discovery.yaml -- uma função por
etapa. Sem I/O aqui: quem lê/escreve dado é fluxo.py, via conectores/."""

from __future__ import annotations

import pandas as pd


def calcular_exposicao(carteira: pd.DataFrame) -> pd.DataFrame:
    """Exposicao = Quantidade * PrecoUnitario, por ativo.

    Fórmula original: Calculo!B = Carteira!B*Carteira!C (discovery.yaml,
    etapa calcular_exposicao)."""
    resultado = carteira.copy()
    resultado["exposicao"] = resultado["quantidade"] * resultado["preco_unitario"]
    return resultado


def calcular_var_individual(carteira: pd.DataFrame, fator_confianca: float) -> pd.DataFrame:
    """VaRIndividual = Exposicao * Volatilidade * FatorConfianca.

    Fórmula original: Calculo!C = B*Carteira!D*Parametros!$B$2 (discovery.yaml,
    etapa calcular_var_individual)."""
    resultado = carteira.copy()
    resultado["var_individual"] = (
        resultado["exposicao"] * resultado["volatilidade"] * fator_confianca
    )
    return resultado


def consolidar_var_total(carteira: pd.DataFrame, limite_var: float) -> pd.DataFrame:
    """VaRTotal = soma do VaR individual de todos os ativos; Status =
    EXCEDIDO se VaRTotal > LimiteVaR, senão OK (estrito, replica o IF
    original -- empatar com o limite conta como OK).

    Fórmula original: Relatorio!D = SUM(Calculo!C2:C6); Relatorio!F =
    IF(D>E,"EXCEDIDO","OK") (discovery.yaml, etapa consolidar_var_total)."""
    resultado = carteira.copy()
    var_total = resultado["var_individual"].sum()
    resultado["var_total"] = var_total
    resultado["limite_var"] = limite_var
    resultado["status"] = "EXCEDIDO" if var_total > limite_var else "OK"
    return resultado


def montar_relatorio(carteira: pd.DataFrame) -> pd.DataFrame:
    """Monta o relatório final no schema de saída
    (ativo,exposicao,var_individual,var_total,limite_var,status), mesmo
    schema denormalizado do CSV original."""
    colunas = ["ativo", "exposicao", "var_individual", "var_total", "limite_var", "status"]
    return carteira[colunas]
