# Apuração de Enquadramento de Limites - Mesa de Renda Fixa (execução de exemplo)

Segunda execução de exemplo — **não é um processo real**. Criada para validar o pipeline contra um monólito real (múltiplos módulos VBA + uma classe), diferente do primeiro exemplo (`consolidacao-var-equities`), que tinha um único módulo `.bas` simples. Fonte fictícia: `entrada/origem_planilha.xlsx` (abas Posicoes/Limites/Resumo) + `entrada/modulos_vba/` (5 módulos + 1 classe, exportados).

## O que este exemplo valida que o primeiro não cobria

- **Modo monólito real**: 6 módulos/classes detectados pelo script de pré-processamento (`scripts/extrair_vba.py`) — bem acima do limiar de ativação (`referencias/extracao-monolitos.md`). Checkpoint incremental registrado em `.sdd/memoria/progresso_discovery.yaml`.
- **Classe VBA** (`ClasseLimite.cls`): extraída como um módulo próprio, com suas duas `Property Get` viram duas `etapas` no discovery — incluindo uma regra de negócio real (limiares de 80%/100% hardcoded).
- **`discovery.yaml` com 6 módulos e `codigo_original` por etapa**: `especificacao/doc_tecnico.md` cita o código VBA original literal em cada uma das 7 etapas com lógica — a seção "Módulos e principais funções", nova nesta rodada de enriquecimento.
- **`doc_negocio.md` com "Regras e decisões de negócio"**: consolida os limiares 80%/100%, sinalizando que a origem não é conhecida — outra seção nova.
- **Grafo excluindo módulos de puro orquestrador/utilitário**: `modulo_principal` e `modulo_utilitarios` não aparecem no grafo (regra nova, adicionada durante a montagem deste exemplo — ver `.claude/agents/gerador-grafo.md`, regra 4) — sem isso, ficariam órfãos no diagrama.
- **`logica/` como subpacote**: com 4 módulos de discovery carregando regra de negócio, o plano decidiu por um arquivo por módulo em vez de um `logica.py` só (`guardrails/codigo.md`).
- **Três ramos de decisão exercitados numa única homologação**: `RENDA_FIXA_PRE` (≈80,9%, `ALERTA`), `RENDA_FIXA_IPCA` (≈120,75%, `EXCEDIDO`), `RENDA_FIXA_CAMBIAL` (48%, `OK`) — cobrindo os três caminhos de roteamento de e-mail numa só execução, `0` divergências.

## Para reproduzir

```
cd migracoes/enquadramento-limites-renda-fixa__0e2be2b7
PYTHONPATH=src python -m pytest testes/test_classe_limite.py testes/test_modulo_consolidacao.py testes/test_modulo_enquadramento.py testes/test_modulo_notificacao.py -q
python testes/comparar_homologacao.py
```

## O que ficou pendente (de propósito)

`revisao_tecnica` permanece `pendente` — mesma lógica do primeiro exemplo, essa etapa é manual mesmo numa migração real.
