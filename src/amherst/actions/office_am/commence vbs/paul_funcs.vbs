'****** PR_FUNCS ***********
Sub PackHire()
    Dim packedBy
    packedBy = InputBox("Who packed this hire?", "Hire Packed by?")
    if packedBy = "" Then
        Exit Sub
    End if
    ' offer to email client about upcoming shipment'
    if MsgBox("Send pre-shipping email?", 4) = 6 Then
        EmailSendOut()
    End if

    ' offer to save and close'
    if MsgBox("Hire packed now by " & packedBy & " - save and close form?", 4) = 6 Then
        Form.Field("Packed Date").Value = "today"
        Form.Field("Packed Time").Value = "now"
        Form.Field("Status").Value = "Booked in and packed"
        Form.Field("Packed By").Value = packedBy
        Form.Save
    End if
End Sub

Sub MaybeReturnedToday()
    if Form.Field("Actual Return Date").Value = "" Then
        Form.Field("Actual Return Date").Value = "today"
    End if
End Sub


Sub ReturnedOkNow(unpackedBy)
    Form.Field("Status").Value = "Returned all OK"
    Form.Field("Unpacked Date").Value = "today"
    Form.Field("Unpacked Time").Value = "now"
    Form.Field("Unpacked By").Value = unpackedBy
    Form.Field("Closed").Value = 1
    MaybeReturnedToday()
End Sub


Sub RetunedWithProblemsNow(unpackedBy)
    Form.Field("Status").Value = "Returned with problems"
    Form.Field("Unpacked By").Value = unpackedBy
    Form.Field("Unpacked Date").Value = "today"
    Form.Field("Unpacked Time").Value = "now"
    MaybeReturnedToday()
End Sub

Sub UnpackHire()
    Dim unpackedBy, missing
    unpackedBy = InputBox("Who unpacked this hire?", "Hire Unpacked by?")
    if unpackedBy = "" Then
        Exit Sub
    End if

    missing = Form.Field("Missing Kit").value
    if missing = "" Then
        if MsgBox("all ok? - Close Hire, save, and exit form?", 4) = 6 Then
            ReturnedOkNow(unpackedBy)
            Form.Save
            Exit Sub
        End if
    End if

    if MsgBox("Use missing kit field?" & vbNewLine & missing, 4) <> 6 Then
        missing = InputBox("What was missing? (replace form data)", "What's Missing?")
        if missing <> "" Then
            Form.Field("Missing Kit").Value = missing
        End if
    End if

    if missing <> "" Then
        EmailMissingKit()
        if MsgBox("Set status to returned with problems, save, and exit?", 4) = 6 Then
            RetunedWithProblemsNow(unpackedBy)
            Form.Save
        End if
    End if
End Sub


