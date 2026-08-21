"""Testes de src/enquadramento_limites_renda_fixa/logica/modulo_notificacao.py."""

from enquadramento_limites_renda_fixa.logica.classe_limite import Limite
from enquadramento_limites_renda_fixa.logica.modulo_notificacao import decidir_alertas

LIMIAR_ALERTA = 0.8
LIMIAR_EXCEDIDO = 1.0
EMAIL_RISCO = "head.risco@banco.com.br"
EMAIL_MESA = "head.mesarendafixa@banco.com.br"


def test_excedido_notifica_head_de_risco():
    limites = [Limite(book="BOOK1", valor_limite=1000, valor_utilizado=1500)]
    alertas = decidir_alertas(limites, LIMIAR_ALERTA, LIMIAR_EXCEDIDO, EMAIL_RISCO, EMAIL_MESA)
    assert len(alertas) == 1
    assert alertas[0].destinatario == EMAIL_RISCO


def test_alerta_notifica_head_da_mesa():
    limites = [Limite(book="BOOK1", valor_limite=1000, valor_utilizado=850)]
    alertas = decidir_alertas(limites, LIMIAR_ALERTA, LIMIAR_EXCEDIDO, EMAIL_RISCO, EMAIL_MESA)
    assert len(alertas) == 1
    assert alertas[0].destinatario == EMAIL_MESA


def test_ok_nao_gera_nenhum_alerta():
    limites = [Limite(book="BOOK1", valor_limite=1000, valor_utilizado=100)]
    alertas = decidir_alertas(limites, LIMIAR_ALERTA, LIMIAR_EXCEDIDO, EMAIL_RISCO, EMAIL_MESA)
    assert alertas == []
