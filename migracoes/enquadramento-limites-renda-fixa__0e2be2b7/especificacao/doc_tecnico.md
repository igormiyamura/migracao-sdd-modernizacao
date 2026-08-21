# Apuração de Enquadramento de Limites - Mesa de Renda Fixa -- Documentação técnica

## Stack de origem

Excel + VBA -- ver `entrada/origem_planilha.xlsx` (abas Posicoes/Limites/Resumo) e `entrada/modulos_vba/` (5 módulos + 1 classe, exportados do editor VBA). Monólito real: 6 unidades de código (`.bas`/`.cls`), extração feita em modo checkpoint incremental (ver `.sdd/memoria/progresso_discovery.yaml`).

## Fluxo do processo

![Grafo do processo](grafo_processo.mmd)

`ModuloPrincipal` é o único ponto de entrada (`Workbook_Open` chama `RodarApuracao`), que dispara os outros três módulos em sequência fixa, sem paralelismo: `ModuloConsolidacao` → `ModuloEnquadramento` → `ModuloNotificacao`. `ClasseLimite` não é chamada diretamente pelo `ModuloPrincipal` — é instanciada dentro de `ModuloEnquadramento`, uma vez por book, e usada por `ModuloNotificacao` para decidir o roteamento de e-mail. `ModuloUtilitarios` é chamado nas duas pontas (log de início/fim), sem participar da lógica de negócio.

## Módulos e principais funções

### Objeto de limite (ClasseLimite) — `classe_vba: ClasseLimite.cls`

Representa o limite de um book: guarda o valor limite e o valor utilizado, e calcula o percentual de uso e a classificação de severidade.

#### Cálculo do percentual de utilização do limite (transformacao)

`PercentualUtilizado = ValorUtilizado / ValorLimite`, com proteção para `ValorLimite = 0` (retorna 0 em vez de erro de divisão).

Regras de negócio:
- `PercentualUtilizado = ValorUtilizado / ValorLimite` (0 se `ValorLimite = 0`, não erro)

Código original:

```vba
Public Property Get PercentualUtilizado() As Double
    If mValorLimite = 0 Then
        PercentualUtilizado = 0
    Else
        PercentualUtilizado = mValorUtilizado / mValorLimite
    End If
End Property
```

#### Classificação de severidade do enquadramento (decisao)

Classifica o book em `OK`, `ALERTA` ou `EXCEDIDO`. Os dois limiares (80%, 100%) estão hardcoded na Property, sem parametrização — ver "Regras e decisões de negócio" em `doc_negocio.md`.

Regras de negócio:
- `Status = EXCEDIDO` se `PercentualUtilizado > 100%`
- `Status = ALERTA` se `80% <= PercentualUtilizado <= 100%`
- `Status = OK` se `PercentualUtilizado < 80%`

Código original:

```vba
Public Property Get Status() As String
    Dim pct As Double
    pct = Me.PercentualUtilizado
    If pct > 1 Then
        Status = "EXCEDIDO"
    ElseIf pct >= 0.8 Then
        Status = "ALERTA"
    Else
        Status = "OK"
    End If
End Property
```

### Consolidação de DV01 por book — `modulo_vba: ModuloConsolidacao.bas`

#### Consolidação de DV01 por book (transformacao)

Percorre a aba `Posicoes` e soma `Quantidade * DV01Unitario`, agrupado por `Book`, num `Scripting.Dictionary`.

Regras de negócio:
- DV01 da posição = `Quantidade * DV01Unitario`
- DV01 do book = soma do DV01 de todas as posições daquele book

Código original:

