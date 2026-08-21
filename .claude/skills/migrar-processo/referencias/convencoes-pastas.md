# Convenções de pastas e artefatos de entrada

Referência consultada nas etapas de **intake** (coleta de artefatos) e **discovery** de qualquer migração.

## Artefatos que o analista precisa reunir antes de começar

Comuns a qualquer stack de origem:

- Identificação do processo: nome de negócio, mesa/área responsável, dono do processo, frequência de execução, criticidade.
- O(s) arquivo(s)-fonte do processo em si (ver específicos por stack abaixo).
- Ao menos uma amostra de output "correto" recente — vira o baseline usado pelo `homologador` na comparação de equivalência.
- Mapeamento das fontes de dados consumidas pelo processo, em uma destas cinco categorias: `fswcorp`, `email`, `sharepoint`, `api`, `saida_processo_legado` — com a localização/endpoint de cada uma.
- Contato do dono do processo, para a entrevista de discovery (quando o arquivo-fonte não é suficiente para reconstruir a lógica) e para o sign-off de homologação.

Específicos por stack:

| Stack | Artefato mínimo | Desejável |
|---|---|---|
| Excel (sem macro) | arquivo `.xlsx` final, com abas auxiliares/ocultas incluídas | — |
| Excel + VBA | arquivo `.xlsm` com macros habilitadas (todos os módulos e classes) | código VBA exportado (`.bas`/`.cls`/`.frm`) do editor VBA |
| Alteryx | workflow `.yxmd`/`.yxwz`, incluindo macros aninhadas (`.yxmc`) | arquivos `.yxdb` referenciados pelo workflow |
| C# | acesso ao código-fonte (solution/projeto) | — |
| Python legado | script(s) `.py` ou notebook(s) `.ipynb` existentes | lista de dependências usadas, mesmo informal |

Processos reais nesta área costumam ser **monólitos**: macro VBA com múltiplas classes e ~1000 linhas, workflow Alteryx com dezenas de ferramentas encadeadas (às vezes com ferramentas Python embutidas), script/notebook Python de ~1000 linhas. Isso não muda os artefatos mínimos, mas muda como o discovery processa o material — ver `extracao-monolitos.md`.

Se só existir o binário/executável compilado (sem código-fonte acessível), a etapa de discovery cai no caminho de **entrevista guiada** — ver a seção "Sem código-fonte disponível" no agente extrator correspondente.

## Estrutura de uma execução de migração

Toda migração vive em sua própria pasta, nomeada `<slug-do-processo>__<uuid8>`, dentro de `migracoes/` na raiz deste repositório:

```
migracoes/
  <slug-do-processo>__<uuid8>/
    .sdd/
      estado.yaml            # estágio atual, timestamps, decisões — ver estado-e-retomada.md
      memoria/                # snapshots de contexto para retomada entre sessões
    entrada/                  # artefatos de origem fornecidos pelo analista (somente leitura)
      origem.<ext>
      amostra_saida/
      discovery.yaml          # saída normalizada do agente extrator — contrato entre discovery e as etapas seguintes
    especificacao/
      doc_negocio.md
      doc_tecnico.md
      grafo_processo.mmd
    plano/
      plano_implementacao.md
    src/                       # código Python gerado (layout src/, ver guardrails/codigo.md)
    testes/
      relatorio_homologacao.md
    README.md
```

`<slug-do-processo>` é o nome do processo em minúsculas, sem acento, espaços trocados por `-` (ex: `consolidacao-carteira-equities`). `<uuid8>` são os 8 primeiros caracteres de um UUID v4 gerado na criação da execução — ver `estado-e-retomada.md` para o motivo de ser curto e onde ele é registrado.

## `discovery.yaml`: o contrato entre extração e as etapas compartilhadas

Todo agente extrator — independentemente da stack de origem — produz `entrada/discovery.yaml` neste schema. É o que permite que `redator-documentacao`, `gerador-grafo`, `planejador`, `implementador-python` e `homologador` sejam agnósticos de stack: eles só leem este arquivo, nunca o artefato de origem diretamente.

`etapas` sempre vive dentro de um `modulo` — mesmo num processo pequeno de um módulo só. Isso mantém um único schema para qualquer tamanho de processo, em vez de um formato para processos simples e outro para monólitos. `modulo` é a unidade natural de divisão de cada stack (um módulo/classe VBA, um container ou macro do Alteryx, uma seção de notebook, um arquivo/classe C#) — ver `extracao-monolitos.md` para como cada stack decide onde ficam essas divisões.

```yaml
processo:
  nome: "Consolidação de Carteira Equities"
  objetivo_negocio: "Descrição em uma ou duas frases do porquê o processo existe"

entradas:
  - id: carteira_equities
    tipo: fswcorp            # fswcorp | email | sharepoint | api | saida_processo_legado | manual
    descricao: "..."
    localizacao: "\\fswcorp\...\arquivo.csv"
    formato: csv
    frequencia_atualizacao: diaria

modulos:
  - id: modulo_consolidacao          # slug curto, único dentro do discovery
    nome: "Consolidação de carteiras"
    origem: "modulo_vba: Modulo1"     # ver os valores possíveis por stack em extracao-monolitos.md
    descricao: "o que este módulo faz, em uma frase"
    etapas:
      - id: modulo_consolidacao__somar_posicoes   # <id-do-modulo>__<id-da-etapa>, único no discovery inteiro
        nome: "Soma de posições por ativo"
        tipo: transformacao       # transformacao | decisao | validacao
        descricao: "..."
        entradas_consumidas: [carteira_equities]  # id de uma `entrada`, ou id completo de outra `etapa` (dependência entre módulos)
        logica: "descrição da lógica de negócio: fórmulas, condições, regras aplicadas"
        codigo_original: |
          ' trecho literal da fonte por trás desta etapa -- corpo do Sub/Function VBA,
          ' fórmula do Excel, expressão/config do Alteryx, método C#, função Python.
          ' vem direto da saída do script de pré-processamento (extracao-monolitos.md);
          ' null se a etapa não tem um trecho de código único que a represente
          ' (ex: um passo inferido só por entrevista com o analista).
        regras_negocio:
          - "regra explícita extraída da fonte (fórmula, macro, tool de Alteryx, método C#)"

saidas:
  - id: relatorio_var
    nome: "Relatório de VaR consolidado"
    destino: "e-mail para mesa X"   # ou sharepoint | arquivo_local | api
    formato: xlsx
    consumido_por: "nome de outro processo, se aplicável"

riscos_pontos_atencao:
  - "ex: cálculo X depende de uma célula com valor hardcoded na planilha original; confirmar com o dono do processo antes de implementar"

glossario:
  - termo: "VaR"
    definicao: "..."
```

`riscos_pontos_atencao` e `glossario` continuam como lista plana no topo — não crescem na mesma proporção que `etapas` num monólito, não precisam de agrupamento por módulo.

`codigo_original` é o que permite ao `redator-documentacao` citar código de verdade em `doc_tecnico.md` (as "principais funções" do processo, não uma paráfrase) sem reabrir o arquivo de origem. `regras_negocio` continua sendo a leitura em prosa da mesma coisa — as duas convivem: uma pro leitor técnico que quer o trecho exato, outra pro `planejador`/`redator-documentacao` que precisa de uma frase para referenciar a regra em outro lugar.

Um extrator que não consegue preencher um campo com confiança deve registrá-lo em `riscos_pontos_atencao` em vez de inventar o valor — a incerteza vira uma pergunta para o analista/dono do processo, não uma suposição silenciosa.
