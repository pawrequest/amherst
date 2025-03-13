$OBJECT=Form

Option Explicit


Sub Form_OnLoad()
    ' msgbox("debug repair lineitem")
End Sub

Sub Form_OnSave()
    if Form.IsAdd() Then
        AutoName()
    End If

End Sub

Sub Form_OnCancel()
End Sub

Sub Form_OnEnterTab(ByVal TabName)
End Sub

Sub Form_OnLeaveTab(ByVal TabName)
End Sub

Sub Form_OnEnterField(ByVal SerialNumber)

End Sub

Sub Form_OnLeaveField(ByVal FieldName)
End Sub

Sub Form_OnActiveXControlEvent(ByVal ControlName, ByVal EventName, ByVal ParameterArray)
End Sub


sub AutoName()
    Dim cRepair, sCustName, sItemName, sType, sSerial, sIDMarks

    set cRepair = Form.Connection("Is Part Of","Repairs2")
    sCustName = cRepair.FieldValue("For Customer")
    Form.Field("Name").value = sCustName & GetName() & " - " & Now
end sub

function GetName():
    dim fieldNames
    fieldNames = Array("Type", "Make", "Model", "Serial Number", "Identifying Marks")

    dim sName, fieldNamey
    sName = ""
    For Each fieldNamey In fieldNames
        sName = sName & MaybeStr(fieldNamey)
    Next
    GetName = sName
End Function



function MaybeStr(fieldName)
    if Form.Field(fieldName).Value = "" Then
        MaybeStr = ""
    else
        MaybeStr = " - " & Form.Field(fieldName).Value
    end if
end function