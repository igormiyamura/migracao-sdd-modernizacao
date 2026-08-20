"""Leitura/escrita de arquivo em biblioteca de documentos do SharePoint.

Implementação placeholder desta fase: usa `Office365-REST-Python-Client`
(ou equivalente) autenticado via credencial resolvida no keyring. Trocar por
outra biblioteca/backend na etapa 1.5 não muda a assinatura pública -- ver
guardrails/interface_conectores.md.
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


def ler_arquivo(site: str, biblioteca: str, caminho: str, credencial: str = "padrao") -> bytes:
    """Lê o conteúdo bruto de um arquivo em uma biblioteca de documentos do SharePoint."""
    _resolver_credencial(credencial)
    logger.info("lendo sharepoint site=%s biblioteca=%s caminho=%s", site, biblioteca, caminho)
    raise NotImplementedError(
        "Placeholder: integrar com Office365-REST-Python-Client na "
        "implementação real do processo, ou aguardar o toolkit refatorado (etapa 1.5)."
    )


def escrever_arquivo(
    site: str, biblioteca: str, caminho: str, conteudo: bytes, credencial: str = "padrao"
) -> None:
    """Escreve conteúdo bruto em uma biblioteca de documentos do SharePoint."""
    _resolver_credencial(credencial)
    logger.info("escrevendo sharepoint site=%s biblioteca=%s caminho=%s", site, biblioteca, caminho)
    raise NotImplementedError(
        "Placeholder: integrar com Office365-REST-Python-Client na "
        "implementação real do processo, ou aguardar o toolkit refatorado (etapa 1.5)."
    )
