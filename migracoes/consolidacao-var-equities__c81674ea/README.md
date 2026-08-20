# Consolidação de VaR - Mesa Equities (execução de exemplo)

Esta execução **não é um processo real** — foi criada para validar o pipeline de `migrar-processo` de ponta a ponta: um processo Excel+VBA fictício (`entrada/origem_planilha.xlsx` + `entrada/origem_macro.bas`) foi levado por todos os estágios até homologação, com todo agente (`.claude/agents/`) exercitado seguindo exatamente as instruções que ele segue numa migração real.

## O que foi validado

- **Discovery** (`entrada/discovery.yaml`): lógica das fórmulas e da macro extraída corretamente, incluindo os cinco `riscos_pontos_atencao` (fonte manual da carteira, parâmetros hardcoded, caminho de saída hardcoded, e-mail hardcoded, gatilho de execução implícito).
- **Documentação** (`especificacao/doc_negocio.md`, `doc_tecnico.md`) e **grafo** (`especificacao/grafo_processo.mmd`, 11 nós, dentro do teto de 18): gerados a partir do discovery, sem informação inventada.
- **Plano** (`plano/plano_implementacao.md`): decisão explícita registrada sobre a fonte de dados da carteira (ver "Questões em aberto", item 1) — o tipo de decisão que numa migração real precisa da confirmação do dono do processo antes de seguir.
- **Implementação** (`src/consolidacao_var_equities/`): `ruff check` e `mypy` passam limpos; `pytest` cobre as regras de negócio, incluindo o caso de borda do limite (`>` estrito, não `>=`).
- **Homologação** (`testes/relatorio_homologacao.md`): `testes/comparar_homologacao.py` roda o processo migrado de ponta a ponta e compara contra `entrada/amostra_saida/relatorio_var.csv` — **0 divergências, veredito APROVADO**, incluindo o disparo correto do alerta por e-mail (capturado por um stub, já que este ambiente não tem credencial O365 real).

## Para reproduzir

```
cd migracoes/consolidacao-var-equities__c81674ea
PYTHONPATH=src python -m pytest testes/test_logica.py -q
python testes/comparar_homologacao.py
```

## O que ficou pendente (de propósito)

`revisao_tecnica` permanece `pendente` em `.sdd/estado.yaml` — essa etapa é manual e obrigatória mesmo numa migração real; não faz sentido simulá-la aqui.
