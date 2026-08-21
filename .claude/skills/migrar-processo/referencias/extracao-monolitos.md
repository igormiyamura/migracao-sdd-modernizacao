# Extração de monólitos

Referência compartilhada pelos cinco agentes extratores (`.claude/agents/extrator-*.md`). Processos reais desta área costumam ser monólitos — macro VBA de ~1000 linhas com várias classes, workflow Alteryx com dezenas de ferramentas encadeadas (às vezes com ferramentas Python embutidas), script ou notebook Python de ~1000 linhas. Ler isso tudo numa passada só, direto do arquivo bruto, estoura contexto e dilui atenção — a lógica enterrada no meio do arquivo é justamente a que mais escapa. Este documento descreve como qualquer extrator lida com isso; os arquivos de agente só têm a regra específica da stack (onde ficam os limites de módulo, o que o script de pré-processamento produz).

## 1. Script primeiro, LLM depois

Antes de ler o conteúdo do arquivo de origem, rode o script de pré-processamento correspondente (`scripts/`) e leia a saída dele — nunca o arquivo bruto (XML do Alteryx, ZIP/XML do `.xlsx`, binário OLE do VBA, JSON do `.ipynb` com outputs em base64). O script é determinístico, testado uma vez, reusado em toda extração — mais barato e mais confiável que o LLM reimplementar o parsing a cada execução:

| Stack | Script | Produz |
|---|---|---|
| Excel | `scripts/extrair_excel.py` | fórmulas, ranges nomeados, validação de dados e formatação condicional por aba, em YAML compacto |
| VBA | `scripts/extrair_vba.py` | um bloco por módulo/classe: assinatura + corpo de cada `Sub`/`Function`/`Property`, grafo de chamadas entre eles |
| Alteryx | `scripts/extrair_alteryx.py` | lista de nós (tipo, config, expressão) e conexões do XML, com ferramentas Python embutidas marcadas à parte |
| Python/notebook | `scripts/extrair_notebook.py` | células de código e markdown em ordem, sem outputs/imagens; script `.py` puro passa direto, sem transformação |
| C# | nenhum — código-fonte já é texto direto, sem overhead de formato a comprimir | — |

Se o script falhar (arquivo corrompido, formato inesperado), registre isso em `riscos_pontos_atencao` e caia para leitura manual do arquivo bruto — não pare a extração por causa de uma falha de parsing.

## 2. Dividir por módulo, nunca por contagem de linhas

Um "módulo" é o limite estrutural natural da stack, não um corte arbitrário de N linhas:

- **VBA**: cada módulo padrão (`.bas`) e cada classe (`.cls`/`.frm`) é um módulo. Uma classe com `Property`/métodos vira um módulo cujas `etapas` documentam o que cada método faz e o que cada `Property` representa como dado.
- **Alteryx**: cada container de ferramentas (`Tool Container`) que o próprio workflow já usa para se organizar é um módulo. Sem containers, agrupe pelas regiões conectadas entre um `Input`/`Output` e o próximo — a mesma régua do `gerador-grafo` para nós agrupados. Uma ferramenta Python embutida é sempre seu próprio módulo, do tipo `python_embutido` (seção 4).
- **Python/notebook**: num notebook, cada seção demarcada por uma célula de markdown com título é um módulo; sem seções marcadas, ou num `.py` puro, agrupe por função/classe de nível superior, e o bloco de código solto (não function-wrapped, comum em notebook) vira um módulo "execução principal".
- **C#**: cada classe é um módulo; uma classe muito grande (ver seção 3) divide por grupo de métodos públicos relacionados.
- **Excel sem macro**: cada aba é um módulo; uma aba com muitas fórmulas desconexas divide por região (grupo de células que se referenciam mutuamente).

## 3. Modo monólito: quando ativa, sequencial com checkpoint

Ative automaticamente (sem perguntar ao analista) quando o script de pré-processamento indicar:

- **VBA**: ≥2 módulos/classes, ou >300 linhas somadas.
- **Alteryx**: qualquer ferramenta Python embutida, ou >30 ferramentas no workflow.
- **Python/notebook**: sempre para `.ipynb`; para `.py`, >200 linhas.
- **C#**/**Excel sem macro**: mesma régua de bom senso — muitos arquivos/classes, ou uma aba com dezenas de fórmulas interdependentes.

Esses números são um ponto de partida, não uma trava rígida — ajustável conforme a experiência real com processos migrados. Ao ativar, avise o analista numa frase (“processo grande detectado, N módulos — vou extrair um por vez e salvar progresso”) e siga.

**Mecânica**: mantenha `.sdd/memoria/progresso_discovery.yaml` com a lista de módulos identificados (a partir da saída do script) e o status de cada um (`pendente`/`em_andamento`/`concluido`). Processe um módulo por vez, e depois de concluir cada um, **grave imediatamente** o bloco correspondente em `entrada/discovery.yaml` (append, não espere terminar tudo para escrever) e atualize o status em `progresso_discovery.yaml`. Se a extração for interrompida, retomar significa ler `progresso_discovery.yaml` e continuar do primeiro módulo `pendente` — nunca reprocessar um módulo já `concluido`.

Módulo sem nenhuma regra de negócio (só glue code, setup, formatação) ainda entra no discovery com `etapas: []` e uma `descricao` dizendo o que ele é — não pule módulos silenciosamente; um módulo ausente do discovery é indistinguível de um módulo esquecido.

## 4. Fan-out: quando um módulo sozinho ainda é grande demais

Se, depois de dividido por módulo, um módulo individual ainda for grande demais para uma passada só (ex: uma classe VBA de milhares de linhas, uma ferramenta Python embutida extensa), despache uma sub-extração — um agente com contexto próprio, dedicado só àquele módulo — seguindo o mesmo procedimento de divisão (seção 2) recursivamente dentro dele. A sub-extração devolve só o bloco `modulo` (com seu `id` e suas `etapas` já prefixadas), que o extrator principal funde no `discovery.yaml` da mesma forma que um módulo processado inline.

Isso é diferente do modo monólito (seção 3): modo monólito divide o **processo inteiro** em módulos processados em sequência por um único agente; fan-out divide **um módulo específico** que não coube numa passada, delegando a um agente à parte. Um processo pode estar em modo monólito sem nenhum módulo precisar de fan-out, e um processo pequeno (um módulo só) pode ainda assim precisar de fan-out se aquele módulo único for enorme.

## 5. Nomenclatura entre módulos

`modulo.id` é um slug curto e único dentro do discovery (`modulo_consolidacao`, não `modulo_1`). `etapa.id` é sempre `<modulo.id>__<nome_curto>`. Uma etapa que depende de outra em módulo diferente referencia o `id` completo dela em `entradas_consumidas` — é assim que o `gerador-grafo` desenha dependência entre módulos, e o `planejador` ordena a implementação entre eles.
