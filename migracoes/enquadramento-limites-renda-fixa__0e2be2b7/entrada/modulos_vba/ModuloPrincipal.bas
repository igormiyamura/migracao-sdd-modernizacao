Attribute VB_Name = "ModuloPrincipal"
Option Explicit

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
