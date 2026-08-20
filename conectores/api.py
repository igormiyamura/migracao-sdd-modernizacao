"""Chamada HTTP autenticada a uma API interna, com retry e timeout padronizados.

Implementação desta fase: `requests` puro. Trocar por outra biblioteca/backend
na etapa 1.5 não muda a assinatura pública -- ver
guardrails/interface_conectores.md.
"""

from __future__ import annotations

import keyring
import requests

from .base import CredencialNaoEncontrada, ErroConector, logger

_SERVICO_KEYRING = "migracao-sdd-risco"
_TIMEOUT_PADRAO_S = 30
_TENTATIVAS_PADRAO = 3


def _resolver_credencial(nome_logico: str) -> str:
    segredo = keyring.get_password(_SERVICO_KEYRING, nome_logico)
    if segredo is None:
        raise CredencialNaoEncontrada(nome_logico)
    return segredo


def chamar(
    endpoint: str,
    metodo: str = "GET",
    payload: dict | None = None,
    credencial: str = "padrao",
    tentativas: int = _TENTATIVAS_PADRAO,
) -> dict:
    """Chama `endpoint` com o `metodo` HTTP informado, autenticado via
    credencial resolvida no keyring. Faz retry em falhas de rede/5xx até
    `tentativas` vezes; não faz retry em erros 4xx (erro do chamador)."""
    token = _resolver_credencial(credencial)
    headers = {"Authorization": f"Bearer {token}"}

    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.request(
                metodo, endpoint, json=payload, headers=headers, timeout=_TIMEOUT_PADRAO_S
            )
            if 400 <= resposta.status_code < 500:
                raise ErroConector(
                    f"API respondeu {resposta.status_code} para {metodo} {endpoint}: "
                    f"{resposta.text}"
                )
            resposta.raise_for_status()
            corpo: dict = resposta.json()
            return corpo
        except requests.RequestException as erro:
            ultimo_erro = erro
            logger.warning(
                "falha ao chamar api endpoint=%s tentativa=%d/%d erro=%s",
                endpoint,
                tentativa,
                tentativas,
                erro,
            )

    raise ErroConector(
        f"Falha ao chamar {metodo} {endpoint} após {tentativas} tentativas"
    ) from ultimo_erro
