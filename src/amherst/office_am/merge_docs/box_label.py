from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Self

from docxtpl import DocxTemplate
from loguru import logger
from pycommence import pycommence_context

from amherst.config import Settings
from amherst.frontend_funcs import ordinal_dt
from amherst.models.amherst_models import (
    AmherstSale,
    AmherstShipableBase,
)

# from amherst.office_tools.doc_handler import DocHandler
SETTINGS = Settings(_env_file=r"C:\prdev\envs\amdev\sandbox\amherst.env")


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
            method=order.delivery_method or '',
            customer_name=order.customer_name,
            delivery_address=order.delivery_address_str,
            delivery_contact=order.delivery_contact_name,
            tel=order.delivery_contact_phone,
            boxes=order.boxes,
        )


def ts_now_for_filename() -> str:
    return datetime.now().strftime('%Y%m%dT%H%M%S')


def box_labels_26(order: AmherstShipableBase) -> Path:
    tmplt = SETTINGS.template_dir / 'box.docx'

    context = BoxLabelContext.from_shipable(order).__dict__
    template = DocxTemplate(tmplt)
    template.render(context)
    file_path = get_order_label_filename(order)
    logger.info(f'Writing box label to {file_path.absolute()}')
    template.save(file_path)
    return file_path


def get_order_label_filename(order: AmherstShipableBase) -> Path:
    data_dir = SETTINGS.data_dir
    filename = f'box_label{ts_now_for_filename()}_{order.customer_name}_{order.category}.docx'
    file_path = data_dir / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()
    return file_path


def from_commence():
    with pycommence_context('Sale') as cmc:
        sale_ = cmc.read_row(pk='Bridgewater Primary School - 15/12/2025 ref 1120')
        sale = AmherstSale(row_info=sale_.row_info, **sale_.data)
        box_labels_26(sale)


if __name__ == '__main__':
    from_commence()
    # with open(r'C:\prdev\amdev\amherst\data\test_customer.json') as f:
    #     cust_data = f.read()
    # customer = AmherstCustomer.model_validate_json(cust_data)
    # box_labels_26(customer)
    #
    # with open(r'C:\prdev\amdev\amherst\data\test_sale.json') as f:
    #     sale_data = f.read()
    # sale = AmherstSale.model_validate_json(sale_data)
    # box_labels_26(sale)
    #
    # with open(r'C:\prdev\amdev\amherst\data\test_hire.json') as f:
    #     hire_data = f.read()
    # hire = AmherstHire.model_validate_json(hire_data)
    # box_labels_26(hire)
    ...

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
