"""Regra de negócio do módulo `classe_limite` de entrada/discovery.yaml
(origem: ClasseLimite.cls). Mantém o mesmo agrupamento dado+cálculo do VBA
original (uma `Property` por cálculo), aqui como uma dataclass com métodos."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Limite:
    book: str
    valor_limite: float
    valor_utilizado: float

    def percentual_utilizado(self) -> float:
        """PercentualUtilizado = ValorUtilizado / ValorLimite, 0 se
        ValorLimite = 0 (não erro de divisão).

        Original: Property Get PercentualUtilizado (discovery.yaml, etapa
        classe_limite__calcular_percentual)."""
        if self.valor_limite == 0:
            return 0.0
        return self.valor_utilizado / self.valor_limite

    def status(self, limiar_alerta: float, limiar_excedido: float) -> str:
        """EXCEDIDO se percentual > limiar_excedido; ALERTA se entre
        limiar_alerta (inclusive) e limiar_excedido (inclusive); OK abaixo
        de limiar_alerta.

        Original: Property Get Status, limiares hardcoded em 1.0/0.8
        (discovery.yaml, etapa classe_limite__classificar_status) -- aqui
        recebidos de config.yaml, não hardcoded."""
        percentual = self.percentual_utilizado()
        if percentual > limiar_excedido:
            return "EXCEDIDO"
        if percentual >= limiar_alerta:
            return "ALERTA"
        return "OK"
