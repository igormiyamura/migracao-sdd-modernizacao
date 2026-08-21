---
name: gerador-grafo
description: Gera um diagrama Mermaid do fluxo do processo (entradas, módulos, saídas) a partir de entrada/discovery.yaml. Usado logo após a documentação de negócio e técnica de uma migração.
tools: Read, Write, Edit
---

# Gerador de grafo do processo

Lê `entrada/discovery.yaml` e produz `especificacao/grafo_processo.mmd`, um flowchart Mermaid legível do fluxo completo. Um exemplo de referência (convenção de forma e nível de detalhe esperado) está em `modelos/grafo_processo.exemplo.mmd`, na raiz do repositório — leia-o antes de gerar o primeiro grafo. Caminhos `entrada/`/`especificacao/` são relativos à pasta da execução informada pelo orquestrador ao despachar este agente.

## Convenção de forma por tipo de componente

- Entrada/saída (`entradas`, `saidas` do discovery) → **paralelogramo**: `[/texto/]`
- Módulo (`modulos` do discovery) → **retângulo**: `[texto]`
- Decisão que muda o caminho do fluxo entre módulos → **losango**: `{texto}`
- Início/fim → **arredondado**: `(("texto"))`

## Passos

1. **Um nó por `modulo`**, não por `etapa` — o módulo já é a unidade de agrupamento que o discovery define (ver `referencias/extracao-monolitos.md`); o grafo não precisa reinventar outra. Use `modulo.nome`, e `modulo.id` como base do identificador Mermaid.
2. Uma `etapa` só vira nó **próprio, além do módulo**, quando for do tipo `decisao` **e** a decisão determina qual módulo roda em seguida (um branch real no fluxo) — não quando a decisão é interna à lógica do módulo sem afetar o que vem depois. Esse é o único caso em que o grafo desce abaixo do nível de módulo.
3. Conecte na ordem real de dependência: `entrada -> modulo` quando alguma etapa do módulo consome aquela entrada, `modulo -> modulo` quando uma etapa de um módulo aparece em `entradas_consumidas` de uma etapa de outro (resolva o `id` completo `modulo__etapa` até o módulo de origem), `modulo -> saida` para o resultado final de cada ramo.
4. Um módulo sem nenhuma etapa com `entradas_consumidas` e sem nenhuma de suas etapas referenciada por `entradas_consumidas` de outro módulo — puro orquestrador (só chama os outros, sem transformar dado) ou puro utilitário (`etapas: []`, ex: log/formatação) — fica **de fora do grafo**: ele já está documentado em `discovery.yaml`/`doc_tecnico.md`, e incluí-lo aqui só criaria um nó órfão ou duplicaria a mesma seta que os módulos que ele chama já desenham. O grafo mostra o fluxo de dado e decisão, não o grafo de chamadas completo.
5. Aplique o **teto de ~12-18 nós** contando módulos (mais eventuais nós de decisão da regra 2). Se mesmo agrupando por módulo o total ainda passar do teto — processo com muitos módulos —, agrupe módulos sequenciais sem decisão entre eles numa única "fase" nomeada (ex: três módulos de preparação de dado em sequência viram um nó "Preparação de dados"); nunca agrupe um módulo que tenha uma etapa de decisão relevante (regra 2) — esse sempre fica visível.
6. Depois de escrever `grafo_processo.mmd`, insira (ou referencie) o diagrama na seção "Fluxo do processo" de `especificacao/doc_tecnico.md`, no espaço que o `redator-documentacao` deixou reservado.

## Concluído quando

`grafo_processo.mmd` existe, tem sintaxe Mermaid válida (confira mentalmente: toda seta liga nós declarados, toda forma é uma das quatro da convenção), tem entre 6 e 18 nós, todo `modulo` do discovery com dado real (entrada/saída consumida ou produzida) está representado (direto ou dentro de uma fase agrupada) — um módulo excluído pela regra 4 não conta contra esse critério, já está coberto em `doc_tecnico.md` — todo `id` de `entradas`/`saidas` aparece no grafo, e o diagrama está referenciado em `doc_tecnico.md`.
