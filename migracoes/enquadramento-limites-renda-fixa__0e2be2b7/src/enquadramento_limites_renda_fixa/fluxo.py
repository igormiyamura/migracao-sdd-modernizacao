"""Orquestra: lê entradas via conectores/ -> aplica logica/ -> escreve
saídas via conectores/. Ver guardrails/interface_conectores.md. Equivalente
ao ModuloPrincipal.bas original (RodarApuracao) -- a orquestração em si não
tem regra de negócio, por isso vive aqui e não em logica/."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Nesta execução de exemplo, `conectores` vive no mesmo repositório -- em um
# processo migrado real, o pacote é instalado como dependência editável do
# projeto (ver guardrails/interface_conectores.md), não referenciado por
# sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

import conectores  # noqa: E402

from .config import ConfiguracaoProcesso  # noqa: E402
from .logica.classe_limite import Limite  # noqa: E402
from .logica.modulo_consolidacao import consolidar_dv01_por_book  # noqa: E402
from .logica.modulo_enquadramento import avaliar_enquadramento  # noqa: E402
from .logica.modulo_notificacao import decidir_alertas, montar_log  # noqa: E402

logger = logging.getLogger(__name__)


def executar(config: ConfiguracaoProcesso) -> None:
    logger.info("lendo posicoes caminho=%s", config.caminho_posicoes)
    posicoes = conectores.fswcorp.ler_arquivo(config.caminho_posicoes)

    logger.info("lendo limites caminho=%s", config.caminho_limites)
    limites_config = conectores.fswcorp.ler_arquivo(config.caminho_limites)

    logger.info("consolidando dv01 por book")
    dv01_por_book = consolidar_dv01_por_book(posicoes)

    logger.info("avaliando enquadramento")
    limites: list[Limite] = avaliar_enquadramento(limites_config, dv01_por_book)

    log = montar_log(limites, config.limiar_alerta, config.limiar_excedido)
    logger.info("escrevendo log caminho=%s", config.caminho_log)
    conectores.fswcorp.escrever_arquivo(config.caminho_log, log, formato="csv")

    alertas = decidir_alertas(
        limites,
        config.limiar_alerta,
        config.limiar_excedido,
        config.email_head_risco,
        config.email_head_mesa,
    )
    for alerta in alertas:
        logger.warning(
            "disparando alerta destinatario=%s assunto=%s", alerta.destinatario, alerta.assunto
        )
        conectores.email.enviar(
            destinatarios=[alerta.destinatario],
            assunto=alerta.assunto,
            corpo=alerta.corpo,
            credencial=config.credencial_email,
        )
