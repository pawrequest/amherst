$OBJECT=Form

Option Explicit

' set name if is add (on leave dummy field), save before adding items, check for empty repairs (on save)


Sub Form_OnLoad()
    'msgbox("debug REPAIR v3")
End Sub

Sub Form_OnLeaveField(ByVal FieldName)
    ' Set new item Name if we leave the dummy field
    if FieldName = "dummy" Then
        if Form.IsAdd Then
            if Form.Field("Name").Value = "" Then
                AutoName()
            End If
            if Form.Field("Date Opened").Value = "" Then
                Form.Field("Date Opened").Value = FormatDateTime(Now, vbShortDate)
            End If
        End If
    End if
End Sub

Sub Form_OnEnterField(ByVal FieldName)
    ' save before adding items (for naming)
    if Form.IsAdd Then
        if FieldName = "Includes Repair Line" Then
            SaveFirst()

        End If
    End If


End Sub

Sub Form_OnSave()
' check we save with no items
    if IsEmpty() = 1 Then
        SaveEmpty()
    end if
    NoCustomer()

End Sub

Sub Form_OnCancel()
End Sub

Sub Form_OnEnterTab(ByVal Tab0)

End Sub

Sub Form_OnLeaveTab(ByVal Tab0)
End Sub





Sub Form_OnActiveXControlEvent(ByVal ControlName, ByVal EventName, ByVal ParameterArray)
End Sub

Sub AutoName()
' Set Name from connected customer
    Dim cCust, sCustName, sRepairName
    set cCust = Form.Connection("For", "Customer")

    sCustName = cCust.FieldValue("Name")
    sRepairName = sCustName & " - " & Now

    Form.Field("Name").Value = sRepairName
    ' NameLineItems(sCustName)
End Sub


Function IsEmpty()
    dim cLines, nLines, i, sLineName, oLine
    set cLines = Form.Connection("Includes","Repair Line")
    nLines = cLines.ConnectedItemCount
    if nLines < 1 Then

        IsEmpty = 1
    else
        IsEmpty = 0

    end if


End Function


Sub SaveFirst()
 ' Show message box with Yes, No, and Cancel options
        Dim userChoice
        userChoice = MsgBox("Can't add items until saved. Save and exit now? ('Cancel' to exit without saving)", vbYesNoCancel + vbQuestion, "Save Form")

        ' Handle user's choice
        If userChoice = vbYes Then
            ' If Yes, save the form
            Form.Save()
        ElseIf userChoice = vbNo Then
            ' If No, do nothing (user chose not to save)
            MsgBox "Form will not be saved."
        ElseIf userChoice = vbCancel Then
            ' If Cancel, do nothing (user canceled)
            Form.Cancel()
        End If
End Sub


Sub SaveEmpty()
    Dim userChoice
    userChoice = MsgBox("Really Save an empty Repair? ('No' to exit without saving)", vbYesNo + vbQuestion, "Save Form")
    If userChoice = vbNo Then
        Form.Cancel()
    End If
End Sub


Sub NoCustomer()
    dim cCust
    set cCust = Form.Connection("For", "Customer")
    if cCust.ConnectedItemCount < 1 Then
        MsgBox "No Customer connected to this Repair. Please connect a Customer"
        Form.MoveToField("For Customer")
        Form.Abort
    end if
End Sub

