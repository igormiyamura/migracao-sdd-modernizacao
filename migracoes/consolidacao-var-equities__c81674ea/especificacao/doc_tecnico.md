# Consolidação de VaR - Mesa Equities -- Documentação técnica

## Stack de origem

Excel + VBA -- ver `entrada/origem_planilha.xlsx` (fórmulas, abas Carteira/Parametros/Calculo/Relatorio) e `entrada/origem_macro.bas` (macro exportada, módulo `Modulo1`).

## Fluxo do processo

![Grafo do processo](grafo_processo.mmd)

## Entradas -- detalhe técnico

| id | tipo | localização | formato | schema |
|---|---|---|---|---|
| `carteira_equities` | manual (colado) | `origem_planilha.xlsx!Carteira` | xlsx | `Ativo (str), Quantidade (int), PrecoUnitario (float), Volatilidade (float)` |
| `parametros_risco` | manual (hardcoded) | `origem_planilha.xlsx!Parametros` | xlsx | `FatorConfianca=1.65 (B2), LimiteVaR=50000 (B3)` |

## Etapas -- lógica de negócio extraída

1. **Cálculo de exposição por ativo** (`calcular_exposicao`): `Exposicao = Quantidade * PrecoUnitario`. Fórmula original: `Calculo!B2 = Carteira!B2*Carteira!C2`, arrastada para as 5 linhas da carteira.
2. **Cálculo de VaR individual por ativo** (`calcular_var_individual`): `VaRIndividual = Exposicao * Volatilidade * FatorConfianca`. Fórmula original: `Calculo!C2 = B2*Carteira!D2*Parametros!$B$2`.
3. **Consolidação do VaR total e verificação do limite** (`consolidar_var_total`, decisão): `VaRTotal = SOMA(VaRIndividual)`; `Status = "EXCEDIDO" se VaRTotal > LimiteVaR, senão "OK"`. Fórmula original: `Relatorio!D = SUM(Calculo!C2:C6)`, `Relatorio!F = IF(D>E,"EXCEDIDO","OK")`. A macro `AtualizarRelatorioVaR` força `wsRelatorio.Calculate` antes de ler `D2`/`F2` — a migração não depende de motor de fórmulas do Excel, calcula diretamente em Python.
4. **Exportação do relatório consolidado** (`exportar_relatorio`): `Sub ExportarRelatorioCSV` grava `ativo,exposicao,var_individual,var_total,limite_var,status`, uma linha por ativo, com `var_total`/`limite_var`/`status` repetidos em todas as linhas (formato denormalizado).
5. **Alerta por e-mail em caso de excesso** (`alertar_excesso_limite`, decisão): `Sub EnviarAlertaLimite`, chamada só quando `Status = "EXCEDIDO"`, via `CreateObject("Outlook.Application")`.

## Saídas -- detalhe técnico

| id | destino original | formato | schema |
|---|---|---|---|
| `relatorio_var` | `\\fswcorp\risco\equities\relatorio_var.csv` (hardcoded) | csv | `ativo,exposicao,var_individual,var_total,limite_var,status` |
| `alerta_email` | Outlook, para `mesa.equities@banco.com.br` (hardcoded) | corpo de e-mail em texto | contém o valor de `var_total` formatado |

## Dependências e ambiente

- Excel com macros habilitadas; automação COM do Outlook (`CreateObject("Outlook.Application")`) — dependência Windows-specific sem uso de biblioteca externa de terceiros.
- Sem agendamento explícito no VBA: execução disparada por `Workbook_Open` (roda toda vez que o arquivo é aberto).

## Pontos de atenção técnicos

- `ExportarRelatorioCSV` usa `fso.CreateTextFile(CAMINHO_SAIDA, True)` — o `True` trunca/sobrescreve o arquivo anterior sem manter histórico.
- A macro assume que a aba `Relatorio` já está com as 5 linhas de ativos preenchidas via fórmula antes de `Calculate` — se a carteira tiver um número de ativos diferente de 5, as fórmulas (arrastadas manualmente) podem não cobrir todas as linhas. A implementação Python não deve ter essa limitação.
- `CAMINHO_SAIDA` e `EMAIL_ALERTA` são constantes hardcoded no módulo — na migração, ambos viram configuração (`config.yaml`), não valores fixos no código-fonte.
