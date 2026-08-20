<!--
Modelo usado pelo agente redator-documentacao para gerar especificacao/doc_tecnico.md.
Público-alvo: quem faz a revisão técnica antes de produção, e quem eventualmente
faz o handoff para a Fase 2 (AWS). Todo conteúdo vem do discovery.yaml da
execução mais o que o gerador-grafo produziu.
-->

# {{ processo.nome }} -- Documentação técnica

## Stack de origem

{{ origem.stack }} -- ver `entrada/origem.<ext>` para o artefato original.

## Fluxo do processo

![Grafo do processo](grafo_processo.mmd)

(o `gerador-grafo` insere o diagrama Mermaid completo aqui, ou referencia o arquivo `grafo_processo.mmd`)

## Entradas -- detalhe técnico

Para cada entrada em `discovery.yaml -> entradas`: tipo de conector (`fswcorp`/`email`/`sharepoint`/`api`/`saida_processo_legado`), localização/endpoint, formato, schema esperado (colunas, tipos) quando conhecido.

## Etapas -- lógica de negócio extraída

Para cada etapa em `discovery.yaml -> etapas`: a lógica (`logica`) e as regras de negócio (`regras_negocio`) tal como extraídas da fonte -- fórmulas de Excel, procedimentos VBA, ferramentas/expressões do Alteryx, métodos C#, funções Python. Esta seção é a base para o `planejador` e o `implementador-python`; deve ser específica o suficiente para alguém implementar sem reabrir o arquivo de origem.

## Saídas -- detalhe técnico

Para cada saída em `discovery.yaml -> saidas`: conector de destino, formato, schema produzido, e o que consome essa saída (se for outro processo, o nome dele).

## Dependências e ambiente

Bibliotecas, versões, credenciais (por nome lógico, nunca o segredo), agendamento observado no processo original (horário, gatilho manual vs automático).

## Pontos de atenção técnicos

Comportamentos não óbvios encontrados na fonte que não são regra de negócio mas afetam a implementação -- ex: uma macro que só funciona se a aba X estiver na posição Y, uma dependência de versão específica de uma lib no C#, um workflow Alteryx que assume ordem de execução não explícita no grafo.
