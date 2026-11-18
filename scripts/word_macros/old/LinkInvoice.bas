Const DEBUG_MODE As Boolean = False



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
    Dim cmdExt As String
    Dim exitCode As Long

    cmdExt = "R:\paul_r\link_invoice.py " & _
        """" & category & """ " & _
        """" & recordName & """ " & _
        """" & invoicePath & """"

    Set sh = CreateObject("WScript.Shell")
    If DEBUG_MODE Then
        cmd = "cmd /k uv run " & cmdExt
        MsgBox cmd
        exitCode = sh.Run(cmd, 1, True)
    Else
        cmd = "cmd /c uv run " & cmdExt
        exitCode = sh.Run(cmd, 0, True)
    End If

    If exitCode <> 0 Then
        MsgBox "link_invoice.py failed with exit code " & exitCode, vbExclamation
    End If

    LinkCommenceInvoice = exitCode
End Function

