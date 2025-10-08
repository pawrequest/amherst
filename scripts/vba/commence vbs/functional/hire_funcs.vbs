'Giles_funcs.vbs
'###################
'first section paul's interpretations


Sub ClearStringField(fieldName)
    Form.Field(fieldName).value = ""
End Sub

Sub ClearNumberField(fieldName)
    Form.Field(fieldName).value = 0
End Sub

Sub ClearStringFields()
    For Each fieldname in Array("Inv UHF Desc", "Inv EM Desc", "Inv EMC Desc", "Inv Case Desc", "Inv Parrot Desc", "Inv Headset Desc", "Inv Bighead Desc", "Inv Batt Desc", "Inv Icom Desc", "Inv Mega Desc", "Inv UHF Price", "Inv EM Price", "Inv EMC Price", "Inv Case Price", "Inv Parrot Price", "Inv Headset Price", "Inv Bighead Price", "Inv Batt Price", "Inv Icom Price", "Inv Mega Price", "Inv UHF Qty", "Inv EM Qty", "Inv EMC Qty", "Inv Case Qty", "Inv Parrot Qty", "Inv Headset Qty", "Inv Bighead Qty", "Inv Batt Qty", "Inv Icom Qty", "Inv Mega Qty", "Inv Delivery Desc", "Inv Send Desc", "Inv Return Desc", "Inv Charger Desc", "Inv Purchase Order", "Inv Meg Batt Desc")
        ClearStringField(fieldname)
    Next
End Sub

Sub ClearNumberFields()
    For Each fieldname in Array()
        ClearNumberField(fieldname)
    Next
End Sub

Sub SetInstructions()
' uncheck the "instructions included" fields if there are none of each item on the order
    If Form.Field("Number VHF").Value = 0 Then
        If Form.Field("Number UHF").Value = 0 Then
            Form.Field("Instruc Walkies").Value = False
        End If
    End If

    If Form.Field("Number Icom").Value = 0 Then
        Form.Field("Instruc Icom").Value = False
    End If

    If Form.Field("Number Megaphone").Value = 0 Then
        Form.Field("Instruc Megaphone").Value = False
    End If

End Sub

sub TrimField(fieldName)
    Form.Field(fieldName).Value = Trim(Form.Field(fieldName).Value)
End Sub

sub TrailingAddressLines()
'added May 14th 2019: copy the contents of the multi-line delivery address field away to a variable called temp_address and then clear the field
' and copy the variable back into it - just doing this copy and copy back seems to remove the trailing blank lines
' then use REPLACE function to get rid of any double-spaced lines (i.e. blanks in between lines of text)
    temp_address = Form.Field("Delivery Address").Value
    temp_address = REPLACE(temp_address, vbCrLf & vbCrLf, vbCrLf)
    temp_address = REPLACE(temp_address, vbCrLf & vbCrLf, vbCrLf)
    Form.Field("Delivery Address").Value = temp_address
End Sub


