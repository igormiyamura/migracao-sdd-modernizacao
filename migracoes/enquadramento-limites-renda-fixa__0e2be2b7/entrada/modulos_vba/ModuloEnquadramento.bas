Attribute VB_Name = "ModuloEnquadramento"
Option Explicit

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
