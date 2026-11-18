Attribute VB_Name = "MergeAndProcessInvoice"
Sub MergeAndProcessInvoice()
    Call FillInvoiceNumber
    Application.Run "cmcmerge.dot!createContinueMerge"
    PauseMacro (3)
    Call ProcessLatestInvoice
End Sub

Sub MergeAndProcessInvoice2()
    If Not FillInvoiceNumberFn() Then
        Exit Sub
    End If
    Application.Run "cmcmerge.dot!createContinueMerge"
    PauseMacro (3)
    Call ProcessLatestInvoice
End Sub



Sub PauseMacro(Seconds As Single)
    Dim EndTime As Double
    EndTime = Timer + Seconds
    
    ' Loop until the designated time has passed
    Do While Timer < EndTime
        ' DoEvents allows Word to process background mail-merge tasks during the pause
        DoEvents
    Loop
End Sub
