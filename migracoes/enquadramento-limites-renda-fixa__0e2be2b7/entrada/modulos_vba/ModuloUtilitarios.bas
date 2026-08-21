Attribute VB_Name = "ModuloUtilitarios"
Option Explicit

Function FormatarDataLog() As String
    FormatarDataLog = Format(Now, "yyyy-mm-dd hh:nn:ss")
End Function

Sub RegistrarLog(mensagem As String)
    Debug.Print FormatarDataLog() & " - " & mensagem
End Sub
