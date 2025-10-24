Sub ProcessLatestInvoice()
    Dim sourceFolder As String
    Dim destFolder As String
    Dim fso As Object
    Dim folder As Object
    Dim file As Object
    Dim latestFile As Object
    Dim latestDate As Date
    Dim newName As String
    Dim pdfName As String

    sourceFolder = "C:\ProgramData\Commence\Commence\8.0\letters\"
    destFolder = "C:\prdev\wordmacro\dest\"


    Set fso = CreateObject("Scripting.FileSystemObject")
    ' Check if folders exist
    If Not fso.FolderExists(sourceFolder) Then
        MsgBox "Source folder does not exist: " & sourceFolder
        Exit Sub
    End If
    If Not fso.FolderExists(destFolder) Then
        MsgBox "Destination folder does not exist: " & destFolder
        Exit Sub
    End If

    Set folder = fso.GetFolder(sourceFolder)
    latestDate = 0

    ' Find latest .docx file
    For Each file In folder.Files
        Dim ext As String
        ext = LCase(fso.GetExtensionName(file.Name))
        If (ext = "docx" Or ext = "doc") And Left(file.Name, 2) <> "~$" Then
            If file.DateLastModified > latestDate Then
                Set latestFile = file
                latestDate = file.DateLastModified
            End If
        End If
    Next

    If latestFile Is Nothing Then
        MsgBox "No .docx files found in: " & sourceFolder
        Exit Sub
    End If

    ' Open the latest document
    Documents.Open latestFile.Path
    Dim invoiceNum As String
    invoiceNum = GetInvoiceNumber(ActiveDocument)

    If invoiceNum = "UNKNOWN" Then
        MsgBox "Invoice number not found in the document.", vbExclamation
        ActiveDocument.Close SaveChanges:=False
        Exit Sub
    End If

    newName = invoiceNum & ".docx"
    pdfName = invoiceNum & ".pdf"

    ' Check if the DOCX file already exists
    If fso.FileExists(destFolder & newName) Then
        MsgBox "File already exists: " & newName, vbExclamation
        Exit Sub
    End If

    ' Check if the PDF file already exists
    If fso.FileExists(destFolder & pdfName) Then
        MsgBox "PDF already exists: " & pdfName, vbExclamation
        Exit Sub
    End If

    ' Save to destination
    ActiveDocument.SaveAs2 fileName:=destFolder & newName, FileFormat:=wdFormatXMLDocument

    ' Export to PDF
    ActiveDocument.ExportAsFixedFormat _
        OutputFileName:=destFolder & pdfName, _
        ExportFormat:=wdExportFormatPDF

    ' Close document
    ActiveDocument.Close SaveChanges:=False

    MsgBox "Invoice saved as:" & vbCrLf & newName & vbCrLf & pdfName, vbInformation
End Sub


Function GetInvoiceNumber(doc As Document) As String
    Dim tbl As Table
    Dim row As Row
    Dim cellText As String
    Dim i As Long

    ' Loop through all tables in the document
    For Each tbl In doc.Tables
        ' Loop through each row in the table
        For i = 1 To tbl.Rows.Count
            cellText = Trim(tbl.Cell(i, 1).Range.Text)
            cellText = Replace(cellText, Chr(13) & Chr(7), "") ' Clean up

            ' Check if the cell contains "Invoice No."
            If InStr(1, cellText, "Invoice No", vbTextCompare) > 0 Then
                ' Return the value from the next cell in the same row
                GetInvoiceNumber = Trim(tbl.Cell(i, 2).Range.Text)
                GetInvoiceNumber = Replace(GetInvoiceNumber, Chr(13) & Chr(7), "") ' Clean up
                Exit Function
            End If
        Next i
    Next tbl

    ' Not found
    GetInvoiceNumber = "UNKNOWN"
End Function
