from dataclasses import dataclass
from pathlib import Path
from typing import Self

from docxtpl import DocxTemplate

from amherst.frontend_funcs import ordinal_dt
from amherst.models.amherst_models import AmherstHire, AmherstOrderBase, AmherstShipableBase
from amherst.office_am import dflt
from amherst.office_am.dflt import DFLT_PATHS


# from amherst.office_tools.doc_handler import DocHandler


def address_rows_limited(address: str):
    add_lst = address.split('\r\n')
    if len(add_lst) > 4:
        add_lst = add_lst[:4]
    add_str = '\r\n'.join(add_lst)
    return add_str


def box_labels_aio_tmplt(hire) -> Path:
    tmplt = DFLT_PATHS.BOX_TMPLT
    temp_file = dflt.DFLT_PATHS.TEMP_DOC

    del_add = address_rows_limited(hire['Delivery Address'])
    boxes = int(hire['Boxes'])
    context = dict(
        date=f"{hire['Send Out Date']:%A %d %B}",
        method=hire['Send Method'],
        customer_name=hire['To Customer'],
        delivery_address=del_add,
        delivery_contact=hire['Delivery Contact'],
        tel=hire['Delivery Tel'],
        boxes=boxes,
    )

    template = DocxTemplate(tmplt)
    template.render(context)
    template.save(temp_file)
    return temp_file


@dataclass
class BoxLabelContext:
    date: str
    method: str
    customer_name: str
    delivery_address: str
    delivery_contact: str
    tel: str
    boxes: int

    @classmethod
    def from_shipable(cls, order: AmherstShipableBase) -> Self:
        return BoxLabelContext(
            date=ordinal_dt(order.send_date),
            method=order.delivery_method,
            customer_name=order.customer_name,
            delivery_address=order.delivery_address_str,
            delivery_contact=order.delivery_contact_name,
            tel=order.delivery_contact_phone,
            boxes=order.boxes,
        )


def box_labels_26(order: AmherstShipableBase) -> Path:
    tmplt = DFLT_PATHS.BOX_TMPLT
    temp_file = dflt.DFLT_PATHS.TEMP_DOC

    context = BoxLabelContext.from_shipable(order).__dict__

    template = DocxTemplate(tmplt)
    template.render(context)
    template.save(temp_file)
    return temp_file




#
#
# def box_labels_sep(hire, doc_handler: DocHandler):
#     total_number_of_parcels = int(hire['Boxes'])
#
#     templates = []
#     for i in range(total_number_of_parcels):
#         box = i + 1
#         package = f"Package {box}/{total_number_of_parcels}"
#         context = dict(
#             date=f"{hire['Send Out Date']:%A %d %B}",
#             method=hire['Send Method'],
#             customer_name=hire['To Customer'],
#             delivery_address=hire['Delivery Address'],
#             delivery_contact=hire['Delivery Contact'],
#             tel=hire['Delivery Tel'],
#             package=package,
#         )
#
#         template = DocxTemplate(tmplt)
#         template.render(context)
#         template.save(temp_file)
#         pdf_file = doc_handler.to_pdf(temp_file)
#         pdf1 = fitz.open(pdf_file)
#
#
#
#     pdf1 = fitz.open(pdf_files[0])
#     for template in templates[1:]:
#         template.save(temp_file)
#         pdf_file = doc_handler.to_pdf(temp_file)
#         pdf2 = fitz.open(pdf_file)
#         pdf_files.append(pdf_file)
#
#     doc_b = fitz.open("b.pdf")  # open the 2nd document
#     doc_a.insert_pdf(doc_b)  # merge the docs
#     doc_a.save("a+b.pdf")  # save the merged document with a new filename
#
#     merger.write(temp_file.with_suffix('.pdf'))
#
#     merger.close()
#     ...
