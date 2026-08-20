<!--
Modelo usado pelo agente redator-documentacao para gerar especificacao/doc_negocio.md.
Público-alvo: o dono do processo e a mesa de negócio -- sem jargão técnico.
Todo conteúdo vem do discovery.yaml da execução; nada aqui é inventado.
-->

# {{ processo.nome }}

**Mesa/área**: {{ processo.mesa }}
**Dono do processo**: {{ processo.dono }}
**Frequência**: {{ processo.frequencia }}
**Criticidade**: {{ processo.criticidade }}

## Objetivo

{{ processo.objetivo_negocio }}

## O que o processo recebe

Para cada entrada em `discovery.yaml -> entradas`, uma entrada nesta lista:

- **{{ entrada.nome }}** ({{ entrada.tipo }}): {{ entrada.descricao }}. Atualizado {{ entrada.frequencia_atualizacao }}.

## O que o processo faz

Narrativa em linguagem de negócio das etapas em `discovery.yaml -> etapas`, na ordem em que acontecem -- sem detalhe de implementação, focada no *porquê* de cada etapa e nas regras de negócio que ela aplica (`regras_negocio`).

## O que o processo entrega

Para cada saída em `discovery.yaml -> saidas`:

- **{{ saida.nome }}**: enviado para {{ saida.destino }}, formato {{ saida.formato }}. {{ "Consumido por " + saida.consumido_por if saida.consumido_por }}

## Pontos de atenção

Lista de `discovery.yaml -> riscos_pontos_atencao` -- comportamentos ou dependências do processo original que merecem confirmação do dono do processo antes da migração seguir adiante.

## Glossário

Lista de `discovery.yaml -> glossario`.
