Option Explicit
' define variables length and atpos for use in calculations
DIM length, atpos

ExecuteGlobal CreateObject("Scripting.FileSystemObject").OpenTextFile("C:\ProgramData\Commence\Commence\8.0\vbs\paul_funcs.vbs").ReadAll()
' import paul's functions:
'   - PackHire(packedBy)
'   - UnpackHire(unpackedBy)
'   - EmailSendOut()
'   - EmailMissingKit()
ExecuteGlobal CreateObject("Scripting.FileSystemObject").OpenTextFile("C:\ProgramData\Commence\Commence\8.0\vbs\giles_funcs.vbs").ReadAll()
' import giles's functions:
'   - FormatTelNumber(telNum)
'   - FormatPersonName(PersonName)
'   - FormatEmail(Emalstring)
'   - FormatPostcode(Postcode)
'   - PCase(str, mode)
'   - NotWeekends(date)
'   - MakeInvoiceDate(dateField)
'   - InvoicePath(Filepath)




Sub Form_OnSave
' stuff to do when the hire screen is saved
' this will consist of checking consistency - like querying if you have chosen "Returned all OK" and not checked "Closed" etc
' and importantly, using the quantities of each item entered to build up the texty "Hire Sheet Text" field that is displayed on the hire
' sheet document

