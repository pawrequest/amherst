Attribute VB_Name = "LinkInvoice"
Function ReadHiddenDataRow(labelText As String) As String
    ' Reads from the cell next to that with labelText in it
    Dim tbl As Table
    Dim i As Long
    Dim cellText As String
    Dim wasShowingHidden As Boolean
    wasShowingHidden = ActiveDocument.ActiveWindow.View.ShowHiddenText
    ActiveDocument.ActiveWindow.View.ShowHiddenText = True

    For Each tbl In ActiveDocument.Tables
        For i = 1 To tbl.Rows.Count
            cellText = Replace(Trim(tbl.Cell(i, 1).Range.Text), Chr(13) & Chr(7), "")
            If cellText = labelText Then
                ReadHiddenDataRow = Replace(Trim(tbl.Cell(i, 2).Range.Text), Chr(13) & Chr(7), "")
                Exit Function
            End If
        Next i
    Next tbl
    ActiveDocument.ActiveWindow.View.ShowHiddenText = wasShowingHidden

End Function

Function LinkCommenceInvoice(category As String, recordName As String, invoicePath As String)
    Dim sh As Object
    Dim cmd As String
    cmd = "cmd /c uv run C:\prdev\amdev\amherst\src\amherst\addons\link_invoice.py " & _
      """" & category & """ " & _
      """" & recordName & """ " & _
      """" & invoicePath & """"
      
    
    Set sh = CreateObject("WScript.Shell")

    Dim exitCode As Long
    exitCode = sh.Run(cmd, 0, True)  ' 0 = hidden window, True = wait/block

    If exitCode <> 0 Then
        MsgBox "link_invoice.py failed with exit code " & exitCode, vbExclamation
    End If

    LinkCommenceInvoice = exitCode
End Function

