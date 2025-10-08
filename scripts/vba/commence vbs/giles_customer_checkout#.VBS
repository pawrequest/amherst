Option Explicit

Sub Form_OnSave()

    Dim tempweb, length, temp, atpos, m, dumpstring, addstring, temp_address

    On Error Resume Next

    ' trim any spaces off the company / "name" field
    Form.Field("Name").Value = Trim(Form.Field("Name").Value)

    ' added May 2022 - convert unusual apostrophes (ASCII codes 96, 145, 146) into the older 7-bit ASCII standard apostrophe (ASCII code 39) to avoid invoices printing funny - Giles
    ' do this for both the customer business name and the delivery address business name
    Form.Field("Name").Value = Replace(Form.Field("Name").Value, Chr(96), Chr(39))
    Form.Field("Name").Value = Replace(Form.Field("Name").Value, Chr(145), Chr(39))
    Form.Field("Name").Value = Replace(Form.Field("Name").Value, Chr(146), Chr(39))

    Form.Field("Deliv Name").Value = Replace(Form.Field("Deliv Name").Value, Chr(96), Chr(39))
    Form.Field("Deliv Name").Value = Replace(Form.Field("Deliv Name").Value, Chr(145), Chr(39))
    Form.Field("Deliv Name").Value = Replace(Form.Field("Deliv Name").Value, Chr(146), Chr(39))

    ' call function to format the email addresses correctly, trimming and removing angle brackets left in by cutting and pasting
    Form.Field("Email").Value = FormatEmail(Form.Field("Email").Value)
    Form.Field("Deliv Email").Value = FormatEmail(Form.Field("Deliv Email").Value)
    Form.Field("Accounts Email").Value = FormatEmail(Form.Field("Accounts Email").Value)

    ' call function to trim, initial capitalise and remove spurious characters from all personal names fields
    Form.Field("Contact Name").Value = FormatPersonName(Form.Field("Contact Name").Value)
    Form.Field("Deliv Contact").Value = FormatPersonName(Form.Field("Deliv Contact").Value)
    Form.Field("Accounts Contact").Value = FormatPersonName(Form.Field("Accounts Contact").Value)


    ' call function to format the UK postcode fields correctly in terms of the middle space
    Form.Field("Postcode").Value = FormatPostcode(Form.Field("Postcode").Value)
    Form.Field("Deliv Postcode").Value = FormatPostcode(Form.Field("Deliv Postcode").Value)

    'added April 11th 2019: copy the contents of the multi-line address field away to a variable called temp_address and then clear the field
    ' and copy the variable back into it - just doing this copy and copy back seems to remove the trailing blank lines
    ' then use REPLACE function to get rid of any double-spaced lines (i.e. blanks in between lines of text)
    temp_address = Form.Field("Address").Value
    temp_address = REPLACE(temp_address, vbCrLf & vbCrLf, vbCrLf)
    temp_address = REPLACE(temp_address, vbCrLf & vbCrLf, vbCrLf)
    Form.Field("Address").Value = temp_address

    ' now do the same for the delivery address
    temp_address = Form.Field("Deliv Address").Value
    temp_address = REPLACE(temp_address, vbCrLf & vbCrLf, vbCrLf)
    temp_address = REPLACE(temp_address, vbCrLf & vbCrLf, vbCrLf)
    Form.Field("Deliv Address").Value = temp_address

    ' if there is nothing entered in the delivery name, address etc fields, copy the values from the main name and address fields
    If Form.Field("Deliv Name").Value = "" Then
        Form.Field("Deliv Name").Value = Form.Field("Name").Value
    End If

    If Form.Field("Deliv Contact").Value = "" Then
        Form.Field("Deliv Contact").Value = Form.Field("Contact Name").Value
    End If

    If Form.Field("Deliv Address").Value = "" Then
        Form.Field("Deliv Address").Value = Form.Field("Address").Value
    End If

    If Form.Field("Deliv Postcode").Value = "" Then
        Form.Field("Deliv Postcode").Value = Form.Field("Postcode").Value
    End If

    If Form.Field("Deliv Telephone").Value = "" Then
        Form.Field("Deliv Telephone").Value = Form.Field("Telephone").Value
    End If

    If Form.Field("Deliv Email").Value = "" Then
        Form.Field("Deliv Email").Value = Form.Field("Email").Value
    End If

    ' call function to format the UK postcode correctly in terms of the middle space for delivery postcode field
    Form.Field("Deliv Postcode").Value = FormatPostcode(Form.Field("Deliv Postcode").Value)

    ' call general phone number formatting function for all telephone number fields
    Form.Field("Telephone").Value = FormatTelNumber(Form.Field("Telephone").Value)
    Form.Field("Fax").Value = FormatTelNumber(Form.Field("Fax").Value)
    Form.Field("Deliv Telephone").Value = FormatTelNumber(Form.Field("Deliv Telephone").Value)
    Form.Field("Mobile Phone").Value = FormatTelNumber(Form.Field("Mobile Phone").Value)
    Form.Field("Accounts Telephone").Value = FormatTelNumber(Form.Field("Accounts Telephone").Value)
    Form.Field("Main Telephone").Value = FormatTelNumber(Form.Field("Main Telephone").Value)

    ' if there is nothing in the main "Telephone" field, but there is a number in the "Mobile Phone" field, copy mobile to main phone number field
    If Form.Field("Telephone").Value = "" Then
        If Form.Field("Mobile Phone").Value <> "" Then
            Form.Field("Telephone").Value = Form.Field("Mobile Phone").Value
        End If
    End If

    ' if there is an "07" UK mobile number in the main "Telephone" field, but nothing in the "Mobile Phone" field, copy main phone number field to mobile number
    If Left(Form.Field("Telephone").Value, 2) = "07" Then

        If Form.Field("Mobile Phone").Value = "" Then
            Form.Field("Mobile Phone").Value = Form.Field("Telephone").Value
        End If
    End If

    ' if there is text in the "Name" field but nothing in "Contact Name" then copy Name to Contact Name
    If Form.Field("Name").Value <> "" Then

        If Form.Field("Contact Name").Value = "" Then
            Form.Field("Contact Name").Value = Form.Field("Name").Value
        End If

    End If

    ' if there is text in the "Contact Name" field but nothing in "Name" then copy Contact Name to Name
    If Form.Field("Contact Name").Value <> "" Then

        If Form.Field("Name").Value = "" Then
            Form.Field("Name").Value = Form.Field("Contact Name").Value
        End If

        ' added May 2022 - added a new field called "Name For Printing" which will hold either the same as the "business name" (Name) field if this is different to the personal contact name (Contact Name)
        ' or nothing if these two fields are identical. The purpose of this is to suppress the printing of two identical names for individual customers on invoices and letters etc
        If Form.Field("Name").Value <> Form.Field("Contact Name").Value Then
            Form.Field("Name For Printing").Value = Form.Field("Name").Value
        Else
            Form.Field("Name For Printing").Value = ""
        End If

    End If

    'May 2014: if there is content in "charity number" field, set the charity tick box to true
    If Form.Field("Charity Number").Value <> "" Then
        Form.Field("Charity?").Value = 1
    End If

    ' May 2014: if the charity tick box is set, insert charity discount and description
    If Form.Field("Charity?").Value = 1 Then
        Form.Field("Discount Description").Value = "Charity Discount"
        Form.Field("Discount Percentage").Value = "25%"

    End If

    ' April 2016: if the student tick box is set, insert student discount and description
    If Form.Field("Student Discount?").Value = 1 Then
        Form.Field("Discount Description").Value = "Student Discount"
        Form.Field("Discount Percentage").Value = "25%"

    End If


    'insert a web site from the email address if there isn't already one there
    If Form.Field("Web Site").Value = "" Then

        length = Len(Form.Field("Email").Value)
        atpos = Instr(Form.Field("Email").Value, "@")
        tempweb = Right(Form.Field("Email").Value, (length - atpos))

        ' insert some well-known exceptions here to filter out hotmail, gmail, yahoo etc, so we don't insert "www.hotmail.com" as the company web site
        If Instr(tempweb, "hotmail") + Instr(tempweb, "gmail") + Instr(tempweb, "yahoo") + Instr(tempweb, "googlemail") + Instr(tempweb, "mac") = 0 Then

        ' replace the web site field with the domain part of the email address, prefixed with "www." if there is something to add
            If tempweb <> "" Then
                Form.Field("Web Site").Value = "www." + tempweb
            End If
        End If
    End If

    ' code to auto-update "number of hires" field depending on how many hire records are connected to the customer
    Form.Field("Number of Hires").Value = Form.Connection("Has Hired", "Hire").ConnectedItemCount

    ' added May 2019 - calculate number of linked "Log" contact records linked to the customer
    Form.Field("Number of contacts").Value = Form.Connection("Has", "Log").ConnectedItemCount

    'combine the contact name, company name, address and postcode into the "All Address" field
    addstring = Form.Field("Contact Name").Value + vbCrLf + Form.Field("Name For Printing").Value + vbCrLf + Form.Field("Address").Value + vbCrLf + Form.Field("Postcode").Value
    Form.Field("All Address").Value = addstring

    ' added May 2019: prevent saving of incomplete customer records

    'Prevent saving a customer with no phone number
    If Form.Field("Telephone").Value = "" Then
        MsgBox "You cannot save a customer record with no telephone number", vbCritical, "WARNING"
        Form.MoveToField("Telephone")
        Form.Abort
        Exit Sub
    End If

    'Prevent saving a customer with nonsense email (no @)
    'If Not Instr(Form.Field("Email").Value,"@") Then
    '   MsgBox "The email address is not correct - must contain a '@'", vbCritical, "WARNING"
    '   Form.MoveToField("Email")
    '    Form.Abort
    '    Exit Sub
    'End If

    'Prevent saving a customer with no log items connected
    If Form.Field("Number of contacts").Value = 0 Then
        MsgBox "You cannot save a customer record with no log items at all!", vbCritical, "WARNING"
        Form.Abort
        Exit Sub
    End If

    'prevent saving a customer with no category boxes ticked
    If Form.Field("Hire Customer").Value = 0 And Form.Field("Sales Customer").Value = 0 And Form.Field("Hire Prospect").Value = 0 And Form.Field("Sales Prospect").Value = 0 And Form.Field("Supplier / Other").Value = 0 And Form.Field("Closed prospect").Value = 0 Then
        MsgBox "You cannot save a customer record with no category box ticked", vbCritical, "WARNING"
        Form.Abort
        Exit Sub
    End If


