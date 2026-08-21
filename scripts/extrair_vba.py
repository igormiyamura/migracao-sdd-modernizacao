#!/usr/bin/env python
"""Pré-processamento determinístico de macros VBA para extração de discovery
-- ver .claude/skills/migrar-processo/referencias/extracao-monolitos.md,
seção 1.

Aceita um arquivo Excel com macro (.xlsm/.xls, via `oletools.olevba` -- não
abre o Excel) ou uma pasta com módulos já exportados (.bas/.cls/.frm). Para
cada módulo/classe, lista a assinatura e o corpo de cada Sub/Function/
Property, e um grafo simples de chamadas entre eles (quem chama quem) --
é o que permite ao extrator tratar cada módulo como uma unidade e navegar
dependência entre eles sem reler o arquivo inteiro.

Uso: python extrair_vba.py <arquivo.xlsm | pasta_com_modulos>
Saída: YAML no stdout.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

PADRAO_ASSINATURA = re.compile(
    r"^\s*(?P<visibilidade>Public|Private|Friend)?\s*"
    r"(?P<tipo>Sub|Function|Property\s+(?:Get|Let|Set))\s+"
    r"(?P<nome>\w+)\s*\((?P<parametros>[^)]*)\)"
    r"(?:\s+As\s+(?P<retorno>\w+))?",
    re.IGNORECASE,
)
PADRAO_FIM = re.compile(r"^\s*End\s+(Sub|Function|Property)", re.IGNORECASE)


def _extrair_procedimentos(codigo: str) -> list[dict]:
    linhas = codigo.splitlines()
    procedimentos = []
    atual = None

    for numero, linha in enumerate(linhas):
        m = PADRAO_ASSINATURA.match(linha)
        if m and atual is None:
            atual = {
                "nome": m.group("nome"),
                "tipo": m.group("tipo").title(),
                "visibilidade": (m.group("visibilidade") or "Public").title(),
                "parametros": m.group("parametros").strip(),
                "retorno": m.group("retorno"),
                "linha_inicio": numero + 1,
                "corpo": [linha],
            }
            continue
        if atual is not None:
            atual["corpo"].append(linha)
            if PADRAO_FIM.match(linha):
                atual["linha_fim"] = numero + 1
                atual["corpo"] = "\n".join(atual["corpo"])
                procedimentos.append(atual)
                atual = None

    return procedimentos


def _grafo_chamadas(modulos: dict[str, list[dict]]) -> None:
    """Preenche `chama` em cada procedimento com os nomes de outros
    procedimentos (de qualquer módulo) referenciados no corpo dele."""
    todos_nomes = {
        proc["nome"] for procs in modulos.values() for proc in procs
    }
    for procs in modulos.values():
        for proc in procs:
            corpo_sem_assinatura = proc["corpo"]
            chamadas = set()
            for nome in todos_nomes:
                if nome == proc["nome"]:
                    continue
                if re.search(rf"\b{re.escape(nome)}\b", corpo_sem_assinatura):
                    chamadas.add(nome)
            proc["chama"] = sorted(chamadas)


def _de_arquivo_xlsm(caminho: Path) -> dict[str, str]:
    from oletools.olevba import VBA_Parser

    parser = VBA_Parser(str(caminho))
    modulos = {}
    for (_filename, _stream_path, vba_filename, vba_code) in parser.extract_macros():
        if vba_code and vba_code.strip():
            modulos[vba_filename] = vba_code
    parser.close()
    return modulos


def _de_pasta_exportada(caminho: Path) -> dict[str, str]:
    modulos = {}
    for arquivo in sorted(caminho.glob("*.[bB][aA][sS]")) + sorted(
        caminho.glob("*.[cC][lL][sS]")
    ) + sorted(caminho.glob("*.[fF][rR][mM]")):
        modulos[arquivo.name] = arquivo.read_text(encoding="utf-8", errors="replace")
    return modulos


def extrair(caminho: Path) -> dict:
    if caminho.is_dir():
        codigo_por_modulo = _de_pasta_exportada(caminho)
    elif caminho.suffix.lower() == ".bas" or caminho.suffix.lower() in (".cls", ".frm"):
        codigo_por_modulo = {caminho.name: caminho.read_text(encoding="utf-8", errors="replace")}
    else:
        codigo_por_modulo = _de_arquivo_xlsm(caminho)

    modulos_procedimentos = {
        nome: _extrair_procedimentos(codigo) for nome, codigo in codigo_por_modulo.items()
    }
    _grafo_chamadas(modulos_procedimentos)

    total_linhas = sum(codigo.count("\n") + 1 for codigo in codigo_por_modulo.values())

    return {
        "arquivo": str(caminho),
        "total_modulos": len(codigo_por_modulo),
        "total_linhas": total_linhas,
        "modulos": {
            nome: {"linhas": codigo_por_modulo[nome].count("\n") + 1, "procedimentos": procs}
            for nome, procs in modulos_procedimentos.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("caminho", type=Path)
    args = parser.parse_args()

    if not args.caminho.exists():
        print(f"erro: caminho não encontrado: {args.caminho}", file=sys.stderr)
        raise SystemExit(1)

    resultado = extrair(args.caminho)
    yaml.dump(resultado, sys.stdout, allow_unicode=True, sort_keys=False, width=100)


if __name__ == "__main__":
    main()
