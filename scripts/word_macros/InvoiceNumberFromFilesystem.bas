Attribute VB_Name = "InvoiceNumberFromFilesystem"
Option Explicit

Function GetNextInvoiceNumber() As String
    Dim sh As Object, ex As Object
    Dim s As String

    Set sh = CreateObject("WScript.Shell")
    Set ex = sh.Exec("cmd /c uv run R:\paul_r\invoice_number.py")

    Do While ex.Status = 0
        DoEvents
    Loop

    s = ex.StdOut.ReadAll
    s = Replace(s, vbCr, "")
    s = Replace(s, vbLf, "")
    s = Trim(s)

    GetNextInvoiceNumber = s
End Function

Function GetNextInvoiceNumberClip() As String
    Dim sh As Object
    Dim cmd As String
    Dim s As String
    Dim clipData As Object

    Set sh = CreateObject("WScript.Shell")
    
    ' The | clip command sends the Python script's console output directly to RAM clipboard
    cmd = "cmd /c uv run R:\paul_r\invoice_number.py | clip"
    
    ' 0 hides the window completely, True waits for it to finish
    sh.Run cmd, 0, True

    ' Retrieve the text from the Windows Clipboard using HTML memory objects
    Set clipData = CreateObject("htmlfile")
    s = clipData.parentWindow.clipboardData.GetData("text")

    ' Clean up formatting
    s = Replace(s, vbCr, "")
    s = Replace(s, vbLf, "")
    GetNextInvoiceNumberClip = Trim(s)
End Function

Sub FillInvoiceNumber()
    Dim tbl As Table
    Dim i As Long
    Dim labelText As String
    Dim inv As String
    Dim r As Range

    inv = GetNextInvoiceNumberClip()
    If inv = "" Then
        MsgBox "No invoice number returned.", vbExclamation
        Exit Sub
    End If

    For Each tbl In ActiveDocument.Tables
        For i = 1 To tbl.Rows.Count
            labelText = tbl.Cell(i, 1).Range.Text
            labelText = Replace(labelText, Chr(13) & Chr(7), "")
            labelText = Trim(labelText)

            If InStr(1, labelText, "Invoice No", vbTextCompare) > 0 Then
                Set r = tbl.Cell(i, 2).Range
                r.End = r.End - 1   ' keep end-of-cell marker
                r.Text = inv
                Exit Sub
            End If
        Next i
    Next tbl

    MsgBox "'Invoice No' row not found.", vbExclamation
End Sub

