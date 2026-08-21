# Relatório de homologação -- Apuração de Enquadramento de Limites - Mesa de Renda Fixa

**Execução**: 0e2be2b7
**Data**: 2026-08-20
**Amostra de output legado usada como baseline**: `entrada/amostra_saida/log_enquadramento.csv`

## Método de comparação

`testes/comparar_homologacao.py` executa o processo migrado de ponta a ponta (com `conectores.email.enviar` substituído por um stub que só registra a chamada) e compara `saida_execucao/log_enquadramento.csv` contra o baseline, alinhando por `book`. Colunas numéricas (`limite`, `utilizado`, `percentual`) comparadas com tolerância absoluta de `1e-6`; `status` por igualdade exata de texto.

## Resultado

- Total de linhas (books) comparadas: 3
- Linhas dentro da tolerância: 3
- Linhas divergentes: 0
- Alertas de e-mail disparados: 2 — `ALERTA` para `RENDA_FIXA_PRE` (head da mesa) e `EXCEDIDO` para `RENDA_FIXA_IPCA` (head de risco); `RENDA_FIXA_CAMBIAL` (`OK`) corretamente não gerou alerta nenhum. Os três ramos de severidade (`OK`/`ALERTA`/`EXCEDIDO`) foram exercitados nesta única execução.

## Divergências encontradas

Nenhuma.

## Veredito automático

**APROVADO**

## Sign-off do dono do processo

> Execução de exemplo para validar o pipeline de migração com um monólito real (múltiplos módulos VBA + classe) — não é um processo real, não há dono de processo de fato para assinar.

## Próximo passo

Numa migração real, `revisao_tecnica` seguiria pendente até a revisão manual obrigatória. Nesta execução de exemplo, o objetivo foi validar que o pipeline lida corretamente com um monólito de verdade: extração em modo checkpoint incremental, discovery hierárquico com código original citado, grafo que exclui módulos de puro orquestração/utilitário, plano que decide `logica/` como subpacote, e homologação cobrindo os três ramos de decisão do processo original.
