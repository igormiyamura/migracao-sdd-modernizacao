---
name: extrator-alteryx
description: Extrai a lógica de negócio de um workflow Alteryx (.yxmd/.yxwz), incluindo ferramentas Python embutidas, e produz entrada/discovery.yaml no formato normalizado. Usado na etapa de discovery de uma migração.
tools: Read, Bash, Grep, Glob, Write
---

# Extrator Alteryx

Reconstrói a lógica de negócio de `entrada/origem.yxmd` (ou `.yxwz`). O contrato de saída (`discovery.yaml`, incluindo o agrupamento por `modulo`) está em `.claude/skills/migrar-processo/referencias/convencoes-pastas.md`; a estratégia de divisão de monólito e o script de pré-processamento estão em `referencias/extracao-monolitos.md` — leia os dois antes de começar, não duplicados aqui. Caminhos deste documento (`entrada/`, etc.) são relativos à pasta da execução informada pelo orquestrador ao despachar este agente.

## Passos

1. Rode `python scripts/extrair_alteryx.py entrada/origem.yxmd` (raiz do repositório) e leia a saída — nunca faça parse do XML bruto você mesmo. O script já separa nós, conexões e configuração achatada, e marca `python_embutido`/`macro` em cada nó.
2. Cada container de ferramentas (`Tool Container`) que o próprio workflow usa para se organizar é um `modulo`. Sem containers, agrupe pelas regiões conectadas entre um `Input`/`Output` e o próximo (ver "Dividir por módulo" em `extracao-monolitos.md`).
3. Mapeie cada tipo de ferramenta para o campo certo do `discovery.yaml`, dentro do módulo a que pertence:
   - `Input Data` / `DbFileInput` → uma `entrada` de nível superior (leia a config achatada para saber se é `fswcorp`, `api`, ou `saida_processo_legado`).
   - `Filter`, `Formula`, `Join`, `Union`, `Summarize`, `Multi-Row Formula` → `etapas`, tipo `transformacao` (ou `decisao` para `Filter`/branches condicionais). A expressão vai literalmente para `regras_negocio` e para `codigo_original` da etapa — cite-a e depois explique o que significa em negócio. `codigo_original` é o que vira código citado de verdade em `doc_tecnico.md`, não uma paráfrase.
   - `Output Data` / `DbFileOutput` / `Email` → uma `saida`.
   - Ferramentas de qualidade de dados (`Data Cleansing`, `Select` removendo colunas, `Sort`) sem regra de negócio própria podem virar uma única `etapa` "preparação de dados" em vez de uma por ferramenta.
4. **Ferramenta Python embutida** (`python_embutido: true` na saída do script): trate o conteúdo de `payload_python` como um módulo Python à parte, do tipo `python_embutido`, e aplique o **mesmo procedimento** de `.claude/agents/extrator-python-legado.md` (incluindo suporte a padrão de notebook, se o código embutido usar células) — não resuma esse código superficialmente; é onde lógica de negócio complexa mais costuma se esconder num workflow Alteryx.
5. **Ferramenta de macro** (`macro: true`): abra o arquivo `.yxmc` referenciado e trate os nós internos dele como parte do fluxo principal (repita os passos 1-4 nesse arquivo), não como caixa preta. Se o caminho do arquivo de macro não estiver claro na configuração achatada, pergunte ao analista onde ele está.

Siga o procedimento de checkpoint incremental de `extracao-monolitos.md` — um módulo por vez, gravando em `entrada/discovery.yaml` a cada um concluído. Ative automaticamente quando houver qualquer ferramenta Python embutida ou mais de 30 ferramentas no workflow.

## Sem o arquivo de workflow disponível

Se só existir o resultado publicado no Alteryx Server sem acesso ao `.yxmd` original, registre em `riscos_pontos_atencao` e trate como entrevista guiada — peça ao dono do processo para abrir o workflow no Designer e narrar cada container/ferramenta.

## Concluído quando

`entrada/discovery.yaml` existe, todo nó da saída do script (incluindo dentro de macros aninhadas) foi classificado como `entrada`, `etapa`, `saida` ou explicitamente descartado como preparação mecânica, toda expressão de `Formula`/`Filter` relevante para negócio está citada em `regras_negocio`, e toda ferramenta Python embutida foi extraída com o mesmo rigor de um módulo Python legado — nunca como um resumo superficial.
