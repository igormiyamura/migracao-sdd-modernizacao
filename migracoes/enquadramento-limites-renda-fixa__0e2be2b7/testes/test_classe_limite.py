"""Testes de src/enquadramento_limites_renda_fixa/logica/classe_limite.py --
ver "Estratégia de testes" em plano/plano_implementacao.md."""

from enquadramento_limites_renda_fixa.logica.classe_limite import Limite

LIMIAR_ALERTA = 0.8
LIMIAR_EXCEDIDO = 1.0


def test_percentual_utilizado():
    limite = Limite(book="X", valor_limite=1000, valor_utilizado=500)
    assert limite.percentual_utilizado() == 0.5


def test_percentual_utilizado_limite_zero_nao_gera_erro():
    limite = Limite(book="X", valor_limite=0, valor_utilizado=500)
    assert limite.percentual_utilizado() == 0.0


def test_status_ok_abaixo_do_limiar_de_alerta():
    limite = Limite(book="X", valor_limite=1000, valor_utilizado=799)
    assert limite.status(LIMIAR_ALERTA, LIMIAR_EXCEDIDO) == "OK"


def test_status_alerta_no_limiar_exato_de_80_por_cento():
    """Caso de borda: 80% exato conta como ALERTA (o >= original é inclusive)."""
    limite = Limite(book="X", valor_limite=1000, valor_utilizado=800)
    assert limite.status(LIMIAR_ALERTA, LIMIAR_EXCEDIDO) == "ALERTA"


def test_status_alerta_no_limiar_exato_de_100_por_cento():
    """Caso de borda: 100% exato ainda é ALERTA, não EXCEDIDO (o corte
    original é > estrito, não >=)."""
    limite = Limite(book="X", valor_limite=1000, valor_utilizado=1000)
    assert limite.status(LIMIAR_ALERTA, LIMIAR_EXCEDIDO) == "ALERTA"


def test_status_excedido_acima_de_100_por_cento():
    limite = Limite(book="X", valor_limite=1000, valor_utilizado=1000.01)
    assert limite.status(LIMIAR_ALERTA, LIMIAR_EXCEDIDO) == "EXCEDIDO"
