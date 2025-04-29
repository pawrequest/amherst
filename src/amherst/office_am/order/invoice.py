from pathlib import Path
from typing import Tuple

# import PySimpleGUI as sg
from docxtpl import DocxTemplate

from .order_ent import HireInvoice
from ..dflt import DFLT_PATHS, format_currency


def get_inv_temp(inv_o: HireInvoice,
                 tmplt_p=DFLT_PATHS.INV_TMPLT, temp_file_p=DFLT_PATHS.TEMP_INV, out_file=DFLT_PATHS.TEMP_INV) \
        -> Tuple[DocxTemplate, Path]:


    template = render_tmplt(inv_o, tmplt_p)

    while True:
        try:
            template.save(out_file)
            return template, temp_file_p
        except Exception as e:
            if sg.popup_ok_cancel("Close the invoice file and try again") == 'OK':
                continue
            else:
                raise e


def render_tmplt(inv_o: HireInvoice, tmplt=DFLT_PATHS.INV_TMPLT) -> DocxTemplate:
    try:
        template = DocxTemplate(tmplt)
        context = invoice_template_context(inv_o)
        template.render(context)
        return template
    except Exception as e:
        raise e


def invoice_template_context(invoice):
    return {
        'dates': invoice.hire_dates,
        'inv_address': invoice.inv_add,
        'del_address': invoice.del_add,
        'order': invoice.order,
        'currency': format_currency,
        # 'self': self,
        'inv_num': invoice.inv_num,
    }
