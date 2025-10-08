Sub aProcessLatestInvoice()
    Dim sourceFolder As String
    Dim destFolder As String
    Dim fso As Object
    Dim folder As Object
    Dim file As Object
    Dim latestFile As Object
    Dim latestDate As Date
    Dim newName As String
    Dim pdfName As String

    sourceFolder = "C:\prdev\wordmacro\source\"
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
        If Right(LCase(file.Name), 5) = ".docx" Then
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

    ' Build new name
    newName = "Invoice_" & Format(Now, "yyyymmdd_HHMMSS") & ".docx"
    pdfName = Replace(newName, ".docx", ".pdf")

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


