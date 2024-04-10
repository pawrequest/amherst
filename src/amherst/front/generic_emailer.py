greeting = """
Hi,
Thanks for choosing to hire from Amherst. 

"""

goodbye = """
If you have any queries please let us know.

Kind Regards
Amherst Enterprises
"""

invoice_body = """
Please find attached the invoice for your recent hire from Amherst.

"""


def missing_kit_body(missing):
    return """
Thanks for returning the hired equipment - I hope it worked well for your event. 

Unfortunately the return was missing the following items - can you please look/check with colleagues to see if they can be recovered - otherwise i'll draw up an invoice for replacement.
Kind regards, 
the Amherst team 

MISSING KIT: 
{missing}

(If you have already discussed missing items with us please disregard this automatically generated email)
 
"""


email_body_map = {
    'invoice': invoice_body,
    'missing_kit': missing_kit_body,
}
