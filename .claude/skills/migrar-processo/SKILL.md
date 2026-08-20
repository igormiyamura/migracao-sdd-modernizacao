---
name: migrar-processo
description: Conduz a migração de um processo legado de risco de mercado (Excel, Excel+VBA, Alteryx, C# ou Python legado) para Python padronizado local, seguindo Spec Driven Development. Acionado pelo analista para começar uma migração nova ou continuar uma em andamento.
disable-model-invocation: true
---

# Migrar processo

Conduz um processo legado, do zero até pronto para revisão técnica, pelos estágios de SDD: discovery, documentação de negócio e técnica, grafo do processo, plano, implementação, homologação. Cada estágio é delegado a um agente especializado (`.claude/agents/`) e seu resultado é gravado em `.sdd/estado.yaml` antes de seguir para o próximo — isso é o que torna a execução retomável a qualquer momento pelo UUID.

Antes do primeiro estágio, leia `referencias/convencoes-pastas.md` (estrutura de pastas e o contrato `discovery.yaml`) e `referencias/estado-e-retomada.md` (esquema de `estado.yaml` e como retomar). Volte a eles quando precisar do schema exato — não duplicado aqui.

Caminhos `referencias/...` são relativos a esta pasta de skill. Caminhos `guardrails/...`, `modelos/...`, `conectores/...` e `migracoes/...` citados abaixo são relativos à raiz do repositório. Ao despachar qualquer agente das seções 3 a 8, informe no prompt de despacho o caminho absoluto da pasta desta execução (`migracoes/<slug>__<uuid>/`) — os arquivos de agente em `.claude/agents/` escrevem `entrada/`, `especificacao/`, `plano/`, `src/`, `testes/` como relativos a essa pasta.

## 1. Nova migração ou continuação?

Pergunte ao analista. Se for continuação, peça o UUID (ou o nome do processo, se ele não lembra o UUID — busque em `migracoes/indice.yaml`). Localize a pasta `migracoes/<slug>__<uuid>/`, leia `.sdd/estado.yaml` e `.sdd/memoria/`, e **anuncie em que estágio a execução parou e o que já existe** antes de continuar. Pule para a seção 3, no primeiro estágio com `status` diferente de `concluido`.

Se for nova migração, siga para a seção 2.

**Concluído quando**: você sabe se está criando ou retomando, e se retomando, sabe exatamente em qual estágio continuar.

## 2. Intake

Colete os artefatos listados em `referencias/convencoes-pastas.md` (comuns + específicos da stack). Pergunte um por um se o analista não trouxe tudo de uma vez — não avance com um artefato mínimo faltando. Confirme a stack de origem com o analista mesmo quando ela for óbvia pela extensão do arquivo.

Gere um UUID v4, use os 8 primeiros caracteres, monte o slug do processo (minúsculo, sem acento, espaços por `-`). Crie a estrutura de pastas completa de `referencias/convencoes-pastas.md`, copie os artefatos de entrada para `entrada/`, e grave `.sdd/estado.yaml` inicial com todos os estágios `pendente`. Adicione a entrada correspondente em `migracoes/indice.yaml`.

**Concluído quando**: a pasta da execução existe com os artefatos de entrada copiados e `estado.yaml` criado.

## 3. Discovery

Despache, via ferramenta de agente, o extrator correspondente à stack confirmada:

| Stack | Agente |
|---|---|
| Excel sem macro | `extrator-excel` |
| Excel + VBA | `extrator-excel-vba` |
| Alteryx | `extrator-alteryx` |
| C# | `extrator-csharp` |
| Python legado | `extrator-python-legado` |

O agente produz `entrada/discovery.yaml`. Atualize `estado.yaml` (`discovery: concluido`) só depois de confirmar que o arquivo existe e tem as quatro seções (`entradas`, `etapas`, `saidas`, `riscos_pontos_atencao`) preenchidas — um discovery vazio ou genérico não conta como concluído.

**Concluído quando**: `entrada/discovery.yaml` existe e cobre as quatro seções.

## 4. Documentação

Despache `redator-documentacao`, que lê `discovery.yaml` e produz `especificacao/doc_negocio.md` e `especificacao/doc_tecnico.md`.

**Concluído quando**: os dois documentos existem e cada `riscos_pontos_atencao` do discovery aparece refletido em algum dos dois.

## 5. Grafo do processo

Despache `gerador-grafo`, que produz `especificacao/grafo_processo.mmd` e o referencia dentro de `doc_tecnico.md`.

**Concluído quando**: `grafo_processo.mmd` existe, renderiza sem erro de sintaxe Mermaid, e todo `id` de `entradas`/`saidas` do discovery aparece no grafo.

## 6. Plano de implementação

Despache `planejador`, que produz `plano/plano_implementacao.md`. Apresente o plano ao analista e **peça aprovação explícita** — uma frase de concordância, não silêncio. Registre a aprovação em `estado.yaml -> estagios.aprovacao_plano`. Não avance para a implementação sem essa aprovação registrada, mesmo que o plano pareça óbvio.

**Concluído quando**: o plano existe e o analista aprovou explicitamente.

## 7. Implementação

Despache `implementador-python`, que escreve o código em `src/` seguindo `guardrails/codigo.md` e `guardrails/interface_conectores.md`, e copia `modelos/pyproject_template.toml` preenchido.

**Concluído quando**: o projeto roda `uv run ruff check`, `uv run mypy` e `uv run pytest` sem falha antes de seguir para homologação.

## 8. Homologação

Despache `homologador`, que compara o output do código novo contra a amostra de output legado e produz `testes/relatorio_homologacao.md`.

Se o veredito automático for `REPROVADO`: volte para a seção 7 com o relatório de divergências como entrada adicional para o `implementador-python`. Não repita a homologação inteira do zero — ela já sabe comparar contra o mesmo baseline.

Se `APROVADO`: colete o sign-off do dono do processo (pode ser assíncrono — registre no relatório quando chegar).

**Concluído quando**: o relatório existe com veredito `APROVADO` e sign-off preenchido.

## 9. Encerramento da Fase 1

Marque `revisao_tecnica: pendente` (permanece pendente — esta etapa não é automatizável) e informe claramente ao analista: **o processo está pronto para revisão técnica, e não deve ir para uso em produção antes dessa revisão** (`estado.yaml -> revisao_tecnica.obrigatoria` é sempre `true`). Aponte o caminho completo da pasta da execução e o UUID, para o analista repassar a quem fizer a revisão.
