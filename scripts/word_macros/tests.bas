Attribute VB_Name = "tests"
Option Explicit

Sub TestReadHiddenDataRow()
    Dim nm As String
    nm = ReadHiddenDataRow("CMCNAME")
    Selection.TypeText nm
    MsgBox nm

End Sub


