<!--
Modelo usado pelo agente redator-documentacao para gerar especificacao/doc_negocio.md.
Público-alvo: o dono do processo e a mesa de negócio -- sem jargão técnico.
Todo conteúdo vem do discovery.yaml da execução; nada aqui é inventado. Este
documento deve valer como referência de negócio completa -- o dono do
processo lê isto (não o doc_tecnico.md) para confirmar que a migração
entendeu o processo direito, incluindo os porquês, não só os passos.
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

Narrativa em linguagem de negócio dos `modulos` de `discovery.yaml`, na ordem em que acontecem -- sem detalhe de implementação, sem os nomes técnicos de `modulo`/`etapa` (esses são unidade de extração, não algo que o dono do processo precisa reconhecer). Agrupe por trecho do processo com significado de negócio (ex: "apuração", "consolidação", "envio do relatório"), não por módulo técnico 1:1 se a divisão técnica não corresponder a uma divisão de negócio natural.

## Onde o processo agrega valor

O que cada etapa relevante *transforma em insight*, não só em dado -- a diferença entre "soma as posições" (mecânico) e "calcula o VaR consolidado, que é o número que a mesa usa para decidir se reduz exposição" (agrega valor). Para cada módulo/etapa com uma `regra_negocio` não trivial: o que ela calcula/decide, e por que esse cálculo/decisão importa para quem usa o resultado final. Esta seção existe para que o dono do processo confirme que a migração não perdeu o "porquê" de nenhum passo, só recodificou o "como".

## Regras e decisões de negócio

Tabela ou lista consolidando todo parâmetro, limiar, ou critério de decisão embutido no processo (`discovery.yaml -> etapas[].regras_negocio` de tipo `decisao`, mais qualquer valor citado em `riscos_pontos_atencao` como possivelmente hardcoded): o valor atual, o que ele controla, e se a origem/motivo da escolha é conhecida ou precisa ser confirmada com o dono do processo. Ex: "Limite de VaR = R$ 50.000 -- controla quando a mesa recebe alerta de excesso; origem do valor não identificada na fonte, confirmar com o dono do processo."

## O que o processo entrega

Para cada saída em `discovery.yaml -> saidas`:

- **{{ saida.nome }}**: enviado para {{ saida.destino }}, formato {{ saida.formato }}. {{ "Consumido por " + saida.consumido_por if saida.consumido_por }}

## Pontos de atenção

Lista de `discovery.yaml -> riscos_pontos_atencao` de natureza de negócio (o de natureza técnica vai para `doc_tecnico.md`) -- comportamentos ou dependências do processo original que merecem confirmação do dono do processo antes da migração seguir adiante.

## Glossário

Lista de `discovery.yaml -> glossario`.
