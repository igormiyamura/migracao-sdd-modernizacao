"""Tipos e exceções compartilhados pela interface de conectores.

Ver guardrails/interface_conectores.md para o contrato completo. Este módulo
não é chamado diretamente por código de negócio — cada conector especializado
(fswcorp, email, sharepoint, api, processo_legado) importa daqui.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ErroConector(Exception):
    """Erro em uma operação de conector. Nunca é engolido silenciosamente
    pelo código de negócio -- ver a seção "Falhas" em guardrails/codigo.md."""


class CredencialNaoEncontrada(ErroConector):
    """A credencial lógica informada não está cadastrada no keyring desta
    máquina. Mensagem inclui o nome lógico para o analista saber o que
    cadastrar, nunca o segredo em si."""

    def __init__(self, nome_logico: str):
        super().__init__(
            f"Credencial '{nome_logico}' não encontrada no keyring desta "
            "máquina. Cadastre com: keyring.set_password('migracao-sdd-risco', "
            f"'{nome_logico}', '<segredo>')"
        )
