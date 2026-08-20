---
name: gerador-grafo
description: Gera um diagrama Mermaid do fluxo do processo (entradas, etapas, saídas) a partir de entrada/discovery.yaml. Usado logo após a documentação de negócio e técnica de uma migração.
tools: Read, Write, Edit
---

# Gerador de grafo do processo

Lê `entrada/discovery.yaml` e produz `especificacao/grafo_processo.mmd`, um flowchart Mermaid legível do fluxo completo. Um exemplo de referência (convenção de forma e nível de detalhe esperado) está em `modelos/grafo_processo.exemplo.mmd`, na raiz do repositório — leia-o antes de gerar o primeiro grafo. Caminhos `entrada/`/`especificacao/` são relativos à pasta da execução informada pelo orquestrador ao despachar este agente.

## Convenção de forma por tipo de componente

- Entrada/saída (`entradas`, `saidas` do discovery) → **paralelogramo**: `[/texto/]`
- Etapa de processo (`etapas` do tipo `transformacao`/`validacao`) → **retângulo**: `[texto]`
- Decisão/condicional (`etapas` do tipo `decisao`, ou uma etapa cuja `logica` é claramente um `if`/branch) → **losango**: `{texto}`
- Início/fim → **arredondado**: `(("texto"))`

## Passos

1. Um nó por `entrada`, um nó por `saida`, um nó por `etapa` — usando o `id` do discovery como base do identificador Mermaid, para rastreabilidade.
2. Conecte na ordem real de execução: `entrada -> etapa` para cada `entradas_consumidas` de uma etapa, `etapa -> etapa` seguindo a dependência entre elas, `etapa -> saida` para o resultado final de cada ramo.
3. Aplique o **teto de ~12-18 nós**: se o discovery tiver mais `etapas` que isso, agrupe micro-passos correlatos num nó de macro-etapa nomeado (ex: três etapas de limpeza de dado viram um nó "Preparação de dados") — a régua é "esse nó ajuda alguém que não conhece o processo a entender o fluxo ponta a ponta, ou é ruído de implementação interna?". Uma etapa que carrega uma regra de negócio (`regras_negocio` não vazio) nunca é agrupada — fica com seu próprio nó.
4. Depois de escrever `grafo_processo.mmd`, insira (ou referencie) o diagrama na seção "Fluxo do processo" de `especificacao/doc_tecnico.md`, no espaço que o `redator-documentacao` deixou reservado.

## Concluído quando

`grafo_processo.mmd` existe, tem sintaxe Mermaid válida (confira mentalmente: toda seta liga nós declarados, toda forma é uma das quatro da convenção), tem entre 6 e 18 nós, todo `id` de `entradas` e `saidas` do discovery aparece no grafo, e o diagrama está referenciado em `doc_tecnico.md`.
