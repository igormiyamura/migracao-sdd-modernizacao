Attribute VB_Name = "ModuloConsolidacao"
Option Explicit

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
