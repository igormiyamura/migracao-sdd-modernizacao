#!/usr/bin/env python
"""Pré-processamento determinístico de um workflow Alteryx (.yxmd/.yxwz/.yxmc)
para extração de discovery -- ver
.claude/skills/migrar-processo/referencias/extracao-monolitos.md, seção 1.

Faz o parse do XML diretamente (não abre o Designer) e produz uma lista
compacta de nós (tipo de ferramenta, configuração relevante) e conexões --
o grafo de execução real, não a ordem em que os nós aparecem no XML.

Config de cada ferramenta é achatada genericamente (caminho de tag -> texto),
já que o schema interno varia por tipo de ferramenta e por versão do
Designer -- mais robusto que tentar mapear cada tipo de ferramenta
individualmente. Ferramentas cujo Plugin contém "Python" são marcadas com
`python_embutido: true` e o conteúdo bruto da configuração é preservado
inteiro (sem achatamento) em `payload_python`, para o extrator tratar como
um módulo Python à parte -- ver extracao-monolitos.md, seção 2. Ferramentas
de macro (Plugin contém "Macro") são marcadas com `macro: true`; o extrator
decide se abre o arquivo de macro referenciado separadamente.

Uso: python extrair_alteryx.py <workflow.yxmd|.yxwz|.yxmc>
Saída: YAML no stdout.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


def _achatar_configuracao(elemento: ET.Element, prefixo: str = "") -> dict:
    """Reduz uma sub-árvore XML a um dict {caminho_de_tag: texto}, mantendo
    só folhas com texto não vazio -- suficiente para capturar expressões,
    caminhos de arquivo, nomes de campo, sem precisar conhecer o schema de
    cada tipo de ferramenta."""
    achatado = {}
    filhos = list(elemento)
    if not filhos:
        texto = (elemento.text or "").strip()
        if texto:
            achatado[prefixo or elemento.tag] = texto
        return achatado

    for filho in filhos:
        caminho = f"{prefixo}.{filho.tag}" if prefixo else filho.tag
        achatado.update(_achatar_configuracao(filho, caminho))
    return achatado


def _extrair_no(node: ET.Element) -> dict:
    tool_id = node.get("ToolID")
    gui = node.find("GuiSettings")
    plugin = gui.get("Plugin", "") if gui is not None else ""

    propriedades = node.find("Properties")
    config = propriedades.find("Configuration") if propriedades is not None else None
    anotacao_el = propriedades.find("Annotation") if propriedades is not None else None
    anotacao = (
        anotacao_el.findtext("AnnotationText", default="").strip()
        if anotacao_el is not None
        else ""
    )

    eh_python = "python" in plugin.lower()
    eh_macro = "macro" in plugin.lower()

    resultado = {
        "tool_id": tool_id,
        "plugin": plugin,
        "anotacao": anotacao or None,
        "python_embutido": eh_python,
        "macro": eh_macro,
    }

    if config is None:
        return resultado

    if eh_python:
        resultado["payload_python"] = ET.tostring(config, encoding="unicode")
    else:
        resultado["configuracao"] = _achatar_configuracao(config)

    return resultado


def extrair(caminho: Path) -> dict:
    arvore = ET.parse(caminho)
    raiz = arvore.getroot()

    nos = {}
    nodes_el = raiz.find("Nodes")
    for node in (nodes_el.findall("Node") if nodes_el is not None else []):
        info = _extrair_no(node)
        nos[info["tool_id"]] = info

    conexoes = []
    connections_el = raiz.find("Connections")
    for conn in (connections_el.findall("Connection") if connections_el is not None else []):
        origem = conn.find("Origin")
        destino = conn.find("Destination")
        conexoes.append(
            {
                "origem_tool_id": origem.get("ToolID") if origem is not None else None,
                "origem_conexao": origem.get("Connection") if origem is not None else None,
                "destino_tool_id": destino.get("ToolID") if destino is not None else None,
                "destino_conexao": destino.get("Connection") if destino is not None else None,
            }
        )

    ferramentas_python = [tid for tid, info in nos.items() if info["python_embutido"]]

    return {
        "arquivo": str(caminho),
        "total_ferramentas": len(nos),
        "ferramentas_python_embutido": ferramentas_python,
        "nos": nos,
        "conexoes": conexoes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("caminho", type=Path)
    args = parser.parse_args()

    if not args.caminho.exists():
        print(f"erro: arquivo não encontrado: {args.caminho}", file=sys.stderr)
        raise SystemExit(1)

    resultado = extrair(args.caminho)
    yaml.dump(resultado, sys.stdout, allow_unicode=True, sort_keys=False, width=100)


if __name__ == "__main__":
    main()