Sub PreventBadSave()
' added Nov 2019
'Prevent saving if the ""Send Method"" is left blank
    If Form.Field("Send Method").Value = "" Then
        MsgBox "You cannot leave the Send Method field empty!", vbCritical, "WARNING"
        Form.MoveToField("Send Method")
        Form.Abort
        Exit Sub
    End If

    ' added 12th April 2019 warning error messages to prevent the hire record being saved with conflicting values in the hire status fields
    ' this is at the suggestion of Nigel Park as a neater way of checking and preventing these than the previous method using agents

    'Prevent saving a hire as "closed" when it has status "Booked In"
    If Form.Field("Closed").Value = 1 And Form.Field("Status").Value = "Booked in" Then
        MsgBox "You cannot close a hire that has a Status of 'Booked In' ", vbCritical, "WARNING"
        Form.MoveToField("Status")
        Form.Abort
        Exit Sub
    End If

    'Prevent saving a hire as "closed" when it has status "Booked In And Packed"
    If Form.Field("Closed").Value = 1 And Form.Field("Status").Value = "Booked in and packed" Then
        MsgBox "You cannot close a hire that has a Status of 'Booked In and packed' ", vbCritical, "WARNING"
        Form.MoveToField("Status")
        Form.Abort
        Exit Sub
    End If

    'Prevent saving a hire as "closed" when it has status "Out"
    If Form.Field("Closed").Value = 1 And Form.Field("Status").Value = "Out" Then
        MsgBox "You cannot close a hire that has a Status of 'Out' ", vbCritical, "WARNING"
        Form.MoveToField("Status")
        Form.Abort
        Exit Sub
    End If

    'Prevent saving a hire as "Returned" if the Actual Return Date field is not filled in
    If (Form.Field("Status").Value = "Returned all OK" Or Form.Field("Status").Value = "Returned with problems") And Form.Field("Actual Return Date").Value = "" Then
        MsgBox "You cannot mark a hire as 'returned' without entering the date that it was returned", vbCritical, "WARNING"
        Form.MoveToField("Actual Return Date")
        Form.Abort
        Exit Sub
    End If

    'Prevent saving a hire as "Booked in and packed" if the initials field for who packed it is empty
    If Form.Field("Status").Value = "Booked in and packed" And Form.Field("Packed By").Value = "" Then
        MsgBox "You cannot mark a hire as 'packed' without entering the initials for who packed it", vbCritical, "WARNING"
        Form.MoveToField("Packed By")
        Form.Abort
        Exit Sub
    End If

    'Prevent saving a hire as "Booked in and packed" if the packed date and time is empty
    If Form.Field("Status").Value = "Booked in and packed" And Form.Field("Packed Date").Value = "" Then
        MsgBox "You cannot mark a hire as 'packed' without entering the date and time that it was packed", vbCritical, "WARNING"
        Form.MoveToField("Packed By")
        Form.Abort
        Exit Sub
    End If

    'Prevent saving a hire if it involves a number of walkie-talkies, but the Radio Type field is blank (added Sep 5th 2021)
    If Form.Field("Radio Type").Value = "not selected" And Cint(Form.Field("Number UHF").Value) > 0 Then
        MsgBox "Please select the model of walkie-talkie for this hire", vbCritical, "WARNING"
        Form.MoveToField("Radio Type")
        Form.Abort
        Exit Sub
    End If
    'MsgBox Form.Field("Radio Type").Value, vbOKOnly, "WARNING"


End Sub


' #####################
' giles actual funcs

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
    ' deal with 084 numbers
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

    ' now use "Pcase" to make it initial capitals
    Pname = PCase(Pname, "")

    ' return the formatted person's name
    FormatPersonName = Pname

End Function

Function FormatEmail(Emailstring)

' first, trim the field to get rid of leading and trailing spaces
    Emailstring = Trim(Emailstring)

    ' remove angle brackets
    Emailstring = Replace(Emailstring, "<", "")
    Emailstring = Replace(Emailstring, ">", "")

    ' remove speech marks
    Emailstring = Replace(Emailstring, Chr(34), "")

    ' remove spaces
    Emailstring = Replace(Emailstring, " ", "")

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


' make sure due back date is not a weekend

Function NotWeekends(backdate)

' deal with Saturday (day 7 of week)
    If Weekday(backdate) = 7 Then
        backdate = DateAdd("d", 2, backdate)
    End If

    ' deal with Sunday (day 1 of week))
    If Weekday(backdate) = 1 Then
        backdate = DateAdd("d", 1, backdate)
    End If
    NotWeekends = backdate

End Function

Function MakeInvoiceDate(datefield)

    MakeInvoiceDate = WeekdayName(WeekDay(datefield), True) + " " + Cstr(Day(datefield)) + " " + MonthName(Month(datefield)) + " " + Cstr(Year(datefield))

End Function

' function to correct file paths to our invoices if they use drive D: or the network (\\) path instead of the R: shared path

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