' hstring holds the text description of the items hired in a hire record. It is built up piece by piece according to how many of
' each item has been hired. When complete, "hstring" is copied to the "Hire Sheet Text" field of the hire record
    Dim hstring

    hstring = ""

    ' these temporarily store the calculated required number of chargers
    Dim sixwaycharger
    Dim singlecharger

    sixwaycharger = 0
    singlecharger = 0

    ' this stores the delivery address field while it is tidied up
    Dim temp_address

    ' clear the invoice description text for each item
    Form.Field("Inv UHF Desc").Value = ""
    Form.Field("Inv EM Desc").Value = ""
    Form.Field("Inv EMC Desc").Value = ""
    Form.Field("Inv Case Desc").Value = ""
    Form.Field("Inv Parrot Desc").Value = ""
    Form.Field("Inv Headset Desc").Value = ""
    Form.Field("Inv Bighead Desc").Value = ""
    Form.Field("Inv Batt Desc").Value = ""
    Form.Field("Inv Icom Desc").Value = ""
    Form.Field("Inv Mega Desc").Value = ""

    ' clear the text unit price fields for each item
    Form.Field("Inv UHF Price").Value = ""
    Form.Field("Inv EM Price").Value = ""
    Form.Field("Inv EMC Price").Value = ""
    Form.Field("Inv Case Price").Value = ""
    Form.Field("Inv Parrot Price").Value = ""
    Form.Field("Inv Headset Price").Value = ""
    Form.Field("Inv Bighead Price").Value = ""
    Form.Field("Inv Batt Price").Value = ""
    Form.Field("Inv Icom Price").Value = ""
    Form.Field("Inv Mega Price").Value = ""

    ' clear the invoice quantity text for each item
    Form.Field("Inv UHF Qty").Value = ""
    Form.Field("Inv EM Qty").Value = ""
    Form.Field("Inv EMC Qty").Value = ""
    Form.Field("Inv Case Qty").Value = ""
    Form.Field("Inv Parrot Qty").Value = ""
    Form.Field("Inv Headset Qty").Value = ""
    Form.Field("Inv Bighead Qty").Value = ""
    Form.Field("Inv Batt Qty").Value = ""
    Form.Field("Inv Icom Qty").Value = ""
    Form.Field("Inv Mega Qty").Value = ""


    ' clear the delivery-related text fields
    Form.Field("Inv Delivery Desc").Value = " "
    Form.Field("Inv Send Desc").Value = " "
    Form.Field("Inv Return Desc").Value = " "

    ' clear the "radio chargers included" text field
    Form.Field("Inv Charger Desc").Value = " "

    ' clear the megaphone batteries description text field
    Form.Field("Inv Meg Batt Desc").Value = " "

    ' clear the invoice Purchase Order description text field
    Form.Field("Inv Purchase Order").Value = " "

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

    ' remove blank spaces around name and address fields etc
    Form.Field("Delivery Name").Value = Trim(Form.Field("Delivery Name").Value)

    ' format the delivery contact name correctly using the function
    Form.Field("Delivery Contact").Value = FormatPersonName(Form.Field("Delivery Contact").Value)

    ' format the delivery email correctly using the function
    Form.Field("Delivery Email").Value = FormatEmail(Form.Field("Delivery Email").Value)

    ' call function to format the UK postcode correctly in terms of the middle space
    Form.Field("Delivery Postcode").Value = FormatPostcode(Form.Field("Delivery Postcode").Value)

    ' call function to correctly format UK phone numbers
    Form.Field("Delivery Tel").Value = FormatTelNumber(Form.Field("Delivery Tel").Value)

    'added May 14th 2019: copy the contents of the multi-line delivery address field away to a variable called temp_address and then clear the field
    ' and copy the variable back into it - just doing this copy and copy back seems to remove the trailing blank lines
    ' then use REPLACE function to get rid of any double-spaced lines (i.e. blanks in between lines of text)
    temp_address = Form.Field("Delivery Address").Value
    temp_address = REPLACE(temp_address, vbCrLf & vbCrLf, vbCrLf)
    temp_address = REPLACE(temp_address, vbCrLf & vbCrLf, vbCrLf)
    Form.Field("Delivery Address").Value = temp_address

    ' if the "Send Method" is left blank on save, we can add some text if the Send/Collect flag value is appropriate
    If Form.Field("Send Method").Value = "" Then

        If Form.Field("Send Or Collect").Value = "Cust. collect/return" Then
            Form.Field("Send Method").Value = "Customer collects from us"
        End If

    End If

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


    'Prevent saving a hire as "Returned" if the Actual Return Date field is in the future
    'If Form.Field("Actual Return Date").Value <> "" And Form.Field("Actual Return Date").Value > Date Then
    '    MsgBox "You cannot enter an actual 'equipment returned date' that is in the future!", vbCritical, "WARNING"
    '    Form.MoveToField("Actual Return Date")
    '    Form.Abort
    '    Exit Sub
    'End If

    'Prevent saving a hire as "Returned" if the Due Back Date is earlier than the Send Out Date
    ' commented out 12th April because it seemed to be triggered sometimes even when dates were OK
    'If Form.Field("Due Back Date").Value < Form.Field("Send Out Date").Value Then
    '   MsgBox "You cannot enter a Due Back Date that is BEFORE the Send Out Date!", vbCritical, "WARNING"
    '    Form.MoveToField("Send Out Date")
    '    Form.Abort
    '    Exit Sub
    'End If

    'Prevent saving a hire if the "Send Out Date" is in the past
    'If Form.Field("Send Out Date").Value < Date Then
    '    MsgBox "You cannot enter a 'Send Out Date' that is in the past!", vbCritical, "WARNING"
    '    Form.MoveToField("Send Out Date")
    '    Form.Abort
    '    Exit Sub
    'End If	

    ' the fields referring to "UHF" now refer to whatever type of walkie-talkie is being hired
    ' if the user hasn't entered any quantities into the "charger" fields, calculate the appropriate numbers of charger units needed
    ' for "normal" walkie-talkies, this involves working out how many six slot and how many single chargers to send
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


    ' make up the standard item text description and price fields


    If Cint(Form.Field("Number UHF").Value) > 0 Then

    ' insert description of radios used - as of Sep 2015 use the new "Radio Type" field for the description
        hstring = hstring + vbCrLf + "* " + Form.Field("Number UHF").Value + " x " + Form.Field("Radio Type").Value + " radios"

        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv UHF Desc").Value = "Hire of " + Form.Field("Radio Type").Value + " walkie-talkie"

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

        Form.Field("Inv UHF Qty").Value = Form.Field("Number UHF").Value

        ' activate the "chargers included" message field
        Form.Field("Inv Charger Desc").Value = "Radio chargers included in price"

    End If

    If Cint(Form.Field("Number UHF 6-way").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number UHF 6-way").Value + " x six-slot radio charger units"
    End If

    If Cint(Form.Field("Number Sgl Charger").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Sgl Charger").Value + " x single radio charger units"
    End If

    If Cint(Form.Field("Number EM").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number EM").Value + " x Earpiece/microphones (in re-usable bags)"
        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv EM Desc").Value = "Hire of earpiece/microphone"
        Form.Field("Inv EM Qty").Value = Form.Field("Number EM").Value

        ' Mar 2013: set price according to length of hire
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv EM Price").Value = "1.50"
            Case 2
                Form.Field("Inv EM Price").Value = "2.00"
            Case 3
                Form.Field("Inv EM Price").Value = "2.50"
            Case 4
                Form.Field("Inv EM Price").Value = "3.00"
        End Select

    End If

    ' added Jan 2013 - code for semi-covert earpiece/mics
    If Cint(Form.Field("Number EMC").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number EMC").Value + " x Semi-covert earpiece/mics (in re-usable bags)"
        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv EMC Desc").Value = "Hire of semi-covert earpiece/mic"
        Form.Field("Inv EMC Qty").Value = Form.Field("Number EMC").Value

        ' Mar 2013: set price according to length of hire
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv EMC Price").Value = "2.50"
            Case 2
                Form.Field("Inv EMC Price").Value = "3.50"
            Case 3
                Form.Field("Inv EMC Price").Value = "5.00"
            Case 4
                Form.Field("Inv EMC Price").Value = "6.00"
        End Select


    End If


    ' added March 2010 - leather cases/straps
    If Cint(Form.Field("Number Cases").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Cases").Value + " x leather cases with carry straps"
        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv Case Desc").Value = "Hire of leather case with neck strap"
        Form.Field("Inv Case Qty").Value = Form.Field("Number Cases").Value
        ' Mar 2013: set price according to length of hire
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv Case Price").Value = "1.50"
            Case 2
                Form.Field("Inv Case Price").Value = "2.00"
            Case 3
                Form.Field("Inv Case Price").Value = "2.50"
            Case 4
                Form.Field("Inv Case Price").Value = "3.00"
        End Select
    End If

    ' added March 2010 - "Madonna" type headsets
    If Cint(Form.Field("Number Headset").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Headset").Value + " x headsets with boom mics"
        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv Headset Desc").Value = "Hire of headset"
        Form.Field("Inv Headset Qty").Value = Form.Field("Number Headset").Value

        ' Mar 2013: set price according to length of hire
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv Headset Price").Value = "2.50"
            Case 2
                Form.Field("Inv Headset Price").Value = "3.50"
            Case 3
                Form.Field("Inv Headset Price").Value = "5.00"
            Case 4
                Form.Field("Inv Headset Price").Value = "6.00"
        End Select

    End If

    ' added Jan 2013 - code for "big" aircraft style headsets
    If Cint(Form.Field("Number Headset Big").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Headset Big").Value + " x big aircraft-style headsets"
        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv Bighead Desc").Value = "Hire of aircraft-style big headset"
        Form.Field("Inv Bighead Price").Value = "5.00"
        Form.Field("Inv Bighead Qty").Value = Form.Field("Number Headset Big").Value

        ' Mar 2013: set price according to length of hire
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv Bighead Price").Value = "6.00"
            Case 2
                Form.Field("Inv Bighead Price").Value = "9.00"
            Case 3
                Form.Field("Inv Bighead Price").Value = "12.00"
            Case 4
                Form.Field("Inv Bighead Price").Value = "15.00"
        End Select
    End If

    ' added March 2010 - "parrot" type speaker / mics
    If Cint(Form.Field("Number Parrot").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Parrot").Value + " x remote speaker / microphones"
        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv Parrot Desc").Value = "Hire of speaker / microphone"

        Form.Field("Inv Parrot Qty").Value = Form.Field("Number Parrot").Value

        ' Mar 2013: set price according to length of hire
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv Parrot Price").Value = "1.50"
            Case 2
                Form.Field("Inv Parrot Price").Value = "2.00"
            Case 3
                Form.Field("Inv Parrot Price").Value = "2.50"
            Case 4
                Form.Field("Inv Parrot Price").Value = "3.00"
        End Select


    End If

    ' added March 2010 - extra radio batteries
    If Cint(Form.Field("Number Batteries").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Batteries").Value + " x extra radio battery packs"
        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv Batt Desc").Value = "Hire of spare battery pack"

        Form.Field("Inv Batt Qty").Value = Form.Field("Number Batteries").Value

        ' Mar 2013: set price according to length of hire
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv Batt Price").Value = "1.50"
            Case 2
                Form.Field("Inv Batt Price").Value = "2.00"
            Case 3
                Form.Field("Inv Batt Price").Value = "2.50"
            Case 4
                Form.Field("Inv Batt Price").Value = "3.00"
        End Select


    End If

    ' added April 2012 - Mobile/base radios (updated July 2023)
    If Cint(Form.Field("Number Icom").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Icom").Value + " x vehicle/base radios"
        ' Feb 2011: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv Icom Desc").Value = "Hire of vehicle/base radios"

        Form.Field("Inv Icom Qty").Value = Form.Field("Number Icom").Value

        ' Oct 2013: set price according to length of hire
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv Icom Price").Value = "19.00"
            Case 2
                Form.Field("Inv Icom Price").Value = "26.00"
            Case 3
                Form.Field("Inv Icom Price").Value = "31.00"
            Case 4
                Form.Field("Inv Icom Price").Value = "36.00"
        End Select

    End If

    ' May 2014: added code to add to hstring the descriptions for the ICOM/base radio aerials and power options
    ' Clip on aerials
    If Cint(Form.Field("Number Clipon Aerial").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Clipon Aerial").Value + " x clip-on aerials"
    End If

    ' Magmount aerials
    If Cint(Form.Field("Number Magmount").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Magmount").Value + " x magnetic-mount aerials"
    End If

    ' September 2018: added code to add to hstring the description for the walkie-talkie aerial adapters
    If Form.Field("Number Aerial Adapt").Value > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Aerial Adapt").Value + " x aerial adapters for walkie talkies"
    End If

    ' car power leads
    If Cint(Form.Field("Number ICOM Car Lead").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number ICOM Car Lead").Value + " x vehicle power leads"
    End If

    ' mains power supplies
    If Cint(Form.Field("Number ICOM PSU").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number ICOM PSU").Value + " x base radio mains power supplies"
    End If

    ' April 2016: added code to add number of metal detector wands and radio repeaters to hstring (note that repeaters are only on the hire
    ' sheet, and not yet on the invoices)

    ' wands - Feb 2018 wands to the invoice
    If Cint(Form.Field("Number Wand").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Wand").Value + " x metal detector wands"
        ' Feb 2018: fill Invoice description field and price if quantity of item greater than 0
        Form.Field("Inv Wand Desc").Value = "Hire of metal detector wands"

        Form.Field("Inv Wand Qty").Value = Form.Field("Number Wand").Value

        ' Feb 2018: set price according to length of hire for wands
        Select Case Form.Field("Weeks").Value
            Case 1
                Form.Field("Inv Wand Price").Value = "6.00"
            Case 2
                Form.Field("Inv Wand Price").Value = "9.00"
            Case 3
                Form.Field("Inv Wand Price").Value = "13.00"
            Case 4
                Form.Field("Inv Wand Price").Value = "17.00"
        End Select

    End If

    ' September 2018: if no value already inserted into the number of security wand batteries field, insert 1 per wand by default
    If Form.Field("Number Wand Battery").Value = 0 Then
        Form.Field("Number Wand Battery").Value = Form.Field("Number Wand").Value
    End If

    ' September 2018: add to hstring text for metal detector wand batteries and battery chargers"
    If Cint(Form.Field("Number Wand Battery").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Wand Battery").Value + " x metal detector wand batteries"
    End If

    If Cint(Form.Field("Number Wand Charger").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Wand Charger").Value + " x metal detector battery chargers"
    End If

    ' repeaters
    If Cint(Form.Field("Number Repeater").Value) > 0 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Repeater").Value + " x repeaters"
    End If


    ' insert appropriate values into delivery and collection description fields - this case is for the usual we send, they return
    If Form.Field("Send Or Collect").Value = "We send, cust return" Then

        Form.Field("Inv Delivery Desc").Value = "Delivery"
        Form.Field("Inv Send Desc").Value = "Send Date"
        Form.Field("Inv Return Desc").Value = "Customer to Return"

        If Form.Field("Delivery Cost").Value = "" Then
            Form.Field("Delivery Cost").Value = "15.00"
        End If

    End If

    ' insert appropriate values into delivery and collection description fields - this case is customer collect and return
    If Form.Field("Send Or Collect").Value = "Cust. collect/return" Then

        Form.Field("Inv Delivery Desc").Value = ""
        Form.Field("Inv Send Desc").Value = "Collect Date"
        Form.Field("Inv Return Desc").Value = "Customer to Return"

        Form.Field("Delivery Cost").Value = ""

        ' added late Oct 2013 - if the customer is to collect the kit from us, set the delivery name to  "** collected from office **"
        ' and delivery address and postcode fields to our office address
        ' modified Nov 2018 to leave the hirer name intact and only modify the address and postcode fields
        Form.Field("Delivery Address").Value = "*** COLLECTED FROM AMHERST OFFICE ***" + vbCrLf + "70 Kingsgate Road" + vbCrLf + "London"
        Form.Field("Delivery Postcode").Value = "NW6 4TE"

    End If

    ' insert appropriate values into delivery and collection description fields - this case is us sending and collecting
    If Form.Field("Send Or Collect").Value = "We send and pick up" Then

        Form.Field("Inv Delivery Desc").Value = "Delivery & Collection"
        Form.Field("Inv Send Desc").Value = "Send Date"
        Form.Field("Inv Return Desc").Value = "Cust. to advise when ready for collection"

        If Form.Field("Delivery Cost").Value = "" Then
            Form.Field("Delivery Cost").Value = "35.00"
        End If

    End If

    ' deal with hire of megaphones (taken off the multi-megaphone price discount, but left code in place for the future - May 2014)
    If Cint(Form.Field("Number Megaphone").Value) = 1 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Megaphone").Value + " Megaphone"

        Form.Field("Inv Mega Desc").Value = "Hire of megaphone"
        Form.Field("Inv Mega Price").Value = "16.00"
        Form.Field("Inv Mega Qty").Value = Form.Field("Number Megaphone").Value

        ' if no value already inserted into the "number of sets of batteries" field, insert 2 per megaphone by default
        If Cint(Form.Field("Number Megaphone Bat").Value) = 0 Then
            Form.Field("Number Megaphone Bat").Value = 2
        End If

    End If

    If Cint(Form.Field("Number Megaphone").Value) > 1 Then
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Megaphone").Value + " Megaphones"
        Form.Field("Inv Mega Desc").Value = "Hire of megaphones"
        Form.Field("Inv Mega Price").Value = "16.00"
        Form.Field("Inv Mega Qty").Value = Form.Field("Number Megaphone").Value

        ' if no value already inserted into the "number of sets of batteries" field, insert 2 per megaphone by default
        If Cint(Form.Field("Number Megaphone Bat").Value) = 0 Then
            Form.Field("Number Megaphone Bat").Value = (Form.Field("Number Megaphone").Value * 2)
        End If

    End If

    ' insert the text description for megaphone batteries if any are present
    If Cint(Form.Field("Number Megaphone Bat").Value) > 0 Then
        Form.Field("Inv Meg Batt Desc").Value = (Form.Field("Number Megaphone Bat").Value + " sets of 8 rechargeable batts included")
        hstring = hstring + vbCrLf + vbCrLf + "* " + Form.Field("Number Megaphone Bat").Value + " sets of 8 rechargeable batteries"
    End If

    ' added April 2012 - megaphone battery charger tick box checked
    If Form.Field("Megaphone Charger").Value Then
        hstring = hstring + vbCrLf + vbCrLf + "* 1 x megaphone battery charger unit"
    End If



    ' added May 2013 - if there is any text in the "Purchase Order" field, then insert it,
    ' prefixed with words "P.O. Number " into the displayed field on the invoice
    If Form.Field("Purchase Order").Value <> "" Then
        Form.Field("Inv Purchase Order").Value = "P.O. Number " + Form.Field("Purchase Order").Value
    End If

    ' added February 2018 - fill in the new "Invoice Date Fields"" using function MakeInvoiceDate
    ' this ensures that the dates are displayed correctly on the hire invoices and hire sheets
    Form.Field("Inv Booked Date").Value = MakeInvoiceDate(Form.Field("Booked Date").Value)
    Form.Field("Inv Send Out Date").Value = MakeInvoiceDate(Form.Field("Send Out Date").Value)
    Form.Field("Inv Due Back Date").Value = MakeInvoiceDate(Form.Field("Due Back Date").Value)

    ' add in the standard instruction sheet text if box is ticked
    If Form.Field("Instruc Walkies").Value Then
        hstring = hstring + vbCrLf + vbCrLf + "* 1 x Laminated walkie-talkie instruction sheet"
    End If

    ' add in the ICOM instruction sheet text if box is ticked
    If Form.Field("Instruc Icom").Value Then
        hstring = hstring + vbCrLf + vbCrLf + "* 1 x Laminated mobile/base radio instruc sheet"
    End If

    ' add in the megaphone instruction sheet text if box is ticked
    If Form.Field("Instruc Megaphone").Value Then
        hstring = hstring + vbCrLf + vbCrLf + "* 1 x Laminated megaphone instruction sheet"
    End If

    ' add the "Special Kit" field to the end of the list of items: this covers odd items, notes on damage to stuff sent out etc
    hstring = hstring + vbCrLf + vbCrLf + Form.Field("Special Kit").Value

    ' finally put the built-up "hstring" variable into the Hire Sheet Text" field
    Form.Field("Hire Sheet Text").Value = hstring

    ' make up the "All Address" field from the parts of the delivery name, contact, address and postcode, phone and email
    Form.Field("All Address").Value = Form.Field("Delivery Contact").Value + vbCrLf + Form.Field("Delivery Name").Value + vbCrLf + Form.Field("Delivery Address").Value + vbCrLf + Form.Field("Delivery Postcode").Value + vbCrLf + vbCrLf + Form.Field("Delivery Tel").Value + vbCrLf + vbCrLf + Form.Field("Delivery Email").Value

    '9 April 12th 2019 - at Nigel Park's suggestion, this section of code has
    ' define a variable called "cCust" to hold the connection from hire record to customer
    ' this makes it easier to refer to several times later on
    Dim cCust
    Set cCust = Form.Connection("To", "Customer")
    ' nstring is used to store the hire record's "Name" field, made up of the customer name (truncated to 27 chars if needed), the date and the
    ' modified reference number (see refstring)
    Dim nstring

    ' refstring is used to store the hire reference number field as a string, and then with its commas removed, it is then inserted into the
    ' name field
    Dim refstring

    nstring = ""
    refstring = ""

    ' put this here to test it out, instead of before hstring stuff, 10th March - seems a bit better in that the correct stuff all appears on
    ' second open of the form - BUT still does not save with correct name first time!

    'If Form.Field("Name").Value = "newhire" And cCust.FieldValue("Name") <> "" Then
    '  refstring = Cstr(Form.Field("Reference Number").Value)
    '  refstring = Replace(refstring, ",", "")
    '  nstring = Left(cCust.FieldValue("Name"), 27) + " - " + Form.Field("Send Out Date").Value + " ref " + refstring
    '  Form.Field("Name").Value = nstring

    'End If

    ' this is Nigel's  code to make the link to the customer and insert the string into the name field
    If Form.Field("Name").Value = "newhire" And Form.Connection("To", "Customer").ConnectedItemCount() = 1 Then
        refstring = CStr(Form.Field("Reference Number").Value)
        refstring = Replace(refstring, ",", "")
        nstring = Left(Form.Connection("To", "Customer").ItemName()  , 27) + " - " + Form.Field("Send Out Date").Value + " ref " + refstring
        Form.Field("Name").Value = nstring
    End If

    ' copy the name, address, postcode, phone, email, contact and discount percentage fields from the connected customer record, unless something else
    ' has been entered there already
    If Form.Field("Delivery Name").Value = "" Then
        Form.Field("Delivery Name").Value = cCust.FieldValue("Deliv Name")
    End If

    If Form.Field("Delivery Contact").Value = "" Then
        Form.Field("Delivery Contact").Value = cCust.FieldValue("Deliv Contact")
    End If

    If Form.Field("Delivery Postcode").Value = "" Then
        Form.Field("Delivery Postcode").Value = cCust.FieldValue("Deliv Postcode")
    End If

    If Form.Field("Delivery Address").Value = "" Then
        Form.Field("Delivery Address").Value = cCust.FieldValue("Deliv Address")
    End If

    If Form.Field("Delivery Tel").Value = "" Then
        Form.Field("Delivery Tel").Value = cCust.FieldValue("Deliv Telephone")
    End If

    If Form.Field("Delivery Email").Value = "" Then
        Form.Field("Delivery Email").Value = cCust.FieldValue("Deliv Email")
    End If

    If Form.Field("Discount Percentage").Value = "" Then
        Form.Field("Discount Percentage").Value = cCust.FieldValue("Discount Percentage")
    End If

    If Form.Field("Discount Description").Value = "" Then
        Form.Field("Discount Description").Value = cCust.FieldValue("Discount Description")
    End If

    ' call function to tidy up any file path entered to show the correct R: drive letter rather than "D:\amherst" etc
    If Form.Field("Invoice").Value <> "" Then
        Form.Field("Invoice").Value = InvoicePath(Form.Field("Invoice").Value)
    End If


End Sub

' this is the end of the On Save section above

' this makes the various buttons on the form work, including the "charity discount" insertion button work, and the buttons for number of weeks of hire
' Jan 2013: added code for the four buttons that insert the due back dates for 1,2,3 week and month (4 week) hire periods
' Mar 2013: added code for the "Student Discount" button, and amended the charity discount rate from 20% to 25%
' Oct 2013: added code to allow user to "pull in" hire quantities from the linked customer record - from Autoquote

Sub Form_OnClick(ControlId)
    Select Case ControlId
        Case "CommandButton1"
            Form.Field("Discount Description").Value = "Charity Discount"
            Form.Field("Discount Percentage").Value = "25%"
        Case "CommandButton2"
            If Form.Field("Send Out Date").Value <> "" Then
                Form.Field("Due Back Date").Value = DateAdd("d", 9, Form.Field("Send Out Date").Value)
                Form.Field("Due Back Date").Value = NotWeekends(Form.Field("Due Back Date").Value)
                Form.Field("Weeks").Value = 1

            End If
        Case "CommandButton3"
            If Form.Field("Send Out Date").Value <> "" Then
                Form.Field("Due Back Date").Value = DateAdd("d", 16, Form.Field("Send Out Date").Value)
                Form.Field("Due Back Date").Value = NotWeekends(Form.Field("Due Back Date").Value)
                Form.Field("Weeks").Value = 2
            End If

        Case "CommandButton4"
            If Form.Field("Send Out Date").Value <> "" Then
                Form.Field("Due Back Date").Value = DateAdd("d", 23, Form.Field("Send Out Date").Value)
                Form.Field("Due Back Date").Value = NotWeekends(Form.Field("Due Back Date").Value)
                Form.Field("Weeks").Value = 3
            End If

        Case "CommandButton5"
            If Form.Field("Send Out Date").Value <> "" Then
                Form.Field("Due Back Date").Value = DateAdd("d", 32, Form.Field("Send Out Date").Value)
                Form.Field("Due Back Date").Value = NotWeekends(Form.Field("Due Back Date").Value)
                Form.Field("Weeks").Value = 4
            End If
        Case "CommandButton6"
            Form.Field("Discount Description").Value = "Student Discount"
            Form.Field("Discount Percentage").Value = "25%"
        Case "CommandButton7"
        ' this button "pulls" the equipment quantity fields from the corresponding fields in the
        ' customer record, that have been put there by being read in from "AutoQuote"
            Form.Field("Number UHF").Value = cCust.FieldValue("Number UHF")
            Form.Field("Number Batteries").Value = cCust.FieldValue("Number Batteries")
            Form.Field("Number Cases").Value = cCust.FieldValue("Number Cases")
            Form.Field("Number EM").Value = cCust.FieldValue("Number EM")
            Form.Field("Number EMC").Value = cCust.FieldValue("Number EMC")
            Form.Field("Number Headset").Value = cCust.FieldValue("Number Headset")
            Form.Field("Number Headset Big").Value = cCust.FieldValue("Number Headset Big")
            Form.Field("Number Icom").Value = cCust.FieldValue("Number Icom")
            Form.Field("Number Megaphone").Value = cCust.FieldValue("Number Megaphone")
            Form.Field("Number Parrot").Value = cCust.FieldValue("Number Parrot")
        Case "CommandButton8"
        ' if there is an email address in the "delivery contact" field enclosed in angle brackets, strip it out and put
        ' it into the email field leaving just the actual name in the contact name field
        ' only do anything if there is an @ in the string in the first place
            If Instr(Form.Field("Delivery Contact").Value, "<") Then
                length = Len(Form.Field("Delivery Contact").Value)
                atpos = Instr(Form.Field("Delivery Contact").Value, "<")
                Form.Field("Delivery Email").Value = Right(Form.Field("Delivery Contact").Value, (length - atpos))
                Form.Field("Delivery Contact").Value = Left(Form.Field("Delivery Contact").Value, atpos)
            End If
        Case "CommandButton9"
        ' this button inserts the current date and time into the Packed Date and Packed Time fields
            Form.Field("Packed Date").Value = "today"
            Form.Field("Packed Time").Value = "now"
        Case "CommandButton10"
        ' this button inserts the current date and time into the Unpacked Date and Unpacked Time fields
            Form.Field("Unpacked Date").Value = "today"
            Form.Field("Unpacked Time").Value = "now"

        Case "CommandButton11"
        ' this button inserts the description "Parcelforce" into the Send Method field
            Form.Field("Send Method").Value = "Parcelforce / DB"
            If Form.Field("Send Or Collect").Value = "We send and pick up" Then
                Form.Field("Send Method").Value = "Parcelforce/DB and we collect"
            End If

        Case "CommandButton12"
        ' this button inserts the description "RUSH bike" into the Send Method field
            Form.Field("Send Method").Value = "RUSH motorbike"
            If Form.Field("Send Or Collect").Value = "We send and pick up" Then
                Form.Field("Send Method").Value = "RUSH motorbike and we collect"
            End If

        Case "CommandButton13"
        ' this button inserts the description "RUSH car/van" into the Send Method field
            Form.Field("Send Method").Value = "RUSH car/van"
            If Form.Field("Send Or Collect").Value = "We send and pick up" Then
                Form.Field("Send Method").Value = "RUSH car/van and we collect"
            End If

        Case "CommandButton14"
        ' this button inserts the description "Absolutely motorbike" into the Send Method field
            Form.Field("Send Method").Value = "Absolutely motorbike"
            If Form.Field("Send Or Collect").Value = "We send and pick up" Then
                Form.Field("Send Method").Value = "Absolutely motorbike and we collect"
            End If

        Case "CommandButton15"
        ' this button writes the delivery details to a CSV text file on the PC's local disk, which can
        ' then be uploaded into the Despatchbay web site
        'dim fs,fname
        'set fs=Server.CreateObject("Scripting.FileSystemObject")
        'set fname=fs.CreateTextFile("c:\test.txt",true)
        'fname.WriteLine("Hello World!")
        'fname.Close
        'set fname=nothing
        'set fs=nothing

'            Dim fso, DBtextfilename, DBstring
'            Set fso = CreateObject("Scripting.FileSystemObject")
'            Set DBtextfilename = fso.CreateTextFile("c:\Windows\temp\DBaddressfile.txt", True)
'            DBstring = Form.Field("Delivery Contact").Value + ", " + Form.Field("Delivery Address").Value + ", " + Form.Field("Delivery Postcode").Value + ", " + Form.Field("Delivery Telephone").Value + ", " + Form.Field("Delivery Telephone").Value
'            DBtextfilename.WriteLine(DBstring)
'            DBtextfilename.Close

        Case "CommandButton16"
        ' this button inserts the description "Absolutely car/van" into the Send Method field
            Form.Field("Send Method").Value = "Absolutely car/van"
            If Form.Field("Send Or Collect").Value = "We send and pick up" Then
                Form.Field("Send Method").Value = "Absolutely car/van and we collect"
            End If

        Case "CommandButton17"
        ' this button inserts the description "Amherst Staff" into the Send Method field
            Form.Field("Send Method").Value = "Amherst staff"
            If Form.Field("Send Or Collect").Value = "We send and pick up" Then
                Form.Field("Send Method").Value = "Amherst staff and we collect"
            End If

        Case "CommandButton18"
        ' actual return today
            Form.Field("Actual Return Date").Value = "today"

        Case "CommandButton19"
        'pack a hire
            PackHire()

        Case "CommandButton20"
        'unpack a hire
            UnpackHire()

        Case "CommandButton21"
        'actual send today'
            Form.Field("Actual Send Date").Value = "today"
            Form.Field("Status").Value = "Out"
            Form.Field("DB label printed").Value = "True"

        Case "CommandButton22"
        'return arranged tomorrow'
            Form.Field("Pickup Date").Value = "tomorrow"
            Form.Field("Pickup Arranged").Value = "True"


    End Select
End Sub