End Sub

' code to respond to user clicking on the various command buttons on the screen

Sub Form_OnClick(ControlId)
    Select Case ControlId
        Case "CommandButton1"
        ' update the last contacted date to today's date - button deleted April 2019 because this field is updated automatically
            Form.Field("Date Last Contact").Value = "today"
        Case "CommandButton2"
        ' change the contents of the "Name" field to initial capitals, rest lower-case
            Form.Field("Name").Value = PCase(Form.Field("Name").Value, "")
        Case "CommandButton3"
        ' change the contents of the "Contact Name" field to initial capitals, rest lower-case
            Form.Field("Contact Name").Value = PCase(Form.Field("Contact Name").Value, "")
        Case "CommandButton4"
        ' strip out any intermediate blank lines in address field
        ' change the contents of the "Address" field to initial capitals, rest lower-case, unless its all CAPS
        ' this only seems to work on first line of text as of April 2019
            DIM temp_address
            temp_address = Form.Field("Address").Value
            temp_address = PCase(temp_address, "A")
            Form.Field("Address").Value = temp_address

        Case "CommandButton6"
        ' Copy the main address, postcode, contact details into the "delivery" ones
            Form.Field("Deliv Name").Value = Form.Field("Name").Value
            Form.Field("Deliv Contact").Value = Form.Field("Contact Name").Value
            Form.Field("Deliv Address").Value = Form.Field("Address").Value
            Form.Field("Deliv Postcode").Value = Form.Field("Postcode").Value
            Form.Field("Deliv Telephone").Value = Form.Field("Telephone").Value
            Form.Field("Deliv Email").Value = Form.Field("Email").Value

        Case "CommandButton7"
        ' if there is an email address in the "contact name" field enclosed in angle brackets, strip it out and put
        ' it into the email field leaving just the actual name in the contact name field
        ' only do anything if there is an @ in the string in the first place
            If Instr(Form.Field("Contact Name").Value, "<") Then
                length = Len(Form.Field("Contact Name").Value)
                atpos = Instr(Form.Field("Contact Name").Value, "<")
                Form.Field("Email").Value = Right(Form.Field("Contact Name").Value, (length - atpos))
                Form.Field("Contact Name").Value = Left(Form.Field("Contact Name").Value, atpos)
            End If

        Case "CommandButton8"
        ' Change the contents of the "Name" field to all UPPER CASE
            Form.Field("Name").Value = Ucase(Form.Field("Name").Value)

        Case "CommandButton5"
        ' process the text copied in from an "AutoQuote" email
            Dim tempweb, length, temp, atpos, m, dumpstring, addstring

            ' only do any of this if the "Dump" field contains text to analyse and split out
            If Form.Field("Dump").Value <> "" Then

            ' copy the "dump" field into a memory variable
                dumpstring = Form.Field("Dump").Value
                'Msgbox(dumpstring)

                ' split the fields found in the AutoQuote text into the appropriate database fields
                Form.Field("AQ Ref Number").Value = FindFieldInString(dumpstring, "Quotation Reference:")
                Form.Field("Contact Name").Value = PCase(FindFieldInString(dumpstring, "Name:"), "")
                Form.Field("Name").Value = PCase(FindFieldInString(dumpstring, "Organisation:"), "A")
                Form.Field("Telephone").Value = FindFieldInString(dumpstring, "Phone:")
                Form.Field("Fax").Value = FindFieldInString(dumpstring, "Fax:")
                Form.Field("Email").Value = FindFieldInString(dumpstring, "Email:")
                Form.Field("Charity Number").Value = FindFieldInString(dumpstring, "Registered Charity:")
                Form.Field("First Hire Date").Value = FindFieldInString(dumpstring, "Start Date:")

                ' if a charity number is entered, set the charity flag to True
                If Form.Field("Charity Number").Value <> "" Then
                    Form.Field("Charity?").Value = 1
                End If


                ' if the "Name" (organisation) field is blank, then substitute the "Contact Name" field - this works for
                ' customers who are private individuals and do not specify any "organisation"
                If Form.Field("Name").Value = "" Then
                    Form.Field("Name").Value = Form.Field("Contact Name").Value
                End If

                ' if we have a value in the "Name" field by this point, then we are dealing with an autoquote, so
                ' set the "Hire Prospect" check box field to "True"
                If Form.Field("Name").Value <> "" Then
                    Form.Field("Hire Prospect").Value = 1
                End If

                ' read in the address and postcode fields
                Form.Field("Address").Value = Pcase(FindFieldInString(dumpstring, "Address:"), "A")
                Form.Field("Postcode").Value = FindFieldInString(dumpstring, "Postcode:")

                ' split the address into lines based on commas at the end of each line - added by Giles April 2016
                Form.Field("Address").Value = Replace(Form.Field("Address").Value, ", ", vbCrLf)

                ' read in notes fields
                Form.Field("Notes").Value = FindFieldInString(dumpstring, "Purpose of hire:") + vbLf + FindFieldInString(dumpstring, "Additional notes:")

                ' read in and format the delivery name, address, phone number etc
                Form.Field("Deliv Name").Value = PCase(FindFieldInString(dumpstring, "Delivery Organisation:"), "A")
                Form.Field("Deliv Contact").Value = PCase(FindFieldInString(dumpstring, "Delivery Name:"), "")
                Form.Field("Deliv Address").Value = Pcase(FindFieldInString(dumpstring, "Delivery Address:"), "A")

                ' split the delivery address into lines based on commas at the end of each line - added by Giles April 2016
                Form.Field("Deliv Address").Value = Replace(Form.Field("Deliv Address").Value, ", ", vbCrLf)

                Form.Field("Deliv Telephone").Value = FindFieldInString(dumpstring, "Delivery Phone")
                Form.Field("Deliv Postcode").Value = FindFieldInString(dumpstring, "Delivery Postcode:")

                ' code to copy quantities of items hired into new fields in customer record
                ' added by Giles 19th October 2013

                ' first, zero all the fields so we don't have leftover values from previous quotes
                Form.Field("Number UHF").Value = 0
                Form.Field("Number Batteries").Value = 0
                Form.Field("Number Cases").Value = 0
                Form.Field("Number EM").Value = 0
                Form.Field("Number EMC").Value = 0
                Form.Field("Number Headset").Value = 0
                Form.Field("Number Headset Big").Value = 0
                Form.Field("Number Icom").Value = 0
                Form.Field("Number Megaphone").Value = 0
                Form.Field("Number Parrot").Value = 0

                ' for each item that can be hired, first locate the line of text containing the quantity and price etc for each item of equipment

                ' the quantity is the first "word" in the string, so we use string functions to take it off and insert
                ' into the appropriate field

                temp = FindFieldInString(dumpstring, "Standard UHF walkie-talkie")
                Form.Field("Number UHF").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "Spare battery")
                Form.Field("Number Batteries").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "Leather case with neck strap")
                Form.Field("Number Cases").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "Standard D-type earpiece/mic")
                Form.Field("Number EM").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "Semi-covert (curly tube) in-ear earpiece/mic")
                Form.Field("Number EMC").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "Headset with boom microphone")
                Form.Field("Number Headset").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "Big headset (noise cancelling)")
                Form.Field("Number Headset Big").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "Vehicle or base station radio")
                Form.Field("Number Icom").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "25 watt megaphone")
                Form.Field("Number Megaphone").Value = Left(temp, Instr(temp, " "))

                temp = FindFieldInString(dumpstring, "Lapel speaker / microphone")
                Form.Field("Number Parrot").Value = Left(temp, Instr(temp, " "))


                ' summarise the order - date and basic quantities of kit hired
                Form.Field("First Hire Date").Value = FindFieldInString(dumpstring, "Start Date:")

                temp = Cstr(Form.Field("Number UHF").Value) + " radios "
                Form.Field("First Hire Details").Value = temp + "for " + FindFieldInString(dumpstring, "Hire Length:")

                ' this last bit is to deal with the "try before you buy" form emails or Sellerdeck orders
                If Form.Field("Contact Name").Value = "" Then
                    Form.Field("Contact Name").Value = PCase(FindFieldInString(dumpstring, "Name"), "")
                End If

                ' this is for Try Before You Buy
                If Form.Field("Name").Value = "" Then
                    Form.Field("Name").Value = PCase(FindFieldInString(dumpstring, "Company/Organisation"), "A")
                End If

                ' this is for Sellerdeck data
                If Form.Field("Name").Value = "" Then
                    Form.Field("Name").Value = PCase(FindFieldInString(dumpstring, "Organisation"), "A")
                End If

                ' this is for Try Before You Buy
                If Form.Field("Address").Value = "" Then
                    Form.Field("Address").Value = Pcase(FindFieldInString(dumpstring, "Address1"), "A")
                    Form.Field("Address").Value = Form.Field("Address").Value + vbcrlf + Pcase(FindFieldInString(dumpstring, "Address2"), "A")
                    Form.Field("Address").Value = Form.Field("Address").Value + vbcrlf + Pcase(FindFieldInString(dumpstring, "Town/City"), "A")
                    ' set the "Sales Prospect" check box field to "True"
                    Form.Field("Sales Prospect").Value = 1
                End If

                ' this for Sellerdeck
                If Form.Field("Address").Value = "" Then
                    Form.Field("Address").Value = Pcase(FindFieldInString(dumpstring, "Address"), "A")
                    ' set the "Sales Customer" check box field to "True"
                    Form.Field("Sales Customer").Value = 1
                End If

                ' this is for Try Before You Buy
                If Form.Field("Postcode").Value = "" Then
                    Form.Field("Postcode").Value = FindFieldInString(dumpstring, "Postcode")
                End If

                ' this for Sellerdeck
                If Form.Field("Postcode").Value = "" Then
                    Form.Field("Postcode").Value = FindFieldInString(dumpstring, "Post Code")
                End If

                ' this is for Try Before You Buy
                If Form.Field("Telephone").Value = "" Then
                    Form.Field("Telephone").Value = FindFieldInString(dumpstring, "Telephone")
                End If

                ' this for Sellerdeck
                If Form.Field("Telephone").Value = "" Then
                    Form.Field("Telephone").Value = FindFieldInString(dumpstring, "Phone")
                End If

                ' this is for Try Before You Buy
                If Form.Field("Email").Value = "" Then
                    Form.Field("Email").Value = FindFieldInString(dumpstring, "Email")
                End If

                ' this for Sellerdeck
                If Form.Field("Email").Value = "" Then
                    Form.Field("Email").Value = FindFieldInString(dumpstring, "email")
                End If

                ' this for Sellerdeck - delivery contact name
                If Form.Field("Deliv Contact").Value = "" Then
                    Form.Field("Deliv Contact").Value = PCase(FindFieldInString(dumpstring, "Delivery Name"), "A")
                End If

                ' this for Sellerdeck - delivery company/organisation
                If Form.Field("Deliv Name").Value = "" Then
                    Form.Field("Deliv Name").Value = PCase(FindFieldInString(dumpstring, "Delivery Organisation"), "A")
                End If

                ' this for Sellerdeck - delivery address
                If Form.Field("Deliv Address").Value = "" Then
                    Form.Field("Deliv Address").Value = PCase(FindFieldInString(dumpstring, "Delivery Address"), "A")
                End If

                ' this for Sellerdeck - delivery phone number
                If Form.Field("Deliv Telephone").Value = "" Then
                    Form.Field("Deliv Telephone").Value = PCase(FindFieldInString(dumpstring, "Delivery Phone"), "A")
                End If

                ' this for Sellerdeck - delivery postcode
                If Form.Field("Deliv Postcode").Value = "" Then
                    Form.Field("Deliv Postcode").Value = PCase(FindFieldInString(dumpstring, "Delivery Post Code"), "A")
                End If


                If Form.Field("Notes").Value = "" Then
                    Form.Field("Notes").Value = FindFieldInString(dumpstring, "Radio Type") + vbLf + FindFieldInString(dumpstring, "Comments") + vbLf + FindFieldInString(dumpstring, "Hear About")
                    Form.Field("First Hire Details").Value = ""
                End If

                ' finally blank the "dump" field so that user changes don't get overwritten next time the record is saved
                Form.Field("Dump").Value = ""

            End If
    End Select
