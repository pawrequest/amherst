$OBJECT=Form

Option Explicit

Dim temp

' Base VBscript template for Commence detail forms.
' See your Commence documentation for more information about scripting.

' define a variable called "cCust" to hold the connection from hire record to customer
' this makes it easier to refer to several times later on
Dim cCust
Set cCust = Form.Connection("For","Customer")

Sub Form_OnLoad()
End Sub

Sub Form_OnSave()
End Sub


' code to respond to user clicking on the various command buttons on the screen
Sub Form_OnClick(ControlId)
    Select Case ControlId
        Case "CommandButton1"
	    ' generate a returns reference using the first few letters of customer name, plus the date
            'temp = Replace(Form.Field("Date opened").Value, "/", "")
			Form.Field("Our repair reference").Value = Replace(Ucase(Left(cCust.FieldValue("Name"),7)), " ", "") + Replace(Form.Field("Date opened").Value, "/", "")
			
	End Select		
End Sub