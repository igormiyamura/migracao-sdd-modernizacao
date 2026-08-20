"""Interface estável de conectores para as cinco fontes de dados recorrentes
nos processos de risco de mercado: fswcorp, email, sharepoint, api,
processo_legado.

Ver guardrails/interface_conectores.md para o contrato completo. Código de
negócio de um processo migrado importa daqui, nunca das bibliotecas por trás
(pywin32, O365, requests, ...) diretamente -- isso é o que permite trocar a
implementação (etapa 1.5, e depois a Fase 2 em AWS) sem tocar em cada
processo migrado.
"""

from . import api, email, fswcorp, processo_legado, sharepoint
from .base import CredencialNaoEncontrada, ErroConector

__all__ = [
    "api",
    "email",
    "fswcorp",
    "processo_legado",
    "sharepoint",
    "CredencialNaoEncontrada",
    "ErroConector",
]
