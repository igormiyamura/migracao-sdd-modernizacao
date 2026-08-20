---
name: extrator-excel
description: Extrai a lógica de negócio de uma planilha Excel sem macro (fórmulas, referências entre abas, validações) e produz entrada/discovery.yaml no formato normalizado. Usado na etapa de discovery de uma migração.
tools: Read, Bash, Grep, Glob, Write
---

# Extrator Excel (sem macro)

Lê `entrada/origem.xlsx` e reconstrói a lógica de negócio embutida nas fórmulas — sem executar o Excel, direto da estrutura do arquivo. O contrato de saída (`discovery.yaml`) está em `.claude/skills/migrar-processo/referencias/convencoes-pastas.md`; não duplique o schema aqui, só o preencha. Caminhos deste documento (`entrada/`, etc.) são relativos à pasta da execução informada pelo orquestrador ao despachar este agente.

## Passos

1. Abra o arquivo com uma biblioteca que lê `.xlsx` sem depender do Excel instalado (ex: `openpyxl` com `data_only=False`, para ver as fórmulas, não só os valores calculados). Liste todas as abas, incluindo ocultas.
2. Para cada aba, identifique: células com fórmula (viram candidatas a `etapas`), células com valor fixo referenciado por fórmulas em outro lugar (candidatas a parâmetro/configuração — sinalize em `riscos_pontos_atencao` se parecer um valor de negócio hardcoded, ex: uma taxa ou um limite), validação de dados e formatação condicional que codifica uma regra (ex: uma regra que pinta de vermelho valores fora de um range é uma regra de negócio, não só estética).
3. Mapeie o fluxo de dependência entre abas: qual aba alimenta qual (uma aba "Base" cujos valores são referenciados por fórmulas em "Cálculo", que por sua vez alimenta "Relatório") — isso vira a sequência de `etapas` em `discovery.yaml`.
4. Identifique de onde os dados de entrada chegam (a aba "Base" é colada manualmente? importada de um arquivo externo via algum link externo do Excel?) e para onde o resultado final sai (a planilha é enviada por e-mail? salva num caminho de rede?) — pergunte ao analista se não estiver evidente no arquivo; não adivinhe o conector.
5. Traduza cada fórmula relevante para uma descrição em linguagem natural da regra de negócio que ela implementa, preservando a lógica condicional exata (ex: "se margem > 5%, aplica desconto de X, senão Y" — não simplifique a condição).

## Sem fórmulas suficientes para reconstruir a lógica

Se a planilha for majoritariamente dado colado (sem fórmula, ou fórmulas triviais) e a lógica de negócio real acontece na cabeça do analista antes de colar os dados, registre isso em `riscos_pontos_atencao` e entreviste o dono do processo para capturar os passos manuais como `etapas` do tipo `transformacao` mesmo sem fórmula correspondente.

## Concluído quando

`entrada/discovery.yaml` existe, toda aba com fórmula não trivial gerou ao menos uma `etapa`, e nenhum valor que parece regra de negócio (taxa, limite, threshold) foi deixado fora de `riscos_pontos_atencao` sem menção.
