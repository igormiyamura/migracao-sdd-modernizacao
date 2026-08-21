VERSION 1.0 CLASS
Attribute VB_Name = "ClasseLimite"
Option Explicit

Private mBook As String
Private mValorLimite As Double
Private mValorUtilizado As Double

Public Property Let Book(valor As String)
    mBook = valor
End Property
Public Property Get Book() As String
    Book = mBook
End Property

Public Property Let ValorLimite(valor As Double)
    mValorLimite = valor
End Property
Public Property Get ValorLimite() As Double
    ValorLimite = mValorLimite
End Property

Public Property Let ValorUtilizado(valor As Double)
    mValorUtilizado = valor
End Property
Public Property Get ValorUtilizado() As Double
    ValorUtilizado = mValorUtilizado
End Property

Public Property Get PercentualUtilizado() As Double
    If mValorLimite = 0 Then
        PercentualUtilizado = 0
    Else
        PercentualUtilizado = mValorUtilizado / mValorLimite
    End If
End Property

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
