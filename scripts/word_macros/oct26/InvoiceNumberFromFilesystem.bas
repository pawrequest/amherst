Attribute VB_Name = "InvoiceNumberFromFilesystem"
Option Explicit


Function GetNextInvoiceNumber() As String
    ' use clipboard = hide shell
    Dim sh As Object
    Dim cmd As String
    Dim s As String
    Dim clipData As Object

    Set sh = CreateObject("WScript.Shell")
    
    ' The | clip command sends the Python script's console output directly to RAM clipboard
    cmd = "cmd /c uv run R:\paul_r\current\scripts\py\invoice_number.py | clip"
    
    ' 0 hides the window completely, True waits for it to finish
    sh.Run cmd, 0, True

    ' Retrieve the text from the Windows Clipboard using HTML memory objects
    Set clipData = CreateObject("htmlfile")
    s = clipData.parentWindow.clipboardData.GetData("text")

    ' Clean up formatting
    s = Replace(s, vbCr, "")
    s = Replace(s, vbLf, "")
    GetNextInvoiceNumber = Trim(s)
End Function


Function FillInvoiceNumber(invNum)
    Dim tbl As Table
    Dim i As Long
    Dim labelText As String
    Dim r As Range
    
    For Each tbl In ActiveDocument.Tables
        For i = 1 To tbl.Rows.Count
            labelText = tbl.Cell(i, 1).Range.Text
            labelText = Replace(labelText, Chr(13) & Chr(7), "")
            labelText = Trim(labelText)

            If InStr(1, labelText, "Invoice No", vbTextCompare) > 0 Then
                Set r = tbl.Cell(i, 2).Range
                r.End = r.End - 1   ' keep end-of-cell marker
                r.Text = invNum
                FillInvoiceNumber = True
                Exit Function
            End If
        Next i
    Next tbl

    MsgBox "'Invoice No' row not found.", vbExclamation
    FillInvoiceNumber = False
End Function
