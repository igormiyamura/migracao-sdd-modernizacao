<!--
Modelo usado pelo agente redator-documentacao para gerar especificacao/doc_tecnico.md.
Público-alvo: quem faz a revisão técnica antes de produção, e quem eventualmente
faz o handoff para a Fase 2 (AWS). Todo conteúdo vem do discovery.yaml da
execução mais o que o gerador-grafo produziu. Este documento deve valer como
referência técnica completa do processo original -- alguém deve conseguir
entender a lógica de negócio e o fluxo de dados lendo só isto, sem reabrir o
arquivo de origem.
-->

# {{ processo.nome }} -- Documentação técnica

## Stack de origem

{{ origem.stack }} -- ver `entrada/origem.<ext>` para o artefato original.

## Fluxo do processo

![Grafo do processo](grafo_processo.mmd)

(o `gerador-grafo` insere o diagrama Mermaid completo aqui, ou referencia o arquivo `grafo_processo.mmd`)

Narrativa de como os módulos se encadeiam (o grafo mostra a forma, esta narrativa explica a ordem e o motivo): qual módulo dispara o quê, o que acontece em paralelo vs em sequência, onde o fluxo pode desviar (branches de decisão) e sob que condição.

## Módulos e principais funções

Para cada `modulo` em `discovery.yaml -> modulos`, nesta ordem: origem (`modulo.origem`), o que o módulo faz (`modulo.descricao`), e uma subseção por `etapa` dentro dele, com este formato:

- Título: `etapa.nome` (`etapa.tipo`)
- A `etapa.logica`, em prosa
- "Regras de negócio": uma lista com cada item de `etapa.regras_negocio`
- "Código original": um bloco de código cercado por crase tripla (com a linguagem da stack de origem — `vba`, `python`, texto puro para fórmula/expressão) contendo `etapa.codigo_original` **literal, sem reescrever ou "limpar"** — é o texto que a revisão técnica confere contra a fonte

Uma etapa sem `codigo_original` (ex: passo capturado só por entrevista) não tem bloco de código, só a narrativa. Isto é a seção mais longa e mais importante do documento: é o que substitui a necessidade de reabrir o arquivo original para entender a lógica.

## Entradas -- detalhe técnico

Para cada entrada em `discovery.yaml -> entradas`: tipo de conector (`fswcorp`/`email`/`sharepoint`/`api`/`saida_processo_legado`), localização/endpoint, formato, schema esperado (colunas, tipos) quando conhecido.

## Saídas -- detalhe técnico

Para cada saída em `discovery.yaml -> saidas`: conector de destino, formato, schema produzido, e o que consome essa saída (se for outro processo, o nome dele).

## Dependências e ambiente

Bibliotecas, versões, credenciais (por nome lógico, nunca o segredo), agendamento observado no processo original (horário, gatilho manual vs automático).

## Pontos de atenção técnicos

Comportamentos não óbvios encontrados na fonte que não são regra de negócio mas afetam a implementação -- ex: uma macro que só funciona se a aba X estiver na posição Y, uma dependência de versão específica de uma lib no C#, um workflow Alteryx que assume ordem de execução não explícita no grafo. Inclua aqui qualquer item de `discovery.yaml -> riscos_pontos_atencao` que seja de natureza técnica (o de natureza puramente de negócio vai para `doc_negocio.md`).
