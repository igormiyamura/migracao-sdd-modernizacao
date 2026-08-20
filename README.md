# Migração SDD — Risco de Mercado

Kit de agentes e skills para migrar processos legados (Excel, Excel+VBA, Alteryx, C#, Python legado/ad-hoc) para Python padronizado rodando localmente, usando Spec Driven Development. Construído para rodar tanto em Claude Code quanto em Devin Desktop a partir do mesmo pipeline canônico.

## Como usar

Analista, na sua máquina, com este repositório aberto no Claude Code ou no Devin Desktop:

- **Claude Code**: digite `/migrar-processo` (ou peça "quero migrar um processo de Excel/Alteryx/..."). O skill está em `.claude/skills/migrar-processo/SKILL.md`.
- **Devin Desktop**: anexe o Playbook `.devin/playbooks/migrar-processo.devin.md` no início da sessão.

Tenha em mãos os artefatos listados em `.claude/skills/migrar-processo/referencias/convencoes-pastas.md` antes de começar — o próprio fluxo pergunta o que faltar.

Cada migração roda até ficar pronta para **revisão técnica** — essa revisão continua manual e obrigatória; nenhuma migração vai para produção sem ela.

## Escopo desta fase

Esta é a Fase 1: migração para Python local + guardrails que preparam a transição futura para AWS (Fase 2, fora de escopo aqui). O toolkit real de conectores (fswcorp/e-mail/SharePoint/API) está previsto para ser refatorado numa etapa intermediária (1.5); até lá, `conectores/` implementa a mesma interface com bibliotecas diretas, para que o código de cada processo migrado não precise mudar quando o toolkit real chegar.

## Estrutura do repositório

```
.claude/skills/migrar-processo/   orquestrador (Claude Code) + referências compartilhadas
.claude/agents/                    um agente por estágio do pipeline (extratores, doc, grafo, plano, implementação, homologação)
.devin/playbooks/                  adaptador do mesmo pipeline para Devin Desktop
guardrails/                        padrão de código e contrato da interface de conectores
conectores/                        implementação placeholder da interface de conectores
modelos/                           templates dos documentos/artefatos gerados por migração
migracoes/                         uma pasta por execução (criada em tempo de uso) + índice agregado
```

Para entender o pipeline estágio a estágio, leia `.claude/skills/migrar-processo/SKILL.md` — é a fonte de verdade do fluxo, este README não o repete.

## Convenções gerais

- Todos os artefatos gerados (documentação, mensagens, e a maior parte do código) são em português.
- Stack de código: Python 3.11, `uv`, `ruff`, `mypy`, `pytest` — detalhe completo em `guardrails/codigo.md`.
- Cada execução tem um UUID próprio, retomável a qualquer momento — detalhe em `.claude/skills/migrar-processo/referencias/estado-e-retomada.md`.
# migracao-sdd-modernizacao