```vba
Function ConsolidarDV01PorBook() As Object
    Dim wsPos As Worksheet
    Dim dictBooks As Object
    Dim ultimaLinha As Long, i As Long
    Dim book As String, dv01 As Double

    Set wsPos = ThisWorkbook.Sheets("Posicoes")
    Set dictBooks = CreateObject("Scripting.Dictionary")

    ultimaLinha = wsPos.Cells(wsPos.Rows.Count, "A").End(xlUp).Row
    For i = 2 To ultimaLinha
        book = wsPos.Cells(i, 2).Value
        dv01 = wsPos.Cells(i, 3).Value * wsPos.Cells(i, 5).Value ' Quantidade * DV01Unitario

        If dictBooks.Exists(book) Then
            dictBooks(book) = dictBooks(book) + dv01
        Else
            dictBooks.Add book, dv01
        End If
    Next i

    Set ConsolidarDV01PorBook = dictBooks
End Function
```

### Avaliação de enquadramento — `modulo_vba: ModuloEnquadramento.bas`

#### Avaliação de enquadramento por book (transformacao)

Para cada linha da aba `Limites`, cria um `ClasseLimite` com o limite configurado e o DV01 consolidado correspondente.

Regras de negócio:
- Um `ClasseLimite` é criado por linha da aba `Limites` (não por book que aparece em `Posicoes`)
- Book presente em `Limites` mas sem posição em `Posicoes` recebe `ValorUtilizado = 0` (status `OK` por definição)

Código original:

```vba
Function AvaliarEnquadramento(dictExposicoes As Object) As Collection
    Dim wsLimites As Worksheet
    Dim ultimaLinha As Long, i As Long
    Dim resultado As New Collection
    Dim limite As ClasseLimite
    Dim book As String

    Set wsLimites = ThisWorkbook.Sheets("Limites")
    ultimaLinha = wsLimites.Cells(wsLimites.Rows.Count, "A").End(xlUp).Row

    For i = 2 To ultimaLinha
        book = wsLimites.Cells(i, 1).Value
        Set limite = New ClasseLimite
        limite.Book = book
        limite.ValorLimite = wsLimites.Cells(i, 2).Value
        If dictExposicoes.Exists(book) Then
            limite.ValorUtilizado = dictExposicoes(book)
        Else
            limite.ValorUtilizado = 0
        End If
        resultado.Add limite
    Next i

    Set AvaliarEnquadramento = resultado
End Function
```

### Notificação e exportação de log — `modulo_vba: ModuloNotificacao.bas`

#### Exportação do log de enquadramento (transformacao)

Grava um CSV com book, limite, utilizado, percentual e status de cada book, sobrescrevendo o arquivo anterior a cada execução.

Código original:

```vba
Sub NotificarEExportar(limites As Collection)
    Dim limite As ClasseLimite
    Dim fso As Object, arq As Object

    Set fso = CreateObject("Scripting.FileSystemObject")
    Set arq = fso.CreateTextFile(CAMINHO_LOG, True)
    arq.WriteLine "book,limite,utilizado,percentual,status"

    For Each limite In limites
        arq.WriteLine limite.Book & "," & limite.ValorLimite & "," & limite.ValorUtilizado & _
            "," & limite.PercentualUtilizado & "," & limite.Status
    Next limite

    arq.Close
End Sub
```

#### Notificação por e-mail conforme severidade (decisao)

Regras de negócio:
- `EXCEDIDO` → e-mail para head de risco
- `ALERTA` → e-mail para head da mesa
- `OK` → nenhum e-mail

Código original:

```vba
If limite.Status = "EXCEDIDO" Then
    EnviarEmail EMAIL_HEAD_RISCO, "EXCEDIDO: limite de " & limite.Book, limite
ElseIf limite.Status = "ALERTA" Then
    EnviarEmail EMAIL_HEAD_MESA, "ALERTA: limite de " & limite.Book, limite
End If

Private Sub EnviarEmail(destinatario As String, assunto As String, limite As ClasseLimite)
    Dim outlookApp As Object, mail As Object
    Set outlookApp = CreateObject("Outlook.Application")
    Set mail = outlookApp.CreateItem(0)
    mail.To = destinatario
    mail.Subject = assunto
    mail.Body = "Book " & limite.Book & ": utilizado " & Format(limite.PercentualUtilizado, "0.0%") & _
        " do limite de " & limite.ValorLimite
    mail.Send
End Sub
```

