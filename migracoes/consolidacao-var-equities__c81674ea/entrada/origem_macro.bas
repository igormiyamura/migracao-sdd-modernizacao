Attribute VB_Name = "Modulo1"
Option Explicit

Private Const CAMINHO_SAIDA As String = "\\fswcorp\risco\equities\relatorio_var.csv"
Private Const EMAIL_ALERTA As String = "mesa.equities@banco.com.br"

Sub AtualizarRelatorioVaR()
    Dim wsRelatorio As Worksheet
    Dim varTotal As Double
    Dim status As String

    Set wsRelatorio = ThisWorkbook.Sheets("Relatorio")
    wsRelatorio.Calculate

    varTotal = wsRelatorio.Range("D2").Value
    status = wsRelatorio.Range("F2").Value

    ExportarRelatorioCSV wsRelatorio

    If status = "EXCEDIDO" Then
        EnviarAlertaLimite varTotal
    End If
End Sub

Private Sub ExportarRelatorioCSV(ws As Worksheet)
    Dim ultimaLinha As Long
    ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

    Dim fso As Object, arq As Object
    Dim i As Long

    Set fso = CreateObject("Scripting.FileSystemObject")
    Set arq = fso.CreateTextFile(CAMINHO_SAIDA, True)

    arq.WriteLine "ativo,exposicao,var_individual,var_total,limite_var,status"
    For i = 2 To ultimaLinha
        arq.WriteLine ws.Cells(i, 1).Value & "," & ws.Cells(i, 2).Value & "," & _
            ws.Cells(i, 3).Value & "," & ws.Cells(i, 4).Value & "," & _
            ws.Cells(i, 5).Value & "," & ws.Cells(i, 6).Value
    Next i
    arq.Close
End Sub

Private Sub EnviarAlertaLimite(varTotal As Double)
    Dim outlookApp As Object, mail As Object

    Set outlookApp = CreateObject("Outlook.Application")
    Set mail = outlookApp.CreateItem(0)

    mail.To = EMAIL_ALERTA
    mail.Subject = "ALERTA: VaR consolidado acima do limite"
    mail.Body = "O VaR total da carteira Equities (" & Format(varTotal, "#,##0.00") & _
        ") ultrapassou o limite configurado. Verificar exposicoes."
    mail.Send
End Sub

Private Sub Workbook_Open()
    AtualizarRelatorioVaR
End Sub
