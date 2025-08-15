Option Explicit
' define variables length and atpos for use in calculations
DIM length, atpos

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
    'If Form.Field("Status").Value = "Booked in and packed" And Form.Field("Packed By").Value = "" Then
    '    MsgBox "You cannot mark a hire as 'packed' without entering the initials for who packed it", vbCritical, "WARNING"
    '    Form.MoveToField("Packed By")
    '    Form.Abort
    '    Exit Sub
    'End If
    FixNoPackedBy()

    'Prevent saving a hire as "Booked in and packed" if the packed date and time is empty
    'If Form.Field("Status").Value = "Booked in and packed" And Form.Field("Packed Date").Value = "" Then
    '    MsgBox "You cannot mark a hire as 'packed' without entering the date and time that it was packed", vbCritical, "WARNING"
    '    Form.MoveToField("Packed By")
    '    Form.Abort
    '    Exit Sub
    'End If
    FixNoPackedDate()

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

            Dim fso, DBtextfilename, DBstring
            Set fso = CreateObject("Scripting.FileSystemObject")
            Set DBtextfilename = fso.CreateTextFile("c:\Windows\temp\DBaddressfile.txt", True)
            DBstring = Form.Field("Delivery Contact").Value + ", " + Form.Field("Delivery Address").Value + ", " + Form.Field("Delivery Postcode").Value + ", " + Form.Field("Delivery Telephone").Value + ", " + Form.Field("Delivery Telephone").Value
            DBtextfilename.WriteLine(DBstring)
            DBtextfilename.Close

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
        ' this button inserts the current date into the "Actual Return Date"
            Form.Field("Actual Return Date").Value = "today"

        Case "CommandButton19"
        'Paul's button to pack a hire"
            PackHire()

        Case "CommandButton20"
        'Paul's button to unpack a hire"
            UnpackHire()


        Case "CommandButton21"
            Form.Field("Actual Send Date").Value = "today"
            Form.Field("Status").Value = "Out"
            Form.Field("DB label printed").Value = "True"

        Case "CommandButton22"
            Form.Field("Pickup Date").Value = "tomorrow"
            Form.Field("Pickup Arranged").Value = "True"


    End Select
End Sub


'****** PR_FUNCS ***********

Sub FixNoPackedBy()
'Prevent saving a hire as "Booked in and packed" if the initials field for who packed it is empty
    If Form.Field("Status").Value = "Booked in and packed" And Form.Field("Packed By").Value = "" Then
        dim packer
        packer = InputBox("Who Packed This Hire?", "Who Packed")
        If packer = "" Then
            Form.Abort
            Exit Sub
        Else
            Form.Field("Packed By").Value = packer
        End If
    End If
End Sub

Sub FixNoPackedDate()
'Prevent saving a hire as "Booked in and packed" if the packed date and time is empty
    If Form.Field("Status").Value = "Booked in and packed" And Form.Field("Packed Date").Value = "" Then
        If MsgBox("No Packed Date and Time entered - Do you want to: use 'Now'?", vbYesNo + vbQuestion, "Choose an Option") = vbYes Then
            Form.Field("Packed Date").Value = "Today"
            Form.Field("Packed Time").Value = "Now"
        Else
            Form.Abort
            Exit Sub
        End If
    End If
End Sub


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
        missing = InputBox("What was missing? (replace form 'Missing Kit' Field)", "What's Missing?")
        Form.Field("Missing Kit").Value = missing
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
    msgbox("Emailing customer about upcoming shipment")
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
        AddMissingKitEmailContact()
        MsgBox("EMAILED and added contact log")
    End if
    Dim today
    today = Right("0" & Day(Now), 2) & "/" & Right("0" & Month(Now), 2)
    Form.Field("Return Notes").Value = today & ": Missing Kit Email Sent" & vbNewLine & _
        Form.Field("Return Notes").Value

    ' close objects'
    Set olApp = Nothing
    Set objMailItem = Nothing
    Set cCust = Nothing

End Sub

Sub AddMissingKitEmailContact()
    dim logName, hireName, missing
    missing = Form.Field("Missing Kit").Value
    hireName = Form.Field("Name").Value
    logName = "Missing Kit Email Sent Re: " & hireName
    Call AddContactLog(logName, missing)
End Sub

Sub AddContactLog(title, notes)
    dim cursor, cCustomer, custName, addSet, result
    dim nameColIndex, dateColIndex, timeColIndex, notesColIndex, custColIndex
    Set cCustomer = Form.Connection("To", "Customer")
    custName = cCustomer.FieldValue("Name")

    set cursor = Form.Application.Database.GetCursor(0, "Log", 0)
    set addSet = cursor.GetAddRowSet(1, 0)
    nameColIndex = addSet.GetColumnIndex("Name", 0)
    dateColIndex = addSet.GetColumnIndex("Date", 0)
    notesColIndex = addSet.GetColumnIndex("Notes", 0)
    timeColIndex = addSet.GetColumnIndex("Time", 0)
    custColIndex = addSet.GetColumnIndex("Relates To Customer", 0)

    addSet.ModifyRow 0, nameColIndex, title, 0
    addSet.ModifyRow 0, dateColIndex, "today", 0
    addSet.ModifyRow 0, timeColIndex, "now", 0
    addSet.ModifyRow 0, custColIndex, custName, 0
    addSet.ModifyRow 0, notesColIndex, notes, 0

    result = addSet.commit(0)
End Sub


'Giles_funcs.vbs

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