### Orquestração da apuração — `modulo_vba: ModuloPrincipal.bas`

#### Orquestração da apuração (transformacao)

Sequência fixa, sem paralelismo: `ConsolidarDV01PorBook` → `AvaliarEnquadramento` → `NotificarEExportar`. Disparada por `Workbook_Open`.

Código original:

```vba
Sub RodarApuracao()
    Dim exposicoes As Object
    Dim limites As Collection

    RegistrarLog "Iniciando apuracao de enquadramento"

    Set exposicoes = ConsolidarDV01PorBook()
    Set limites = AvaliarEnquadramento(exposicoes)
    NotificarEExportar limites

    RegistrarLog "Apuracao concluida"
End Sub

Private Sub Workbook_Open()
    RodarApuracao
End Sub
```

### Utilitários de log — `modulo_vba: ModuloUtilitarios.bas`

Funções auxiliares de formatação de data e log de depuração (`Debug.Print`). Sem lógica de negócio própria — nenhuma etapa associada (ver `entrada/discovery.yaml -> modulos[].etapas: []`).

## Entradas -- detalhe técnico

| id | tipo | localização | formato | schema |
|---|---|---|---|---|
| `posicoes_renda_fixa` | manual (colado) | `origem_planilha.xlsx!Posicoes` | xlsx | `Ativo (str), Book (str), Quantidade (int), PU (float), DV01Unitario (float)` |
| `limites_negociacao` | manual | `origem_planilha.xlsx!Limites` | xlsx | `Book (str), LimiteDV01 (float)` |

## Saídas -- detalhe técnico

| id | destino original | formato | schema |
|---|---|---|---|
| `log_enquadramento` | `\\fswcorp\risco\rendafixa\log_enquadramento.csv` (hardcoded) | csv | `book,limite,utilizado,percentual,status` |
| `alerta_limite_excedido` | Outlook, para `head.risco@banco.com.br` (hardcoded) | corpo de e-mail | percentual + limite do book |
| `alerta_limite_proximo` | Outlook, para `head.mesarendafixa@banco.com.br` (hardcoded) | corpo de e-mail | percentual + limite do book |

## Dependências e ambiente

- Excel com macros habilitadas; `Scripting.Dictionary` (biblioteca de automação do Windows, não nativa do VBA); automação COM do Outlook. Todas dependências Windows-specific, sem uso de lib externa de terceiros.
- Sem agendamento explícito: execução disparada por `Workbook_Open`.

## Pontos de atenção técnicos

- A aba `Resumo` contém fórmulas `SUMPRODUCT` que recalculam o mesmo DV01 por book de forma independente do VBA, mas não são lidas por nenhum procedimento — é uma segunda implementação da mesma regra de negócio (`ConsolidarDV01PorBook`), mantida só na planilha. As duas podem divergir sem nenhum aviso. Decisão de preservar ou não esse cálculo redundante na migração está em `doc_negocio.md`.
- `dictExposicoes.Exists(book)` retornando `False` é tratado como `ValorUtilizado = 0`, não como erro — um book mal digitado em `Limites` (que não bate com nenhum valor em `Posicoes`) silenciosamente vira "book zerado, dentro do limite", nunca gera um alerta de dado ausente.
- `CAMINHO_LOG`, `EMAIL_HEAD_RISCO` e `EMAIL_HEAD_MESA` são constantes hardcoded em `ModuloNotificacao` — na migração, viram configuração (`config.yaml`), não valores fixos no código-fonte.
- `fso.CreateTextFile(CAMINHO_LOG, True)` trunca o arquivo de log a cada execução — sem histórico de execuções anteriores.