End Sub


' ***** start of functions etc *****

' New Sep 2013 - general function to remove un-needed characters from telephone number fields and try to format the numbers correctly
' as UK phone numbers
' Jan 2014: added stuff to space an "x" for phone extensions properly

Function FormatTelNumber(Telnum)

    Dim xpos

    ' first, remove all dashes, brackets etc from phone number
    Telnum = Replace(Telnum, "-", "")
    Telnum = Replace(Telnum, "(", "")
    Telnum = Replace(Telnum, ")", "")
    Telnum = Replace(Telnum, ".", "")
    Telnum = Replace(Telnum, "/", "")
    Telnum = Replace(Telnum, ":", "")
    Telnum = Replace(Telnum, "<", "")
    Telnum = Replace(Telnum, ">", "")

    ' remove all spaces from the phone number
    Telnum = Replace(Telnum, " ", "")

    ' now we should have (usually) a string consisting only of numbers, maybe with a "+" at the start

    ' if the number starts "+44"  then remove it
    If Left(Telnum, 3) = "+44" Then
        Telnum = Mid(Telnum, 4)
    End If

    ' if the number starts "0044" then remove it
    If Left(Telnum, 4) = "0044" Then
        Telnum = Mid(Telnum, 5)
    End If

    ' if the number starts "44"  then remove it
    If Left(Telnum, 2) = "44" Then
        Telnum = Mid(Telnum, 3)
    End If

    ' if the number starts "7" add a leading "0"
    If Left(Telnum, 1) = "7" Then
        Telnum = "0" + Mid(Telnum, 1)
    End If

    ' if the number starts "1" add a leading "0"
    If Left(Telnum, 1) = "1" Then
        Telnum = "0" + Mid(Telnum, 1)
    End If

    ' if the number starts "2" add a leading "0"
    If Left(Telnum, 1) = "2" Then
        Telnum = "0" + Mid(Telnum, 1)
    End If

    ' from here on, we have to do a big If ... ElseIf statement to deal with specific types of number
    If Left(Telnum, 2) = "07" Then
    ' it is a UK mobile number, so insert a space after the fifth digit
        Telnum = Left(Telnum, 5) + " " + Mid(Telnum, 6)

    Elseif Left(Telnum, 2) = "02" Then
    ' format London and other "02" numbers correctly - 02x xxxx xxxx
        Telnum = Left(Telnum, 3) + " " + Mid(Telnum, 4, 4) + " " + Mid(Telnum, 8)

    Elseif Left(Telnum, 3) = "011" Then
    ' deal with the large town numbers like Sheffield 0114 etc - 011x xxx xxxx
        Telnum = Left(Telnum, 4) + " " + Mid(Telnum, 5, 3) + " " + Mid (Telnum, 8)

    Elseif Left(Telnum, 4) = "0845" Then
    ' deal with 0845 numbers
        Telnum = Left(Telnum, 4) + " " + Mid(Telnum, 5)

    Elseif Left(Telnum, 4) = "0844" Then
    ' deal with 0844 numbers
        Telnum = Left(Telnum, 4) + " " + Mid(Telnum, 5)

    Elseif Left(Telnum, 4) = "0800" Then
    ' deal with 0800 numbers
        Telnum = Left(Telnum, 4) + " " + Mid(Telnum, 5)

    Elseif Left(Telnum, 2) = "01" Then

    ' if the fourth character is a "1" then it must be one if the UK large city numbers, (like Edinburgh 0131 xxx xxxx) so format for this
        If Mid(Telnum, 4, 1) = "1" Then
            Telnum = Left(Telnum, 4) + " " + Mid(Telnum, 5, 3) + " " + Mid (Telnum, 8)

            ' if it looks like a general UK Landline, insert a space after what is usually the area code
        Elseif Len(Telnum) < 12 Then
            Telnum = Left(Telnum, 5) + " " + Mid(Telnum, 6)
        End If

    End If

    ' finally, if there is an "x" in the number string (to show "extension") then insert a space on either side of it
    xpos = Instr(Telnum, "x")
    If xpos <> 0 Then
        Telnum = Left(Telnum, xpos - 1) + " x " + Mid(Telnum, xpos + 1)
    End If

    ' return the formatted number
    FormatTelNumber = Telnum

