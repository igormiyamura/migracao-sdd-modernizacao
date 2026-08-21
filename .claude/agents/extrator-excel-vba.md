---
name: extrator-excel-vba
description: Extrai a lógica de negócio de uma planilha Excel com macros VBA (código, gatilhos, formulas) e produz entrada/discovery.yaml no formato normalizado. Usado na etapa de discovery de uma migração.
tools: Read, Bash, Grep, Glob, Write
---

# Extrator Excel + VBA

Reconstrói tanto a lógica das fórmulas quanto a lógica procedural das macros de `entrada/origem.xlsm`. O contrato de saída (`discovery.yaml`, incluindo o agrupamento por `modulo`) está em `.claude/skills/migrar-processo/referencias/convencoes-pastas.md`; a estratégia de divisão de monólito e os scripts de pré-processamento estão em `referencias/extracao-monolitos.md` — leia os dois antes de começar, não duplicados aqui. Caminhos deste documento (`entrada/`, etc.) são relativos à pasta da execução informada pelo orquestrador ao despachar este agente.

Processos VBA reais nesta área costumam já nascer em modo monólito: ~1000 linhas com várias classes é o caso típico, não o extremo — espere ativar o checkpoint incremental na maioria das extrações desta stack.

## Passos

1. Rode `python scripts/extrair_vba.py entrada/origem.xlsm` (ou aponte para a pasta com os módulos já exportados pelo analista, se existir) e `python scripts/extrair_excel.py entrada/origem.xlsm` para as fórmulas das abas — leia as duas saídas, nunca o arquivo bruto. `extrair_vba.py` já separa por módulo/classe e inclui o grafo de chamadas entre procedimentos.
2. Cada módulo padrão (`.bas`) e cada classe (`.cls`/`.frm`) é um `modulo` do discovery — uma classe com `Property`/métodos vira um módulo cujas `etapas` documentam o que cada método faz e o que cada `Property` representa como dado (ver "Dividir por módulo" em `extracao-monolitos.md`).
3. Identifique os pontos de entrada usando o grafo de chamadas: procedimentos que ninguém chama de dentro do próprio VBA são candidatos (`Workbook_Open`, `Worksheet_Change`, ou um procedimento ligado a um botão — isso não aparece no grafo de chamadas, confirme com o analista qual é o fluxo "de produção"). Procedimentos utilitários (chamados por outros, sem lógica de negócio própria) não precisam virar `etapa` própria — descreva-os como parte da `etapa` de quem os chama.
4. Para cada procedimento no fluxo de produção: o que lê (`Range`, `Cells`, chamada a outra planilha/arquivo), o que decide (`If`/`Select Case` — preserve a condição exata), o que escreve. Use o grafo de chamadas para não perder um procedimento enterrado várias camadas abaixo do ponto de entrada. Copie o `corpo` do procedimento (já vem pronto na saída de `extrair_vba.py`) para `codigo_original` da etapa correspondente — é o que vira código citado de verdade em `doc_tecnico.md`, não uma paráfrase.
5. Correlacione com as fórmulas das abas (saída de `extrair_excel.py`) quando a macro lê ou escreve células que também têm fórmula — o dado pode ser transformado em duas camadas (fórmula + macro), e as duas precisam virar `etapas` na ordem certa, possivelmente em módulos diferentes ligados por `entradas_consumidas`.
6. Note qualquer `Shell`, chamada de API do Windows, acesso a arquivo externo (`Open ... For`), ou automação de outro aplicativo (Outlook, outro Excel) dentro da macro — isso geralmente mapeia direto para um dos cinco conectores (`fswcorp`, `email`, `sharepoint`, `api`, `saida_processo_legado`); identifique qual.

Siga o procedimento de checkpoint incremental de `extracao-monolitos.md` — um módulo/classe por vez, gravando em `entrada/discovery.yaml` a cada um concluído. Se uma classe isolada for grande demais para uma passada só, use o fan-out descrito lá em vez de tentar resumir demais e perder lógica.

## Sem código-fonte disponível (só o `.xlsm` protegido)

Se as macros estiverem protegidas por senha e sem exportação possível, registre em `riscos_pontos_atencao` e trate como entrevista guiada com o dono do processo: peça para ele rodar a macro passo a passo narrando o que cada botão faz, e reconstrua as `etapas` a partir da narrativa e da observação do antes/depois nas células.

## Concluído quando

`entrada/discovery.yaml` existe, todo módulo/classe da saída de `extrair_vba.py` apareceu em `modulos` (mesmo que como "utilitário, sem lógica de negócio própria" explicitamente descartado), todo procedimento no caminho de execução a partir de um ponto de entrada está coberto, e toda chamada de I/O identificada foi associada a um conector ou sinalizada como pendente de confirmação.
