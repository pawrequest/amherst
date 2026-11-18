Attribute VB_Name = "MergeAndProcessInvoice"
Option Explicit

Sub PauseMacro(Seconds As Single)
    Dim EndTime As Double
    EndTime = Timer + Seconds
    
    ' Loop until the designated time has passed
    Do While Timer < EndTime
        ' DoEvents allows Word to process background mail-merge tasks during the pause
        DoEvents
    Loop
End Sub

Sub MergeAndProcessInvoice()
    Dim filled As Boolean
    Dim invNum As String
    Dim newDocPath As String
            
    invNum = GetNextInvoiceNumber()
    If Not FillInvoiceNumber(invNum) Then
        MsgBox ("Failed To Fill Invoice Number")
        Exit Sub
    End If
    Application.Run "cmcmerge.dot!createContinueMerge"
    PauseMacro (3) ' wait for commence
    
    newDocPath = a_MoveLastInvoice
    
    ' Link invoice.doc to commence
    Dim recordName As String
    Dim category As String
    recordName = ReadHiddenDataRow("CMCNAME99999")
    category = ReadHiddenDataRow("CMCCATEGORY99999")
        
    Call LinkCommenceInvoice(category, recordName, newDocPath)

End Sub
