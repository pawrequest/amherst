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
