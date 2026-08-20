<!--
Modelo usado pelo agente planejador para gerar plano/plano_implementacao.md.
Este documento precisa da aprovação explícita do analista (estágio
aprovacao_plano em estado.yaml) antes do implementador-python começar a
escrever código -- ver .claude/agents/planejador.md.
-->

# Plano de implementação -- {{ processo.nome }}

## Ordem de implementação

Lista ordenada das etapas de `discovery.yaml -> etapas`, com a etapa de entrada/saída associada e o conector correspondente (`guardrails/interface_conectores.md`). A ordem segue dependências reais entre etapas, não a ordem em que apareceram na fonte original.

| Etapa | Conector(es) envolvido(s) | Depende de |
|---|---|---|
| {{ etapa.nome }} | {{ conector }} | {{ etapas anteriores necessárias }} |

## Módulos previstos

Mapeamento das etapas para a estrutura de `guardrails/codigo.md` (`config.py`, `logica.py`, `fluxo.py`, `main.py`) -- uma função por etapa do `discovery.yaml` dentro de `logica.py`.

## Estratégia de testes

Quais regras de negócio (`discovery.yaml -> etapas[].regras_negocio`) viram casos de teste unitário, e quais só são verificáveis via a homologação (comparação de output completo) por dependerem de dado real.

## Questões em aberto para o analista

Qualquer item de `riscos_pontos_atencao` do discovery que exige uma decisão explícita antes de implementar (ex: "replicar o valor hardcoded ou torná-lo configurável?"). O `implementador-python` não decide isso sozinho.

## Aprovação

> Este plano precisa ser aprovado explicitamente pelo analista antes da implementação começar. Aprovação registrada em `.sdd/estado.yaml -> estagios.aprovacao_plano`.
