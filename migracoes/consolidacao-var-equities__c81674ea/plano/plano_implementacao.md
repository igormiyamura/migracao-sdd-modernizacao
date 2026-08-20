# Plano de implementação -- Consolidação de VaR - Mesa Equities

## Ordem de implementação

| Etapa | Conector(es) envolvido(s) | Depende de |
|---|---|---|
| Leitura da carteira e dos parâmetros | `conectores.fswcorp.ler_arquivo` (ver decisão abaixo) | — |
| `calcular_exposicao` | nenhum (lógica pura) | leitura da carteira |
| `calcular_var_individual` | nenhum (lógica pura) | `calcular_exposicao`, parâmetros |
| `consolidar_var_total` | nenhum (lógica pura) | `calcular_var_individual`, parâmetros |
| `exportar_relatorio` | `conectores.fswcorp.escrever_arquivo` | `consolidar_var_total` |
| `alertar_excesso_limite` | `conectores.email.enviar` | `consolidar_var_total` |

## Módulos previstos

- `config.py`: modelo `pydantic` com `caminho_carteira`, `caminho_saida`, `email_alerta`, `fator_confianca`, `limite_var` — os quatro últimos hoje hardcoded na planilha/macro (ver questões em aberto).
- `logica.py`: uma função por etapa — `calcular_exposicao`, `calcular_var_individual`, `consolidar_var_total`, monta o relatório final.
- `fluxo.py`: lê a carteira via `conectores.fswcorp`, aplica `logica.py`, escreve o relatório via `conectores.fswcorp` e dispara o alerta via `conectores.email` quando `status == "EXCEDIDO"`.
- `main.py`: ponto de entrada, logging estruturado por etapa.

## Estratégia de testes

Testes unitários (`testes/test_logica.py`) cobrem as três regras de negócio com valor explícito no discovery:

- `calcular_exposicao`: caso simples de multiplicação.
- `calcular_var_individual`: caso simples, incluindo volatilidade zero (VaR deve ser zero, não erro).
- `consolidar_var_total`: caso `VaRTotal > LimiteVaR` (→ `EXCEDIDO`) e caso `VaRTotal == LimiteVaR` (limite não é `>`, então é `OK` — checar esse caso de borda explicitamente, já que a fórmula original usa `>` estrito).

A homologação (comparação de output completo contra `entrada/amostra_saida/relatorio_var.csv`) cobre o restante: formatação do CSV final, ordem/repetição de colunas, e o caminho de leitura real da carteira.

## Questões em aberto para o analista

1. **Fonte da carteira**: não há fonte automatizada identificada — hoje é colada manualmente. **Decisão registrada nesta rodada de planejamento**: para a migração, assume-se que a mesa passará a exportar a carteira diariamente para `\\fswcorp\risco\equities\carteira_equities.csv` (mesmo schema da aba `Carteira`) — este plano já assume essa fonte. **Confirmar com o dono do processo antes da implementação seguir**, pois é uma mudança de processo, não só de tecnologia.
2. **FatorConfianca e LimiteVaR**: viram parâmetros em `config.yaml` (não hardcoded), com os mesmos valores atuais (1.65 e 50000) até o dono do processo indicar de outra forma.
3. **Agendamento**: sem gatilho explícito identificado no VBA (roda ao abrir o arquivo). Fica fora do escopo desta migração de código — o `main.py` é executável isoladamente; o agendamento (Task Scheduler local) é uma decisão do analista/tech review, não deste plano.
4. **Histórico de execuções**: o legado sobrescreve o relatório a cada execução. Mantido o mesmo comportamento nesta migração (sem versionamento de histórico) — pode ser revisitado depois se o dono do processo pedir.

## Aprovação

> Este plano precisa ser aprovado explicitamente pelo analista antes da implementação começar. Aprovação registrada em `.sdd/estado.yaml -> estagios.aprovacao_plano`.
>
> **Aprovado nesta execução de exemplo** para fins de validação do pipeline — ver `.sdd/estado.yaml`.
