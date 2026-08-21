"""Roda o processo migrado de ponta a ponta e compara o output contra o
baseline legado (entrada/amostra_saida/). Ver .claude/agents/homologador.md.

O conector de e-mail é substituído por um stub nesta execução de exemplo,
pela mesma razão do primeiro exemplo (sem credencial O365 real neste
ambiente) -- só o caminho do log CSV é homologado; o roteamento de alertas
por severidade já está coberto pelos testes unitários de
logica/modulo_notificacao.py.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

RAIZ_EXECUCAO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_EXECUCAO / "src"))

import pandas as pd  # noqa: E402

from enquadramento_limites_renda_fixa.config import carregar_config  # noqa: E402
from enquadramento_limites_renda_fixa.fluxo import executar  # noqa: E402

TOLERANCIA = 1e-6


def main() -> None:
    config = carregar_config(RAIZ_EXECUCAO / "config.yaml")

    alertas_enviados = []

    def _stub_enviar(destinatarios, assunto, corpo, anexos=None, credencial="padrao"):
        alertas_enviados.append({"destinatarios": destinatarios, "assunto": assunto})

    with patch("conectores.email.enviar", side_effect=_stub_enviar):
        config.caminho_posicoes = str(RAIZ_EXECUCAO / config.caminho_posicoes)
        config.caminho_limites = str(RAIZ_EXECUCAO / config.caminho_limites)
        config.caminho_log = str(RAIZ_EXECUCAO / config.caminho_log)
        executar(config)

    novo = pd.read_csv(config.caminho_log)
    baseline = pd.read_csv(RAIZ_EXECUCAO / "entrada" / "amostra_saida" / "log_enquadramento.csv")

    novo = novo.set_index("book").sort_index()
    baseline = baseline.set_index("book").sort_index()

    divergencias = []
    for chave in set(baseline.index) | set(novo.index):
        if chave not in novo.index:
            divergencias.append((chave, "(linha inteira)", "presente", "faltante", None))
            continue
        if chave not in baseline.index:
            divergencias.append((chave, "(linha inteira)", "ausente", "extra", None))
            continue
        for coluna in baseline.columns:
            valor_legado = baseline.loc[chave, coluna]
            valor_novo = novo.loc[chave, coluna]
            try:
                diferenca = abs(float(valor_novo) - float(valor_legado))
                if diferenca > TOLERANCIA:
                    divergencias.append((chave, coluna, valor_legado, valor_novo, diferenca))
            except (TypeError, ValueError):
                if str(valor_legado) != str(valor_novo):
                    divergencias.append((chave, coluna, valor_legado, valor_novo, None))

    veredito = "REPROVADO" if divergencias else "APROVADO"

    print(f"linhas comparadas: {len(baseline)}")
    print(f"divergencias: {len(divergencias)}")
    print(f"alertas de e-mail disparados: {len(alertas_enviados)}")
    for alerta in alertas_enviados:
        print(f"  -> para={alerta['destinatarios']} assunto={alerta['assunto']!r}")
    print(f"veredito: {veredito}")
    if divergencias:
        print("detalhe das divergencias:")
        for chave, coluna, legado, novo_valor, diff in divergencias:
            print(f"  {chave} / {coluna}: legado={legado} novo={novo_valor} diff={diff}")


if __name__ == "__main__":
    main()
