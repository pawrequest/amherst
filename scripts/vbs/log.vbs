$OBJECT=Form

Option Explicit

' Base VBscript template for Commence detail forms.
' See your Commence documentation for more information about scripting.

Sub Form_OnClick(ControlId)
    Select Case ControlId
        Case "CommandButton1"
            Form.Field("Name").Value = "Got Auto Quote"
            
        Case "CommandButton2"
            Form.Field("Name").Value = "Called to book in hire"
        Case "CommandButton3"
            Form.Field("Name").Value = "Called for prices"
        Case "CommandButton4"
            Form.Field("Name").Value = "Sent followup email"
        Case "CommandButton5"
            Form.Field("Name").Value = "Emailed invoice to them"
            
	Case "CommandButton6"
            Form.Field("Name").Value = "Emailed to book in hire"
            
	Case "CommandButton7"
            Form.Field("Name").Value = "Called to pay on card"
	Case "CommandButton8"
            Form.Field("Name").Value = "Emailed for prices"
            
	Case "CommandButton9"
            Form.Field("Name").Value = "Emailed re overdue return"
            
	Case "CommandButton10"
            Form.Field("Name").Value = "Called re overdue return"
	Case "CommandButton11"
            Form.Field("Name").Value = "Got Auto Quote Booking Request"
            
	Case "CommandButton12"
            Form.Field("Name").Value = "Got Auto Quote Calculate"
            
	Case "CommandButton13"
            Form.Field("Name").Value = "Emailed to arrange return"
            
	Case "CommandButton14"
            Form.Field("Name").Value = "Requested radio trial"
            
	Case "CommandButton15"
            Form.Field("Name").Value = "Got Try Before You Buy Form"
            
	Case "CommandButton16"
            Form.Field("Staff").Value = "GT"
    Case "CommandButton17"
            Form.Field("Staff").Value = "CJ"
    Case "CommandButton21"
            Form.Field("Staff").Value = "PR"
    Case "CommandButton19"
            Form.Field("Name").Value = "Called and left voicemail"
	Case "CommandButton20"
			Form.Field("Name").Value = "Emailed re missing kit"	
			
    Case "CommandButton18"
			Form.Field("Staff").Value = "GT"
			
			' call function to tidy up any file path entered to show the correct R: drive letter rather than "D:\amherst"
			If Form.Field("Document").Value <> "" Then
				Form.Field("Document").Value = InvoicePath(Form.Field("Document").Value)
			End If
			
            Form.Save
    Case "CommandButton22"
			Form.Field("Staff").Value = "CJ"
			
			' call function to tidy up any file path entered to show the correct R: drive letter rather than "D:\amherst"
			If Form.Field("Document").Value <> "" Then
				Form.Field("Document").Value = InvoicePath(Form.Field("Document").Value)
			End If
            
			Form.Save
    Case "CommandButton23"
			Form.Field("Staff").Value = "PR"
			
			' call function to tidy up any file path entered to show the correct R: drive letter rather than "D:\amherst"
			If Form.Field("Document").Value <> "" Then
				Form.Field("Document").Value = InvoicePath(Form.Field("Document").Value)
			End If
			
			
            Form.Save
			
	End Select
End Sub


Sub Form_OnLoad()
End Sub

Sub Form_OnSave()

	' call function to tidy up any file path entered to show the correct R: drive letter rather than "D:\amherst"
	If Form.Field("Document").Value <> "" Then
		Form.Field("Document").Value = InvoicePath(Form.Field("Document").Value)
	End If

' added Sep 5th 2021 to check staff initials filled in, will replace the "mandatory field" setting, because this method
' works more quickly in giving the user the warning message
	'Prevent saving if the staff name is blank
    If Form.Field("Staff").Value = "" Then
       MsgBox "You cannot leave the staff initials box empty!", vbCritical, "WARNING"
        Form.MoveToField("Staff")
        Form.Abort
        Exit Sub
    End If


End Sub

Sub Form_OnCancel()
End Sub

Sub Form_OnEnterTab(ByVal TabName)
End Sub

Sub Form_OnLeaveTab(ByVal TabName)
End Sub

Sub Form_OnEnterField(ByVal FieldName)
End Sub

Sub Form_OnLeaveField(ByVal FieldName)
End Sub

Sub Form_OnActiveXControlEvent(ByVal ControlName, ByVal EventName, ByVal ParameterArray)
End Sub

' start of functions

' function to correct file paths to our invoices
Function InvoicePath(Filepath)
	
	' change incoming path to UPPER CASE
	Filepath = Ucase(Filepath)
	
	' now set the returned value to the incoming file path, so we simply send back the incoming path unless it needs changing
	InvoicePath = Filepath
		
	' check if path is drive D: and change to R: if it is
	If Left(Filepath, 10) = "D:\AMHERST" Then

		InvoicePath = Ucase("R:" + Mid(Filepath, 11))

	End If
	
	' check if path is a \\ network drive path and change to R:\ if it is
	If Left(Filepath, 21) = "\\AMHERSTMAIN\AMHERST" Then

		InvoicePath = Ucase("R:" + Mid(Filepath, 22))

	End If


End Function
