from __future__ import annotations

import functools
from typing import Literal, Self

from fastapi import Body, Depends, Query
from loguru import logger
from pydantic import BaseModel, Field, model_validator

from amherst.models.amherst_models import AMHERST_TABLE_TYPES
from amherst.models.filters import FilterName
from amherst.models.maps import CURSOR_MAP, FILTER_MAP
from pycommence.filters import ConditionType, FilterArray
from pycommence.pycmc_types import MoreAvailable
from pycommence.pycommence_v2 import PyCommence

PAGE_SIZE = 30
CsrName = Literal['Hire', 'Sale', 'Customer']


class Pagination(BaseModel):
    offset: int = 0
    limit: int | None = PAGE_SIZE

    @classmethod
    def from_query(cls, limit: int | None = Query(PAGE_SIZE), offset: int = Query(0)) -> Self:
        logger.debug(f'Pagination.from_query({limit=}, {offset=})')
        return cls(limit=limit, offset=offset)


class SearchQuery(BaseModel):
    csrname: CsrName
    filtername: FilterName | None = None
    package: dict[str, str] | None = Field(default_factory=dict)
    pagination: Pagination = Pagination()
    filter_array: FilterArray | None = None
    pk_value: str = ''
    condition: ConditionType = ConditionType.CONTAIN

    def __hash__(self):
        return hash(
            (self.csrname, self.filtername, self.pk_value, self.pagination.offset, self.pagination.limit,
             *list(self.package.values()))
        )

    def q_str(self):
        # todo package?
        qstr = f'?csrname={self.csrname}'
        if self.filtername:
            qstr += f'&filtername={self.filtername}'
        if self.pk_value:
            qstr += f'&pkvalue={self.pk_value}'
        qstr += f'&limit={self.pagination.limit}&offset={self.pagination.offset}'
        return qstr

    @functools.lru_cache
    def next_query(self):
        return SearchQuery(
            csrname=self.csrname,
            filtername=self.filtername,
            package=self.package,
            pagination=Pagination(offset=self.pagination.offset + self.pagination.limit, limit=self.pagination.limit),
            pk_value=self.pk_value
        )

    @functools.lru_cache
    def prev_query(self):
        return SearchQuery(
            csrname=self.csrname,
            filtername=self.filtername,
            package=self.package,
            pagination=Pagination(offset=self.pagination.offset - self.pagination.limit, limit=self.pagination.limit),
            pk_value=self.pk_value
        )

    @model_validator(mode='after')
    def get_filter_array(self):
        if self.filtername:
            self.filter_array = FILTER_MAP.get(self.filtername, None)
        return self

    @classmethod
    def from_body(
            cls,
            csrname: CsrName = Body(...),
            filtername: FilterName | None = Body(None),
            pk_value: str = Body(''),
            package: dict | None = Body(None),
            pagination: Pagination = Depends(Pagination.from_query),
    ):
        return cls(
            csrname=csrname,
            filtername=filtername,
            package=package,
            pagination=pagination,
            pk_value=pk_value
        )

    def to_query_params(self) -> dict:
        return {
            'csrname': self.csrname,
            'filtername': self.filtername,
            'pk_value': self.pk_value,
            'package': self.package,
            'limit': self.pagination.limit,
            'offset': self.pagination.offset
        }


class SearchResponse[T:AMHERST_TABLE_TYPES](BaseModel):
    records: list[T]
    # todo more is a link with offset and limit
    more: bool
    length: int = None
    search_query: SearchQuery | None = None
    more_link: str | None = None

    @model_validator(mode='after')
    def set_more_link(self):
        if self.more and not self.more_link:
            self.more_link = self.get_more_link()
        return self

    def get_more_link(self):
        next_query = self.search_query.next_query()
        return next_query.q_str()

    @model_validator(mode='after')
    def set_length(self):
        if self.length is None and self.records:
            self.length = len(self.records)
        return self

    @classmethod
    async def from_q(cls, sq: SearchQuery, pycmc):
        record_type: type[BaseModel] = CURSOR_MAP[sq.csrname]['input_type']
        more, records = await gather_records(input_type=record_type, pycmc=pycmc, sq=sq)
        search_response = cls(records=records, more=more, search_query=sq)
        return search_response


async def gather_records(input_type, pycmc, sq):
    records = []
    more = False
    async for row in pk_search(pycmc, sq):
        if isinstance(row, MoreAvailable):
            more = True
            break
        records.append(input_type.model_validate(row))
    return more, records


async def pk_search(
        pycmc: PyCommence,
        sq: SearchQuery,
):
    filter_array = pycmc.csr(sq.csrname).pk_filter(pk=sq.pk_value, condition=sq.condition)
    for row in pycmc.read_rows(
            csrname=sq.csrname,
            with_category=True,
            pagination=sq.pagination,
            filter_array=filter_array
    ):
        yield row
