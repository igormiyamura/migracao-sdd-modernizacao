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
| Excel + VBA | arquivo `.xlsm` com macros habilitadas | código VBA exportado (`.bas`/`.cls`/`.frm`) do editor VBA |
| Alteryx | workflow `.yxmd`/`.yxwz` | arquivos `.yxdb` referenciados pelo workflow |
| C# | acesso ao código-fonte (solution/projeto) | — |
| Python legado | script(s) `.py` existentes | lista de dependências usadas, mesmo informal |

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

etapas:
  - id: consolidar_carteiras
    nome: "Consolidação de carteiras"
    tipo: transformacao       # transformacao | decisao | validacao
    descricao: "..."
    entradas_consumidas: [carteira_equities]
    logica: "descrição da lógica de negócio: fórmulas, condições, regras aplicadas"
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

Um extrator que não consegue preencher um campo com confiança deve registrá-lo em `riscos_pontos_atencao` em vez de inventar o valor — a incerteza vira uma pergunta para o analista/dono do processo, não uma suposição silenciosa.
