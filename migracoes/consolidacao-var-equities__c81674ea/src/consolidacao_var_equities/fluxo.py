"""Orquestra: lê entradas via conectores/ -> aplica logica.py -> escreve
saídas via conectores/. Ver guardrails/interface_conectores.md -- nenhuma
chamada direta a pywin32/smbclient/O365/msal/requests aqui."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Nesta execução de exemplo, `conectores` vive no mesmo repositório
# (migracao-sdd-risco/conectores). Em um processo migrado real, o pacote é
# instalado como dependência do projeto (ex: `uv add --editable
# ../caminho/para/conectores`), não referenciado por sys.path -- feito assim
# aqui só para a árvore de exemplo poder rodar isolada.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

import conectores  # noqa: E402

from .config import ConfiguracaoProcesso  # noqa: E402
from .logica import (  # noqa: E402
    calcular_exposicao,
    calcular_var_individual,
    consolidar_var_total,
    montar_relatorio,
)

logger = logging.getLogger(__name__)


def executar(config: ConfiguracaoProcesso) -> None:
    logger.info("lendo carteira caminho=%s", config.caminho_carteira)
    carteira = conectores.fswcorp.ler_arquivo(config.caminho_carteira)

    logger.info("calculando exposicao e var individual")
    carteira = calcular_exposicao(carteira)
    carteira = calcular_var_individual(carteira, config.fator_confianca)

    logger.info("consolidando var total")
    carteira = consolidar_var_total(carteira, config.limite_var)
    relatorio = montar_relatorio(carteira)

    status = relatorio["status"].iloc[0]
    var_total = relatorio["var_total"].iloc[0]
    logger.info("resultado consolidado var_total=%.2f status=%s", var_total, status)

    logger.info("escrevendo relatorio caminho=%s", config.caminho_saida)
    conectores.fswcorp.escrever_arquivo(config.caminho_saida, relatorio, formato="csv")

    if status == "EXCEDIDO":
        logger.warning("var_total acima do limite, disparando alerta")
        conectores.email.enviar(
            destinatarios=[config.email_alerta],
            assunto="ALERTA: VaR consolidado acima do limite",
            corpo=(
                f"O VaR total da carteira Equities ({var_total:,.2f}) "
                "ultrapassou o limite configurado. Verificar exposicoes."
            ),
            credencial=config.credencial_email,
        )
