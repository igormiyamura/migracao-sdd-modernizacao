<!--
Modelo usado pelo agente homologador para gerar testes/relatorio_homologacao.md.
Combina comparação automática de output com sign-off manual do dono do
processo -- ver Q6 do desenho original e .claude/agents/homologador.md.
-->

# Relatório de homologação -- {{ processo.nome }}

**Execução**: {{ uuid }}
**Data**: {{ data }}
**Amostra de output legado usada como baseline**: {{ caminho_amostra }}

## Método de comparação

Descrição de como o output do código novo foi comparado ao baseline: chaves usadas para alinhar linhas, colunas comparadas, tolerância numérica aplicada (`config.yaml -> homologacao.tolerancia`), e como divergências não numéricas (texto, datas, linhas faltantes/extras) foram tratadas.

## Resultado

- Total de linhas comparadas: N
- Linhas dentro da tolerância: N
- Linhas divergentes: N
- Colunas com maior taxa de divergência: ...

## Divergências encontradas

Tabela com cada divergência: chave da linha, coluna, valor legado, valor novo, diferença, dentro/fora da tolerância.

## Veredito automático

`APROVADO` (todas as divergências dentro da tolerância) ou `REPROVADO` (ao menos uma divergência fora da tolerância -- volta para o `implementador-python` com este relatório).

## Sign-off do dono do processo

> Confirmo que revisei este relatório e que o processo migrado está equivalente ao processo legado para uso em produção.
>
> Nome: ______________________
> Data: ______________________
> Assinatura/aprovação (e-mail, ticket, ou assinatura formal conforme processo da área): ______________________

## Próximo passo

Homologação aprovada + sign-off do dono do processo é pré-requisito para o estágio `revisao_tecnica` em `.sdd/estado.yaml` -- o processo não vai para produção sem os dois.