End Function


' this function cleans up the formatting of any "persons name" field passed to it by removing spaces, wrong characters
' and then making each part of the person's name have a capital letter (added 9th April 2016)

Function FormatPersonName(Pname)

' first, trim the field to get rid of leading and trailing spaces
    Pname = Trim(Pname)

    ' remove all silly characters etc from the name
    Pname = Replace(Pname, "(", "")
    Pname = Replace(Pname, ")", "")
    Pname = Replace(Pname, ".", "")
    Pname = Replace(Pname, ",", "")
    Pname = Replace(Pname, "/", "")
    Pname = Replace(Pname, ":", "")
    Pname = Replace(Pname, "<", "")
    Pname = Replace(Pname, ">", "")
    ' remove speech marks
    Pname = Replace(Pname, Chr(34), "")

    ' added May 2022 replace any unusual apostrophes (ASCII code 95, 145, 146) with the standard 7 bit ASCII apostrophe (ASCII code 39) to avoid printing problems
    Pname = Replace(Pname, Chr(96), Chr(39))
    Pname = Replace(Pname, Chr(145), Chr(39))
    Pname = Replace(Pname, Chr(146), Chr(39))

    ' now use "Pcase" to make it initial capitals
    Pname = PCase(Pname, "")

    ' return the formatted person's name
    FormatPersonName = Pname

