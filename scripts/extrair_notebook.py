#!/usr/bin/env python
"""Pré-processamento determinístico de um script ou notebook Python para
extração de discovery -- ver
.claude/skills/migrar-processo/referencias/extracao-monolitos.md, seção 1.

Para um notebook (.ipynb): lê o JSON e extrai células de código e markdown
em ordem, descartando outputs (prints longos, imagens em base64, HTML de
DataFrame) -- eles não carregam lógica de negócio e são a maior fonte de
peso morto num notebook. Sinaliza células cujo `execution_count` não é
estritamente maior que o maior já visto até ali -- indício de que o
analista rodou células fora de ordem, e a ordem visual do notebook pode não
refletir a ordem real de execução que produziu o último output correto.

Para um script `.py`: passa o conteúdo direto, sem transformação -- não há
metadata/output para descartar.

Uso: python extrair_notebook.py <arquivo.ipynb|arquivo.py>
Saída: YAML no stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml


def _texto_celula(celula: dict) -> str:
    fonte = celula.get("source", "")
    return "".join(fonte) if isinstance(fonte, list) else fonte


def extrair_notebook(caminho: Path) -> dict:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    celulas_out = []
    maior_execution_count_visto = 0

    for indice, celula in enumerate(dados.get("cells", [])):
        tipo = celula.get("cell_type")
        conteudo = _texto_celula(celula)
        if not conteudo.strip():
            continue

        entrada = {"indice": indice, "tipo": tipo, "conteudo": conteudo}

        if tipo == "code":
            execution_count = celula.get("execution_count")
            entrada["execution_count"] = execution_count
            if execution_count is not None:
                entrada["fora_de_ordem"] = execution_count <= maior_execution_count_visto
                maior_execution_count_visto = max(maior_execution_count_visto, execution_count)
            else:
                entrada["fora_de_ordem"] = None  # célula nunca executada

        celulas_out.append(entrada)

    return {
        "arquivo": str(caminho),
        "tipo": "notebook",
        "total_celulas": len(celulas_out),
        "tem_celula_fora_de_ordem": any(c.get("fora_de_ordem") for c in celulas_out),
        "celulas": celulas_out,
    }


def extrair_script(caminho: Path) -> dict:
    codigo = caminho.read_text(encoding="utf-8", errors="replace")
    return {
        "arquivo": str(caminho),
        "tipo": "script",
        "total_linhas": codigo.count("\n") + 1,
        "codigo": codigo,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("caminho", type=Path)
    args = parser.parse_args()

    if not args.caminho.exists():
        print(f"erro: arquivo não encontrado: {args.caminho}", file=sys.stderr)
        raise SystemExit(1)

    if args.caminho.suffix.lower() == ".ipynb":
        resultado = extrair_notebook(args.caminho)
    else:
        resultado = extrair_script(args.caminho)

    yaml.dump(resultado, sys.stdout, allow_unicode=True, sort_keys=False, width=100)


if __name__ == "__main__":
    main()