Sub EmailSendOut()
'emails customer conforming address and schedule and gear'
    Dim olApp : Set olApp = CreateObject("Outlook.Application")
    Dim objMailItem : Set objMailItem = olApp.CreateItem(0)
    Dim cCust : Set cCust = Form.Connection("To", "Customer")
    Dim returnStr, del_email, sendMeth, invoice_email

    'tbc include parcelforce tracking numbers in email'
    '         MsgBox Form.Field("Tracking Numbers").value

    '*** create email ***'
    '* if invoice and delivery emails are differnt then combine into a string
    invoice_email = cCust.FieldValue("Email")
    del_email = Form.Field("Delivery Email").Value
    if invoice_email <> del_email Then
        del_email = del_email & ";" & invoice_email
    End if

    ' get send method from horrible strings
    If InStr(Form.Field("Send Or Collect").Value, "Cust. collect") > 0 OR InStr(Form.Field("Send Or Collect").Value, "We pick up only") > 0 Then
        sendMeth = "collected by yourself or at your expense "
    Else sendMeth = "sent out "
    End If

    ' get return method from horrible strings'
    if Form.Field("Send Or Collect").Value = "We send only" Or Form.Field("Send Or Collect").Value = "Cust. collect/return" Then
        returnStr = "Our records indicate you have not pre-paid for return shipping and are required to send the gear back at your expense." & vbNewLine & _
            vbNewLine & "Please use a trackable service and send us the tracking details when you have dispatched the shipment."

    Elseif Form.Field("Send Or Collect").Value = "We send and pick up" Or Form.Field("Send Or Collect").Value = "We pick up only" Then
        returnStr = "Our records indicate that you have paid for return shipping - please contact us two days before the equipment will be ready to collect so that we can arrange the courier."
    End if

    ' compose email'
    objMailItem.Subject = "Radio Hire - upcoming shipment details"
    objMailItem.To = del_email
    objMailItem.Body = "Hi," & vbNewLine & _
                           vbNewLine & "Thanks for choosing to hire from Amherst." & vbNewLine & vbNewLine & "Your upcoming hire is due to be " & sendMeth & "on " & Form.Field("Send Out Date").Value & vbNewLine & vbNewLine & _
                           "Please check the following details and contact us urgently if there are any discrepancies." & vbNewLine & _
                           vbNewLine & "Delivery To:" & vbNewLine & vbNewLine & _
                           Form.Field("Delivery Contact").Value & vbNewLine & _
                           Form.Field("Delivery Name").Value & vbNewLine & _
                           Form.Field("Delivery Address").Value & vbNewLine & _
                           Form.Field("Delivery Postcode").Value & vbNewLine & _
                           vbNewLine & "Hire Contents:" & Form.Field("Hire Sheet Text").Value & vbNewLine & _
                           vbNewLine & "Your Hire is due back with us by the " & Form.Field("Due Back Date").Value & vbNewLine & _
                           vbNewLine & returnStr & vbNewLine & _
                           vbNewLine & "Kind regards" & vbNewLine & "The Amherst team" & vbNewLine & vbNewLine & "(this email generated automatically)"

    '* Get user inputs*'
    'confirm/amend email address or cancel'
    Dim email_or_change
    email_or_change = MsgBox("Send email to: " & del_email & "?" & vbNewLine & _
    "'No' to enter an alternative, 'Cancel' to abort emailing", 3)
    if email_or_change = 7 Then
        del_email = InputBox("Enter new email address")
    Elseif email_or_change = 2 Then
        Exit Sub
    End if

    ' show user the email and get confirmation to send email'
    objMailItem.Send
    Form.Field("PreShip Emailed").Value = True

    ' close objects'
    Set olApp = Nothing
    Set objMailItem = Nothing

End Sub

Sub EmailMissingKit()
' emails 'Missing Kit' field to invoice and delivery email addresse
    Dim cCust : Set cCust = Form.Connection("To", "Customer")
    Dim olApp : Set olApp = CreateObject("Outlook.Application")
    Dim objMailItem : Set objMailItem = olApp.CreateItem(0)
    Dim del_email, invoice_email

    ' make email address string if delivery and invoice emails are different send to both
    invoice_email = cCust.FieldValue("Email")
    del_email = Form.Field("Delivery Email").Value
    if invoice_email <> del_email Then
        del_email = del_email & ";" & invoice_email
    End if


    'compose email'
    objMailItem.Subject = "Radio Hire - Missing Kit"
    objMailItem.To = del_email
    objMailItem.Body = "Hi," & vbNewLine & _
                           vbNewLine & "Thanks for returning the hired equipment - I hope it worked well for your event." & vbNewLine & _
                           vbNewLine & "Unfortunately the return was missing the following items - can you please look/check with colleagues to see if they can be recovered - otherwise i'll draw up an invoice for replacement." & vbNewLine & _
                           "Kind regards," & vbNewLine & "the Amherst team" & vbNewLine & _
                           vbNewLine & "MISSING KIT:" & vbNewLine & _
                           Form.Field("Missing Kit").value & vbNewLine & vbNewLine & "(If you have already discussed missing items with us please disregard this automatically generated email)"

    ' show user the email and if confirmed send email'
    if MsgBox ("Confirm Email:" & vbNewLine & vbNewLine & objMailItem & vbNewLine & objMailItem.Body, 4) = 6 Then
        objMailItem.Send
        MsgBox("EMAILED")
    End if

    ' close objects'
    Set olApp = Nothing
    Set objMailItem = Nothing
    Set cCust = Nothing

End Sub
