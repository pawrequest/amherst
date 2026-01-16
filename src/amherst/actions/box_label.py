import asyncio
import os
from datetime import datetime
from pathlib import Path

from docxtpl import DocxTemplate
from jinja2 import Environment
from loguru import logger
from pycommence import pycommence_context

from amherst.config import Settings
from amherst.frontend_funcs import ordinal_dt
from amherst.models.amherst_models import (
    AmherstShipableBase,
)
from amherst.models.commence_adaptors import CategoryName
from amherst.models.maps import mapper_from_query_csrname


def timestamp() -> str:
    return datetime.now().strftime('%Y%m%dT%H%M%S')


def generate_box_label(order: AmherstShipableBase, settings: Settings, tmplt_name: str = 'box_pd.docx') -> Path:
    tmplt = settings.template_dir / tmplt_name
    template = DocxTemplate(tmplt)
    jinja_env = Environment()
    jinja_env.globals['ordinal_dt'] = ordinal_dt
    context = {'order': order}
    template.render(context=context, jinja_env=jinja_env)
    file_path = get_box_label_filename(order, settings.data_dir)
    logger.info(f'Writing box label to {file_path.absolute()}')
    template.save(file_path)
    return file_path


def get_box_label_filename(order: AmherstShipableBase, data_dir) -> Path:
    filename = f'box_label_for_{order.customer_name}_{order.category}@{timestamp()}.docx'
    file_path = data_dir / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()
    return file_path


async def record_from_commence(category: CategoryName, pk: str) -> AmherstShipableBase:
    mapper = await mapper_from_query_csrname(category)
    with pycommence_context(category) as cmc:
        record_ = cmc.read_row(pk=pk)
    record = mapper.record_model(row_info=record_.row_info, **record_.data)
    return record


def commence_box_label(category: CategoryName, pk: str, amherst_env: Path) -> Path:
    settings = Settings(_env_file=amherst_env)
    record = asyncio.run(record_from_commence(category=category, pk=pk))
    return generate_box_label(record, settings)


if __name__ == '__main__':
    category = CategoryName.Trial
    pk = 'Test -  ref 1660'
    amherst_env = Path(r"C:\prdev\envs\amdev\sandbox\amherst.env")
    output = commence_box_label(category, pk, amherst_env)
    os.startfile(output)
