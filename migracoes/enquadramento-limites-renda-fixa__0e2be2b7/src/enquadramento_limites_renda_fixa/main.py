"""Ponto de entrada executável."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from .config import carregar_config
from .fluxo import executar


def main() -> None:
    formato_log = (
        '{"tempo": "%(asctime)s", "nivel": "%(levelname)s", '
        '"modulo": "%(name)s", "mensagem": "%(message)s"}'
    )
    logging.basicConfig(level=logging.INFO, format=formato_log)
    caminho_config = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    config = carregar_config(Path(caminho_config))
    executar(config)


if __name__ == "__main__":
    main()
