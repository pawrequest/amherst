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
from amherst.models.commence_adaptors import CategoryName
from amherst.models.maps import mapper_from_query_csrname
import asyncio


# from amherst.office_tools.doc_handler import DocHandler


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


def timestamp() -> str:
    return datetime.now().strftime('%Y%m%dT%H%M%S')


def box_labels_26(order: AmherstShipableBase, tmplt, data_dir) -> Path:
    context = BoxLabelContext.from_shipable(order).__dict__
    template = DocxTemplate(tmplt)
    template.render(context)
    file_path = get_order_label_filename(order, data_dir)
    logger.info(f'Writing box label to {file_path.absolute()}')
    template.save(file_path)
    return file_path


def get_order_label_filename(order: AmherstShipableBase, data_dir) -> Path:
    filename = f'box_label{timestamp()}_{order.customer_name}_{order.category}.docx'
    file_path = data_dir / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()
    return file_path


async def record_from_commence(category: CategoryName, pk: str):
    mapper = await mapper_from_query_csrname(category)
    with pycommence_context(category) as cmc:
        record_ = cmc.read_row(pk=pk)
    record = mapper.record_model(row_info=record_.row_info, **record_.data)
    return record


def commence_box_label(category: CategoryName, pk: str, amherst_env: Path):
    settings = Settings(_env_file=amherst_env)
    data_dir = settings.data_dir
    tmplt = settings.template_dir / 'box.docx'
    record = asyncio.run(record_from_commence(category=category, pk=pk))
    box_labels_26(record, tmplt, data_dir)


if __name__ == '__main__':
    category = CategoryName.Customer
    pk = 'Test'
    amherst_env = Path(r"C:\prdev\envs\amdev\sandbox\amherst.env")
    commence_box_label(category, pk, amherst_env)