Sub WarnBadSave()
    If Form.Field("Radio Type").Value = "Tesunho SIM TH288" Then
        MsgBox "TH288 no longer used - use TH388", vbOKOnly, "WARNING"
        Form.Field("Radio Type").Value = "Tesunho SIM TH388"
    End If

    If Form.Field("Radio Type").Value = "Tesunho SIM TH289" Then
        MsgBox "TH289 no longer used - use TH388", vbOKOnly, "WARNING"
        Form.Field("Radio Type").Value = "Tesunho SIM TH388"
    End If

    'Warn if the day of week of the send date is a weekend day
    If Weekday(Form.Field("Send Out Date").Value) = 1 Then
        MsgBox "The entered send/collect date is a Sunday ", vbOKOnly, "WARNING"
    End If

    If Weekday(Form.Field("Send Out Date").Value) = 7 Then
        MsgBox "The entered send/collect date is a Saturday ", vbOKOnly, "WARNING"
    End If

    'Warn if the day of week of the due back date is a weekend day
    If Weekday(Form.Field("Due Back Date").Value) = 1 Then
        MsgBox "The entered due back date is a Sunday ", vbOKOnly, "WARNING"
    End If

    If Weekday(Form.Field("Due Back Date").Value) = 7 Then
        MsgBox "The entered due back date is a Saturday ", vbOKOnly, "WARNING"
    End If

End Sub

Sub SetChargers()
    If Cint(Form.Field("Number UHF").Value) > 0 Then

    ' work out six slots and singles needed
        If Cint(Form.Field("Number UHF 6-way").Value) = 0 And Cint(Form.Field("Number Sgl Charger").Value) = 0 Then
        ' this backslash division sign calculates the integer part of the result - the number of 6-way chargers needed
            sixwaycharger = Form.Field("Number UHF").Value \ 6

            ' this works out the "remainder" - the number of single chargers needed
            singlecharger = Form.Field("Number UHF").Value Mod 6

            ' if there are going to be 4 or 5 single chargers, send another 6-way charger instead
            If singlecharger > 3 Then
                sixwaycharger = sixwaycharger + 1
                singlecharger = 0
            End If

            ' insert the calculated values into the fields
            Form.Field("Number UHF 6-way").Value = sixwaycharger
            Form.Field("Number Sgl Charger").Value = singlecharger

        End If

        ' if the radio type is a Tesunho, which doesn't have six slot chargers, we zero the number of six slots and set the number of singles same
        ' as the number of radios hired
        If Form.Field("Radio Type").Value > "Tesunho" Then
            Form.Field("Number Sgl Charger").Value = Form.Field("Number UHF").Value
            Form.Field("Number UHF 6-way").Value = 0
        End If
    End If
End Sub

Sub SetHireString()
    Dim hstring


End Sub

Sub SetPrices()

' Mar 2013: set price according to length of hire
    Select Case Form.Field("Weeks").Value
        Case 1
            Form.Field("Inv UHF Price").Value = "12.00"
        Case 2
            Form.Field("Inv UHF Price").Value = "18.00"
        Case 3
            Form.Field("Inv UHF Price").Value = "22.00"
        Case 4
            Form.Field("Inv UHF Price").Value = "27.00"
    End Select

    ' deal with discounts for bigger quantities
    If Form.Field("Number UHF").Value > 9 Then
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv UHF Price").Value = "12.00"
            Case 2
                Form.Field("Inv UHF Price").Value = "16.00"
            Case 3
                Form.Field("Inv UHF Price").Value = "21.00"
            Case 4
                Form.Field("Inv UHF Price").Value = "25.00"
        End Select

    End If

    If Form.Field("Number UHF").Value > 19 Then
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv UHF Price").Value = "10.00"
            Case 2
                Form.Field("Inv UHF Price").Value = "14.00"
            Case 3
                Form.Field("Inv UHF Price").Value = "19.00"
            Case 4
                Form.Field("Inv UHF Price").Value = "23.00"
        End Select

    End If

    If Form.Field("Number UHF").Value > 29 Then
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv UHF Price").Value = "8.00"
            Case 2
                Form.Field("Inv UHF Price").Value = "12.00"
            Case 3
                Form.Field("Inv UHF Price").Value = "18.00"
            Case 4
                Form.Field("Inv UHF Price").Value = "22.00"
        End Select

    End If
End Sub