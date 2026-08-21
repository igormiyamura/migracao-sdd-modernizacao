# Migrar processo (Devin Playbook)

Adaptador Devin do pipeline canônico de migração. O procedimento, o schema de `discovery.yaml`, o `estado.yaml` e todos os guardrails são os mesmos usados pelo skill `migrar-processo` do Claude Code (`.claude/skills/migrar-processo/SKILL.md`) — este Playbook não duplica esse conteúdo, só aponta para os mesmos arquivos, que são markdown puro e leem igual em qualquer ferramenta.

## Overview

Conduz a migração de um processo legado de risco de mercado (Excel, Excel+VBA, Alteryx, C#, Python legado) para Python padronizado local, em estágios de Spec Driven Development, do intake até pronto para revisão técnica. Cada estágio grava seu resultado em `.sdd/estado.yaml` da execução, o que torna a migração retomável por UUID em uma sessão Devin futura.

## Procedure

1. Perguntar ao usuário: nova migração ou continuação de um UUID existente? Se continuação, ler `.sdd/estado.yaml` da pasta `migracoes/<slug>__<uuid>/` e anunciar em que estágio parou antes de prosseguir.
2. Intake: seguir `.claude/skills/migrar-processo/referencias/convencoes-pastas.md` para os artefatos mínimos por stack e a estrutura de pastas. Criar a pasta da execução com UUID (8 primeiros caracteres de um UUID v4) e registrar em `migracoes/indice.yaml`.
3. Discovery: seguir as instruções do arquivo `.claude/agents/extrator-<stack>.md` correspondente à stack de origem (`extrator-excel`, `extrator-excel-vba`, `extrator-alteryx`, `extrator-csharp`, `extrator-python-legado`) para produzir `entrada/discovery.yaml`. Rodar primeiro o script de pré-processamento correspondente em `scripts/` (nunca ler o arquivo bruto direto) e seguir a estratégia de divisão por módulo de `.claude/skills/migrar-processo/referencias/extracao-monolitos.md` — processos reais aqui costumam ser monólitos.
4. Documentação: seguir `.claude/agents/redator-documentacao.md` para produzir `especificacao/doc_negocio.md` e `especificacao/doc_tecnico.md`.
5. Grafo: seguir `.claude/agents/gerador-grafo.md` para produzir `especificacao/grafo_processo.mmd`.
6. Plano: seguir `.claude/agents/planejador.md` para produzir `plano/plano_implementacao.md`. Parar e pedir aprovação explícita do usuário antes de seguir — registrar em `estado.yaml -> estagios.aprovacao_plano`.
7. Implementação: seguir `.claude/agents/implementador-python.md` e `guardrails/codigo.md` + `guardrails/interface_conectores.md`.
8. Homologação: seguir `.claude/agents/homologador.md`. Se `REPROVADO`, voltar ao passo 7 com o relatório de divergências. Se `APROVADO`, aguardar sign-off do dono do processo.
9. Encerrar informando que o processo está pronto para revisão técnica obrigatória (`estado.yaml -> revisao_tecnica.obrigatoria: true`) e não deve ir a produção sem ela.

## Specifications

- Schema de `discovery.yaml` (agrupado por `modulo`): `.claude/skills/migrar-processo/referencias/convencoes-pastas.md`
- Schema de `estado.yaml` e lógica de retomada por UUID: `.claude/skills/migrar-processo/referencias/estado-e-retomada.md`
- Divisão de monólito, checkpoint incremental e scripts de pré-processamento: `.claude/skills/migrar-processo/referencias/extracao-monolitos.md`
- Guardrails de código (stack, nomenclatura, estrutura, `logica/` como subpacote em processo grande): `guardrails/codigo.md`
- Interface de conectores (fswcorp/email/sharepoint/api/processo_legado): `guardrails/interface_conectores.md`
- Modelos dos documentos gerados: `modelos/`

## Advice and Pointers

- Todo artefato gerado (documentação, código, mensagens ao usuário) é em português — nomes de conceito de negócio em português, termos técnicos genéricos do Python podem ficar em inglês quando não há tradução natural.
- Se a máquina/ambiente Devin não tiver acesso de rede a `fswcorp`/SharePoint/e-mail durante a sessão, isso não bloqueia discovery, documentação, grafo ou plano — só bloqueia a execução real do `implementador-python`/`homologador` contra dados vivos. Sinalizar essa limitação ao usuário em vez de simular dados.
- Um único repositório git por processo migrado é esperado eventualmente, mas essa etapa ainda não está em vigor — não force a criação de um repositório/PR como parte deste Playbook a menos que o usuário peça.

## Forbidden Actions

- Não avançar para implementação sem a aprovação explícita do plano pelo usuário (passo 6).
- Não marcar homologação como concluída sem o sign-off do dono do processo preenchido no relatório.
- Não acessar `fswcorp`, e-mail, SharePoint ou API diretamente no código gerado — sempre via `conectores/`.

## Required from User

- Confirmação da stack de origem e os artefatos mínimos listados em `referencias/convencoes-pastas.md`.
- Aprovação explícita do plano de implementação antes da etapa 7.
- Sign-off do dono do processo depois da homologação `APROVADO`.
