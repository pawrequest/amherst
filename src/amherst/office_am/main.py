# import argparse
# import shutil
# from pathlib import Path
#
# import PySimpleGUI as sg
# from office_tools.o_tool import OfficeTools
#
# from pycommence.api import csr_context
# from .dflt import DFLT_HIRE_EMAIL, DFLT_PATHS
# from .gui import invoice_gui
# from .merge_docs.box_label import box_labels_aio_tmplt
# from .order.invoice import get_inv_temp
# from .order.transact import TransactionContext
#
#
# def main(args):
#     # ot = OfficeTools.libre() if args.libre else OfficeTools.microsoft()
#     ot = OfficeTools.auto_select()
#     with csr_context('Hire') as csr:
#         hire = csr.one_record(, args.HIRE_NAME_OFFICE
#
#     if args.box:
#         box_labels_aio_tmplt(hire)
#         return
#
#     with TransactionContext() as tm:
#         hire_inv = tm.get_hire_invoice(hire)
#         out_file = (DFLT_PATHS.INV_OUT_DIR / hire_inv.inv_num).with_suffix('.docx')
#         template, temp_file = get_inv_temp(hire_inv)
#
#         if args.doall:
#             do_all(temp_file, out_file, hire, ot)
#         else:
#             event_loop(cmc, temp_file, out_file, hire, ot)
#
#
# def event_loop(cmc, temp_file, outfile, hire, ot: OfficeTools):
#     window = invoice_gui()
#
#     while True:
#         event, values = window.read()
#         if event == sg.WINDOW_CLOSED:
#             break
#         elif event == 'Submit':
#             if values['-SAVE-']:
#                 saved_docx = shutil.copy(temp_file, outfile)
#                 if not saved_docx:
#                     raise FileNotFoundError(f'Failed to save {temp_file} to {outfile}')
#                 # pdf_file = ot.pdf.from_docx(outfile)
#                 pdf_file = ot.doc.to_pdf(outfile)
#                 if values['-EMAIL-']:
#                     do_email(pdf_file, ot.email)
#                 if values['-PRINT-']:
#                     print_file(pdf_file)
#                 if values['-CMC-']:
#                     do_cmc(cmc, 'Hire', hire, outfile)
#             if values['-OPEN-']:
#                 opened = ot.doc.open_document(outfile if outfile.exists() else temp_file)
#             break
#
#
# def do_all(cmc, temp_file, outfile, hire, ot: OfficeTools):
#     saved_docx = shutil.copy(temp_file, outfile)
#     pdf_file = ot.doc.to_pdf(outfile)
#     # print_file(outfile.with_suffix('.pdf'))
#     do_cmc(cmc, 'Hire', hire, outfile)
#     do_email(pdf_file, ot.email)
#     opened = ot.doc.open_document(saved_docx or temp_file)
#
#     ...
#
#
# def check_really_edit(transaction):
#     if 'test' not in transaction['Name'].lower():
#         raise ValueError(
#             f"dev safety check - Transaction {transaction['Name']} does not contain 'test'"
#         )
#         # if sg.popup_ok_cancel(f'Log {transaction["Name"]} to CMC?') != 'OK':
#         #     return False
#     return True
#
#
# def do_cmc(cmc, table, transaction, outfile):
#     package = {'Invoice': outfile}
#     if not check_really_edit(transaction):
#         return
#     try:
#         cmc.edit_record(table, transaction['Name'], package)
#     except CmcError as e:
#         sg.popup_error(f'Failed to log to CMC with error: {e}')
#     else:
#         return True
#
#
# def do_email(attachment: Path, handler: EmailHandler, email_=DFLT_HIRE_EMAIL):
#     email_.attachment_path = attachment
#     try:
#         handler.create_open_email(email_)
#
#     except EmailError as e:
#         sg.popup_error(f'Email failed with error: {e}')
#
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('hire_name', help='The name of the hire')
#     parser.add_argument('--print', action='store_true', help='Print the invoice after generating.')
#     parser.add_argument('--openfile', action='store_true', help='Open the file.')
#     parser.add_argument('--libre', action='store_true', help='Use Free Office tools.')
#     parser.add_argument(
#         '--doall',
#         action='store_true',
#         help='save, convert to pdf, print, email, and log to commence.'
#     )
#     parser.add_argument('--box', action='store_true', help='Send a box label')
#
#     args = parser.parse_args()
#     main(args)
