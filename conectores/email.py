"""Envio e leitura de e-mail corporativo.

Implementação placeholder desta fase: usa a biblioteca `O365` (Microsoft
Graph) autenticada via credencial resolvida no keyring pelo nome lógico.
Trocar por outra biblioteca/backend na etapa 1.5 não muda a assinatura
pública -- ver guardrails/interface_conectores.md.
"""

from __future__ import annotations

import keyring

from .base import CredencialNaoEncontrada, logger

_SERVICO_KEYRING = "migracao-sdd-risco"


def _resolver_credencial(nome_logico: str) -> str:
    segredo = keyring.get_password(_SERVICO_KEYRING, nome_logico)
    if segredo is None:
        raise CredencialNaoEncontrada(nome_logico)
    return segredo


def enviar(
    destinatarios: list[str],
    assunto: str,
    corpo: str,
    anexos: list[str] | None = None,
    credencial: str = "padrao",
) -> None:
    """Envia um e-mail. `credencial` é o nome lógico cadastrado no keyring,
    nunca o segredo em si -- ver base.CredencialNaoEncontrada."""
    _resolver_credencial(credencial)
    logger.info(
        "enviando e-mail destinatarios=%s assunto=%s anexos=%s",
        destinatarios,
        assunto,
        anexos or [],
    )
    # TODO(etapa 1.5): substituir pelo cliente real do toolkit refatorado.
    # from O365 import Account
    # account = Account((client_id, segredo)); ...
    raise NotImplementedError(
        "Placeholder: integrar com O365/Graph API na implementação real do "
        "processo, ou aguardar o toolkit refatorado (etapa 1.5)."
    )


def ler_anexos(pasta: str, filtro: str, credencial: str = "padrao") -> list[bytes]:
    """Lê anexos de mensagens em `pasta` que casam com `filtro` (assunto ou remetente)."""
    _resolver_credencial(credencial)
    logger.info("lendo anexos pasta=%s filtro=%s", pasta, filtro)
    raise NotImplementedError(
        "Placeholder: integrar com O365/Graph API na implementação real do "
        "processo, ou aguardar o toolkit refatorado (etapa 1.5)."
    )
