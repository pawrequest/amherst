Attribute VB_Name = "ProcessLastInvoice"
Option Explicit

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

    sourceFolder = "C:\ProgramData\Commence\Commence\8.0\letters"
    destFolder = "R:\ACCOUNTS\invoices\"


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
    invoiceNum = GetInvoiceNumberFromDoc(ActiveDocument)

    If invoiceNum = "UNKNOWN" Then
        MsgBox "Invoice number not found in the document.", vbExclamation
        ActiveDocument.Close SaveChanges:=False
        Exit Sub
    End If

    newName = invoiceNum & ".docx"
    pdfName = invoiceNum & ".pdf"
    Dim newDocPath As String
    Dim newPdfPath As String
    newDocPath = destFolder & newName
    newPdfPath = destFolder & pdfName


    ' Check if the DOCX file already exists
    If fso.FileExists(newDocPath) Then
        MsgBox "File already exists: " & newDocPath, vbExclamation
        Exit Sub
    End If

    ' Check if the PDF file already exists
    If fso.FileExists(newPdfPath) Then
        MsgBox "PDF already exists: " & newPdfPath, vbExclamation
        Exit Sub
    End If

    ' Save to destination
    ActiveDocument.SaveAs2 FileName:=newDocPath, FileFormat:=wdFormatXMLDocument

    ' Export to PDF
    ActiveDocument.ExportAsFixedFormat _
        OutputFileName:=newPdfPath, _
        ExportFormat:=wdExportFormatPDF

    ' Link invoice.doc to commence
    Dim recordName As String
    recordName = ReadHiddenDataRow("CMCNAME")
        
    Call LinkCommenceInvoice("Hire", recordName, newDocPath)

    ' Close document
    ActiveDocument.Close SaveChanges:=False

    MsgBox "Invoice saved as:" & vbCrLf & newDocPath & vbCrLf & newPdfPath & vbCrLf & "+ linked to commence", vbInformation
End Sub


Function GetInvoiceNumberFromDoc(doc As Document) As String
    Dim tbl As Table
    Dim row As row
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
                GetInvoiceNumberFromDoc = Trim(tbl.Cell(i, 2).Range.Text)
                GetInvoiceNumberFromDoc = Replace(GetInvoiceNumberFromDoc, Chr(13) & Chr(7), "") ' Clean up
                Exit Function
            End If
        Next i
    Next tbl

    ' Not found
    GetInvoiceNumberFromDoc = "UNKNOWN"
End Function




