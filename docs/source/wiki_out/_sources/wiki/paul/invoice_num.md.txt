# Next Invoice Number

Retrieve the next invoice number and store it in clipboard.

Also available as commence agent.

- Looks in 'R:\ACCOUNTS\invoices' for existing filenames "A00000.pdf" to "A99999.pdf" 
- Discards any file which does not have 20 consecutively numbered invoices before it. (avoid random filename scuppering everything)
- Finds the last invoice number and increments it by 1
- Stores the new invoice number in the clipboard