End Function

Function FormatEmail(Emailstring)

' first, trim the field to get rid of leading and trailing spaces
    Emailstring = Trim(Emailstring)

    ' get rid of any spaces
    Emailstring = Replace(Emailstring, " ", "")

    ' remove angle brackets
    Emailstring = Replace(Emailstring, "<", "")
    Emailstring = Replace(Emailstring, ">", "")

    ' remove speech marks
    Emailstring = Replace(Emailstring, Chr(34), "")

    ' remove spaces
    Emailstring = Replace(Emailstring, " ", "")

    ' remove double @
    Emailstring = Replace(Emailstring, "@@", "@")

    ' return the formatted email address
    FormatEmail = Emailstring

End Function


Function FormatPostcode(pcode)

' remove all silly characters etc from the postcode
    Pcode = Replace(Pcode, "(", "")
    Pcode = Replace(Pcode, ")", "")
    Pcode = Replace(Pcode, ".", "")
    Pcode = Replace(Pcode, "/", "")
    Pcode = Replace(Pcode, ":", "")
    Pcode = Replace(Pcode, "<", "")
    Pcode = Replace(Pcode, ">", "")

    'always capitalise postcode field
    FormatPostcode = Ucase(pcode)

    'FormatPostcode = Trim(FormatPostcode)
    FormatPostcode = Replace(FormatPostcode, " ", "")

    If Len(FormatPostcode) = 7 Then
        FormatPostcode = Left(FormatPostcode, 4) + " " + Mid(FormatPostcode, 5)
    End If

    If Len(FormatPostcode) = 6 Then
        FormatPostcode = Left(FormatPostcode, 3) + " " + Mid(FormatPostcode, 4)
    End If

    If Len(FormatPostcode) = 5 Then
        FormatPostcode = Left(FormatPostcode, 2) + " " + Mid(FormatPostcode, 3)
    End If

