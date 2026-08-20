# Guardrails de código

Referência consultada pelo agente `implementador-python` ao gerar código, e pelo `planejador` ao desenhar o plano de implementação. Todo código Python produzido por uma migração segue este padrão — é o que torna os processos migrados previsíveis o suficiente para a Fase 2 (handoff para AWS) sem retrabalho de padronização.

## Stack

- **Python 3.11.** Não usar sintaxe/typing de versões mais novas.
- **`uv`** para dependências e ambiente virtual — todo processo migrado tem seu próprio `pyproject.toml` (copiado de `modelos/pyproject_template.toml`) e seu próprio `.venv`, nunca dependências instaladas globalmente na máquina do analista.
- **Layout `src/`**: código de negócio em `src/<slug_do_processo>/`, nunca solto na raiz do projeto.
- **Config via YAML + `pydantic`**: nenhum valor de configuração (caminhos, endpoints, tolerâncias, agendamento) hardcoded no meio da lógica — sempre um modelo `pydantic` carregado de um `config.yaml` na raiz do projeto migrado.
- **Segredos via `keyring`** (cofre de credenciais do SO): nunca senha, token ou connection string em texto plano em código ou em `config.yaml`. Se o processo original tinha credencial hardcoded na planilha/macro/script, isso é um achado de `riscos_pontos_atencao` no discovery, não algo a replicar.
- **Logging estruturado**: `logging` padrão da biblioteca, formato JSON, um logger por módulo (`logging.getLogger(__name__)`), nunca `print`. Nível `INFO` para o fluxo normal do processo, `WARNING` para divergências toleráveis, `ERROR` para falhas que interrompem a execução.
- **`ruff`** para lint e formatação (substitui `black`/`flake8`/`isort` — uma ferramenta só).
- **`mypy`** para checagem de tipos — toda função pública tem assinatura tipada.
- **`pytest`** para testes — todo módulo de lógica de negócio (não os conectores de I/O) tem teste unitário cobrindo as regras de negócio extraídas no discovery.

## Nomenclatura

Identificadores de código (variáveis, funções, classes) que representam **conceitos de negócio** são nomeados em português, espelhando os termos usados no `discovery.yaml` e no `doc_negocio.md` — isso é o que torna o código legível para o dono do processo e para revisão técnica, sem precisar traduzir mentalmente. Termos técnicos/genéricos do ecossistema Python (`config`, `logger`, `client`, `df`, nomes de bibliotecas) seguem a convenção usual em inglês quando não há tradução natural — não forçar tradução de um termo técnico só por regra. Comentários, docstrings e mensagens de log são sempre em português.

## Falhas

Um processo de risco de mercado erra alto e falha visivelmente é preferível a um processo que degrada silenciosamente e produz um número errado. Nunca envolver uma chamada de conector ou um cálculo de regra de negócio em `try/except` genérico que engole a exceção — deixar a exceção propagar com uma mensagem de log que identifique a etapa e a entrada envolvida. Validação de schema de entrada (via `pydantic`) acontece assim que um dado é lido, não no meio do processamento.

## Fronteira com o toolkit de conectores

Nenhum código de negócio faz acesso direto a fswcorp, e-mail, SharePoint, API ou output de outro processo — sempre através da interface descrita em `guardrails/interface_conectores.md`, importada do pacote `conectores/`. Ver esse documento antes de escrever qualquer etapa de entrada/saída.

## Estrutura mínima de um processo migrado

```
src/<slug_do_processo>/
  __init__.py
  config.py          # modelo pydantic + carregamento do config.yaml
  logica.py           # regras de negócio (uma função por etapa do discovery.yaml)
  fluxo.py            # orquestra: lê entradas via conectores/ -> aplica logica.py -> escreve saídas via conectores/
  main.py             # ponto de entrada executável
config.yaml
pyproject.toml
testes/
  test_logica.py
```
