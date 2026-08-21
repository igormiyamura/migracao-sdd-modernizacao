Attribute VB_Name = "ModuloNotificacao"
Option Explicit

Private Const EMAIL_HEAD_RISCO As String = "head.risco@banco.com.br"
Private Const EMAIL_HEAD_MESA As String = "head.mesarendafixa@banco.com.br"
Private Const CAMINHO_LOG As String = "\\fswcorp\risco\rendafixa\log_enquadramento.csv"

Sub NotificarEExportar(limites As Collection)
    Dim limite As ClasseLimite
    Dim fso As Object, arq As Object

    Set fso = CreateObject("Scripting.FileSystemObject")
    Set arq = fso.CreateTextFile(CAMINHO_LOG, True)
    arq.WriteLine "book,limite,utilizado,percentual,status"

    For Each limite In limites
        arq.WriteLine limite.Book & "," & limite.ValorLimite & "," & limite.ValorUtilizado & _
            "," & limite.PercentualUtilizado & "," & limite.Status

        If limite.Status = "EXCEDIDO" Then
            EnviarEmail EMAIL_HEAD_RISCO, "EXCEDIDO: limite de " & limite.Book, limite
        ElseIf limite.Status = "ALERTA" Then
            EnviarEmail EMAIL_HEAD_MESA, "ALERTA: limite de " & limite.Book, limite
        End If
    Next limite

    arq.Close
End Sub

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
