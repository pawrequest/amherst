from __future__ import annotations

from amherst_core.consts_enums import CategoryName
from pycommence import PyCommence
from pycommence.core.row_data import RowData


async def row_from_pycommence(category: CategoryName, record_name: str) -> RowData:
    with PyCommence(category) as pycmc:
        return pycmc.item_read_csr(pk=record_name)


def row_from_pycommence_sync(category: CategoryName, record_name: str) -> RowData:
    with PyCommence(category) as pycmc:
        return pycmc.item_read_csr(pk=record_name)
