import random
from pprint import pprint

import pytest
import pytest_asyncio
from loguru import logger

from amherst.back.backend_pycommence import pycommence_context
from amherst.back.backend_search_paginate import Pagination
from amherst.models.amherst_models import AmherstTableBase
from amherst.models.maps2 import AmherstMap, maps2
from pycommence.pycommence_v2 import PyCommence


@pytest_asyncio.fixture(
    params=['Hire', 'Sale', 'Customer']
)
def pycmc(request) -> PyCommence:
    table = request.param
    # mapper = maps2(table)
    with pycommence_context(table) as pycmc_:
        csr = pycmc_.csr()
        logger.info(f'testing against {csr.row_count} {table} records')
        yield pycmc_


def test_pycmc(pycmc):
    csr = pycmc.csr()
    assert csr.row_count > 0


@pytest.mark.asyncio
async def test_record(pycmc):
    mapper: AmherstMap = await maps2(pycmc.get_csrname())
    pag = Pagination(
        offset=random.randint(0, 30),
    )
    filtered = pycmc.read_rows(filter_array=mapper.cmc_filters.loose, pagination=pag)
    recordtype = mapper.record_model
    record_dict = next(filtered)
    record: AmherstTableBase = recordtype.model_validate(record_dict)
    assert record.row_id
    print(record)
    print(type(record))
    amship = record.am_shipment()
    assert amship.contract_number
    pprint(amship)