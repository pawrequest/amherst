from __future__ import annotations

from typing import Literal, Self

from fastapi import Body, Depends, Query
from loguru import logger
from pydantic import BaseModel, Field, model_validator
from starlette.requests import Request

from amherst.models.amherst_models import AMHERST_TABLE_TYPES
from amherst.models.filters import FilterName
from amherst.models.maps import CURSOR_MAP
from pycommence.cursor_v2 import CursorAPI
from pycommence.filters import ConditionType, FilterArray
from pycommence.pycmc_types import MoreAvailable, Pagination as _Pagination

CsrName = Literal['Hire', 'Sale', 'Customer']

PAGE_SIZE = 30


class Pagination(_Pagination):
    @classmethod
    def from_query(cls, request: Request, limit: int | bool = Query(PAGE_SIZE), offset: int = Query(0)) -> Self:
        logger.debug(f'Pagination.from_query({limit=}, {offset=})')
        return cls(limit=limit, offset=offset)


async def template_name_from_query(csrname: CsrName = Query(...)):
    return CURSOR_MAP[csrname]['template']


class SearchRequest(BaseModel):
    csrname: CsrName
    filtername: FilterName | None = None
    package: dict[str, str] = Field(default_factory=dict)
    pagination: Pagination = Pagination()
    pk_value: str = ''
    condition: ConditionType = ConditionType.CONTAIN

    def filter_array(self, csr: CursorAPI | None = None) -> FilterArray:
        if not any([self.filtername, self.pk_value]):
            raise ValueError('filtername or pk_value required')
        if self.pk_value and not csr:
            raise ValueError('pk_value requires csr')
        filarray: FilterArray = CURSOR_MAP[self.csrname]['filters'].get(self.filtername, FilterArray())
        if self.pk_value:
            filarray.add_filter(csr.pk_filter(self.pk_value))
            filarray.logics.append('And')
        return filarray

    def __hash__(self):
        return hash(
            (
                self.csrname,
                self.filtername,
                self.pk_value,
                self.pagination.offset,
                self.pagination.limit,
                *list(self.package.items()),
            )
        )

    @property
    def q_str(self):
        return self.q_str_paginate()

    @property
    def query_str_json(self):
        return self.q_str_paginate(json=True)

    @property
    def next_q_str(self):
        return self.q_str_paginate(self.pagination.next_page())

    @property
    def next_q_str_json(self):
        return self.q_str_paginate(self.pagination.next_page(), json=True)

    def q_str_paginate(self, pagination: Pagination = None, json: bool = False):
        # todo package?
        pagination = pagination or self.pagination
        qstr = '/api' if json else ''
        qstr += f'/search?csrname={self.csrname}'
        if self.filtername:
            qstr += f'&filtername={self.filtername}'
        if self.pk_value:
            qstr += f'&pkvalue={self.pk_value}'
        qstr += f'&limit={pagination.limit}&offset={pagination.offset}'
        return qstr

    def next_request(self):
        return self.model_copy(update={'pagination': self.pagination.next_page()})

    def prev_request(self):
        return self.model_copy(update={'pagination': self.pagination.prev_page()})

    @classmethod
    def from_query(
        cls,
        request: Request,
        csrname: CsrName = Query(...),
        filtername: FilterName | None = Query(None),
        pk_value: str = Query(''),
        pagination: Pagination = Depends(Pagination.from_query),
    ):
        logger.warning(f'SearchRequest.from_query({csrname=}, {filtername=}, {pk_value=}, {pagination=})')
        return cls(
            csrname=csrname,
            pagination=pagination,
            pk_value=pk_value,
            filtername=filtername,
        )

    @classmethod
    def from_body(
        cls,
        csrname: CsrName = Body(...),
        filtername: FilterName | None = Body(None),
        pk_value: str = Body(''),
        package: dict | None = Body(default_factory=dict),
        pagination: Pagination = Depends(Pagination.from_query),
    ):
        logger.warning(f'SearchRequest.from_body({csrname=}, {filtername=}, {pk_value=}, {package=}, {pagination=})')
        res = cls(
            csrname=csrname,
            filtername=filtername,
            pagination=pagination,
            pk_value=pk_value,
            package=package,
        )
        return res.model_validate(res)


class SearchResponse[T: AMHERST_TABLE_TYPES](BaseModel):
    records: list[T]
    length: int = None
    search_request: SearchRequest | None = None
    more: MoreAvailable | None = None

    @model_validator(mode='after')
    def set_length(self):
        if self.length is None and self.records:
            self.length = len(self.records)
        return self
