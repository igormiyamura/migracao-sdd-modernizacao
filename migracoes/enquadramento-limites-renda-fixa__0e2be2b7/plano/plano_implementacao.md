# Plano de implementação -- Apuração de Enquadramento de Limites - Mesa de Renda Fixa

## Ordem de implementação

| Módulo (discovery) | Conector(es) envolvido(s) | Depende de |
|---|---|---|
| `modulo_consolidacao` | `conectores.fswcorp.ler_arquivo` (posições) | — |
| `modulo_enquadramento` | `conectores.fswcorp.ler_arquivo` (limites) | `modulo_consolidacao` |
| `classe_limite` | nenhum (lógica pura) | `modulo_enquadramento` |
| `modulo_notificacao` | `conectores.fswcorp.escrever_arquivo` (log), `conectores.email.enviar` (alertas) | `classe_limite` |

`modulo_principal` (orquestração) e `modulo_utilitarios` (log) não geram módulos de código próprios com regra de negócio — viram, respectivamente, o próprio `fluxo.py` e chamadas de `logging` padrão (ver `guardrails/codigo.md`), não arquivos em `logica/`.

## Estrutura de código

Este processo tem 4 módulos de discovery com regra de negócio própria (`modulo_consolidacao`, `modulo_enquadramento`, `classe_limite`, `modulo_notificacao`) — acima do ponto de valer a pena um `logica.py` único. Estrutura escolhida: subpacote `logica/`, um arquivo por `modulo.id`:

```
src/enquadramento_limites_renda_fixa/
  logica/
    __init__.py
    modulo_consolidacao.py      # consolidar_dv01_por_book()
    modulo_enquadramento.py     # avaliar_enquadramento()
    classe_limite.py            # dataclass Limite + calcular_percentual() + classificar_status()
    modulo_notificacao.py       # montar_log() + decidir_destinatarios()
  config.py
  fluxo.py
  main.py
```

`classe_limite.py` implementa `ClasseLimite` original como uma `dataclass` Python (`Limite`) com métodos `percentual_utilizado()` e `status()` — mantém o mesmo agrupamento de responsabilidade do VBA (dado + cálculo derivado juntos), só sem a sintaxe de `Property Let`/`Property Get`.

## Estratégia de testes

Um `test_<modulo_id>.py` por arquivo de `logica/` (espelhando a divisão, ver `guardrails/codigo.md`):

- `test_classe_limite.py`: cobre os três limiares de `Status` (`OK`/`ALERTA`/`EXCEDIDO`), incluindo os dois casos de borda exatos: `PercentualUtilizado = 80%` (deve ser `ALERTA`, o `>=` é inclusive) e `PercentualUtilizado = 100%` (deve ser `ALERTA`, não `EXCEDIDO` — o corte é `>` estrito). Também `ValorLimite = 0` (deve retornar `PercentualUtilizado = 0`, não erro de divisão).
- `test_modulo_consolidacao.py`: soma de DV01 por book, incluindo duas posições do mesmo book (devem somar) e um book com uma única posição.
- `test_modulo_enquadramento.py`: book presente em `Limites` sem posição em `Posicoes` (deve resultar em `ValorUtilizado = 0`, conforme `regras_negocio` do discovery — comportamento replicado, não corrigido, sem decisão do analista em contrário).
- `test_modulo_notificacao.py`: roteamento de e-mail — `EXCEDIDO` chama o conector de e-mail com o destinatário do head de risco, `ALERTA` com o do head da mesa, `OK` não chama o conector nenhuma vez.

A homologação cobre o pipeline completo, incluindo a leitura real das posições/limites e a geração do CSV final.

## Questões em aberto para o analista

1. **Fonte das posições**: sem fonte automatizada identificada (mesmo achado do processo de VaR já migrado) — **decisão registrada nesta rodada**: assume-se leitura de `\\fswcorp\risco\rendafixa\posicoes_renda_fixa.csv`, mesmo schema da aba `Posicoes`. Confirmar com o dono do processo antes da implementação seguir.
2. **Limiares 80%/100%**: sem origem documentada. Mantidos como estão, agora como parâmetros de `config.yaml` (`limiar_alerta: 0.8`, `limiar_excedido: 1.0`) em vez de hardcoded — replicados, não alterados, até o dono do processo indicar de outra forma.
3. **Conferência manual (aba `Resumo`)**: **decisão registrada nesta rodada** — não replicar na Fase 1 (o `SUMPRODUCT` não é lido por nenhum procedimento e duplicaria a mesma regra de `modulo_consolidacao` sem uso real). Se o dono do processo quiser mantê-la como teste de consistência, isso vira uma tarefa separada, não parte desta migração.
4. **Book sem posição = OK por padrão**: replicado como está (ver `test_modulo_enquadramento.py`) — não é uma correção de bug, é preservar o comportamento observado; qualquer mudança de comportamento aqui é decisão do dono do processo, não do `implementador-python`.
5. **Agendamento e histórico de log**: mesmo tratamento do processo de VaR já migrado — fora do escopo desta migração de código, decisão de analista/tech review.

## Aprovação

> Este plano precisa ser aprovado explicitamente pelo analista antes da implementação começar. Aprovação registrada em `.sdd/estado.yaml -> estagios.aprovacao_plano`.
>
> **Aprovado nesta execução de exemplo** para fins de validação do pipeline — ver `.sdd/estado.yaml`.
