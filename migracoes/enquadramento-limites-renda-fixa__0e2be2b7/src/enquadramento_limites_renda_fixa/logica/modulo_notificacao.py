"""Regra de negócio do módulo `modulo_notificacao` de
entrada/discovery.yaml (origem: ModuloNotificacao.bas)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .classe_limite import Limite


@dataclass
class Alerta:
    destinatario: str
    assunto: str
    corpo: str


def montar_log(
    limites: list[Limite], limiar_alerta: float, limiar_excedido: float
) -> pd.DataFrame:
    """Uma linha por Limite, no schema original book,limite,utilizado,
    percentual,status.

    Original: Sub NotificarEExportar, trecho de escrita do CSV
    (discovery.yaml, etapa modulo_notificacao__exportar_log)."""
    linhas = [
        {
            "book": limite.book,
            "limite": limite.valor_limite,
            "utilizado": limite.valor_utilizado,
            "percentual": limite.percentual_utilizado(),
            "status": limite.status(limiar_alerta, limiar_excedido),
        }
        for limite in limites
    ]
    return pd.DataFrame(linhas)


def decidir_alertas(
    limites: list[Limite],
    limiar_alerta: float,
    limiar_excedido: float,
    email_head_risco: str,
    email_head_mesa: str,
) -> list[Alerta]:
    """EXCEDIDO -> e-mail para o head de risco; ALERTA -> e-mail para o head
    da mesa; OK -> nenhum e-mail.

    Original: bloco If/ElseIf em NotificarEExportar + Sub EnviarEmail
    (discovery.yaml, etapa modulo_notificacao__notificar_por_severidade)."""
    alertas = []
    for limite in limites:
        status = limite.status(limiar_alerta, limiar_excedido)
        corpo = (
            f"Book {limite.book}: utilizado {limite.percentual_utilizado():.1%} "
            f"do limite de {limite.valor_limite}"
        )
        if status == "EXCEDIDO":
            alertas.append(
                Alerta(email_head_risco, f"EXCEDIDO: limite de {limite.book}", corpo)
            )
        elif status == "ALERTA":
            alertas.append(
                Alerta(email_head_mesa, f"ALERTA: limite de {limite.book}", corpo)
            )
    return alertas
