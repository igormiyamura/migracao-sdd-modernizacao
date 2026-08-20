# Relatório de homologação -- Consolidação de VaR - Mesa Equities

**Execução**: c81674ea
**Data**: 2026-08-19
**Amostra de output legado usada como baseline**: `entrada/amostra_saida/relatorio_var.csv`

## Método de comparação

`testes/comparar_homologacao.py` executa o processo migrado de ponta a ponta (`src/consolidacao_var_equities/fluxo.py`, com `conectores.email.enviar` substituído por um stub que só registra a chamada, já que este ambiente de validação não tem credencial O365 real) e compara `saida_execucao/relatorio_var.csv` contra o baseline, alinhando por `ativo`. Colunas numéricas (`exposicao`, `var_individual`, `var_total`, `limite_var`) comparadas com tolerância absoluta de `1e-6`; `status` comparado por igualdade exata de texto.

## Resultado

- Total de linhas comparadas: 5
- Linhas dentro da tolerância: 5
- Linhas divergentes: 0
- Alerta de e-mail: disparado (esperado -- `var_total = 63019.44 > limite_var = 50000`), capturado pelo stub com destinatário e assunto corretos.

## Divergências encontradas

Nenhuma. O CSV gerado tem ruído de ponto flutuante em relação ao baseline (ex: `var_total = 63019.439999999995` no lugar de `63019.44`, `exposicao = 247799.99999999997` no lugar de `247800.0` para WEGE3) -- exatamente o tipo de diferença que a tolerância numérica existe para absorver; nenhuma delas reflete uma regra de negócio implementada errado.

## Veredito automático

**APROVADO**

## Sign-off do dono do processo

> Esta é uma execução de exemplo para validar o pipeline de migração, não um processo real -- não há dono de processo de fato para assinar. Em uma migração real, este espaço fica em aberto até o dono do processo confirmar.
>
> Nome: _(execução de exemplo -- não aplicável)_
> Data: _(execução de exemplo -- não aplicável)_
> Assinatura/aprovação: _(execução de exemplo -- não aplicável)_

## Próximo passo

Numa migração real, homologação `APROVADO` + sign-off do dono do processo são pré-requisito para o estágio `revisao_tecnica`. Nesta execução de exemplo, `revisao_tecnica` permanece `pendente` por definição -- o objetivo aqui foi validar que o pipeline (discovery → documentação → grafo → plano → implementação → homologação) produz artefatos corretos de ponta a ponta, não levar um processo real à produção.