End Function


'Function to return string in proper case. The "Smode" parameter decides if ALL UPPER WORDS are allowed (mode "A" or Not (Mode Anything Else)

Function PCase(Str, Smode)
    Const Delimiters = " -,."
    Dim PStr, I, Char
    Str = Trim(Str)
    PStr = UCase(Left(Str, 1))
    For I = 2 To Len(Str)
        Char = Mid(Str, i - 1, 1)
        If InStr(Delimiters, Char) > 0 Then
            PStr = PStr & UCase(Mid(Str, i, 1))
        Else
        'If the function is in "A" (all upper) mode it allows words all upper case to stay that way, otherwise it makes Each Word Into Title Case
            If Smode = "A" Then
                PStr = PStr & Mid(Str, i, 1)
            Else
                PStr = PStr & LCase(Mid(Str, i, 1))
            End If
        End If
    Next
    PCase = PStr
End Function


' Rob's function to split a string containing several lines of text into an array (v) then search each array element 
' for a given string (the field name) and return the rightmost part of that line (the field contents)

Function FindFieldInString(dumpstring, field)
    Dim v
    Dim f
    v = Split(dumpstring, vbLf)
    For f = 0 To UBound(v)
        If Left(v(f), Len(field)) = field Then
            FindFieldInString = Trim(Right(v(f), Len(v(f)) - Len(field)))
            Exit Function
        End If
    Next
End Function 
 
