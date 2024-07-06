from __future__ import annotations

from typing import Literal, Self

from fastapi import Body, Depends, Query
from loguru import logger
from pydantic import BaseModel, Field, model_validator

from amherst.models.amherst_models import AMHERST_TABLE_TYPES
from amherst.models.filters import FilterName
from amherst.models.maps import CURSOR_MAP, FILTER_MAP
from pycommence.filters import FilterArray
from pycommence.pycommence_v2 import PyCommence

PAGE_SIZE = 20
CsrName = Literal['Hire', 'Sale', 'Customer']


class MoreAvailable:
    ...


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
    package: dict | None = Field(default_factory=dict)
    pagination: Pagination = Pagination()
    filter_array: FilterArray | None = None
    pk_value: str = ''

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


class SearchResponse[T:AMHERST_TABLE_TYPES](BaseModel):
    records: list[T]
    # todo more is a link with offset and limit
    more: bool
    # pagination: Pagination
    length: int = None
    search_query: SearchQuery | None = None

    @model_validator(mode='after')
    def set_length(self):
        if self.length is None and self.records:
            self.length = len(self.records)
        return self

    @classmethod
    async def from_query(cls, sq: SearchQuery, pycmc):
        input_type: type[BaseModel] = CURSOR_MAP[sq.csrname]['input_type']
        more = False
        records = []
        async for row in do_search(sq.csrname, sq.pk_value, pycmc, sq.pagination):
            if isinstance(row, MoreAvailable):
                more = True
                break
            records.append(input_type.model_validate(row))
        return SearchResponse(records=records, more=more, search_query=sq)


async def do_search(
        csrname: CsrName,
        pk_value: str,
        pycmc: PyCommence,
        pagination: Pagination,
):
    for rownum, row in enumerate(
            pycmc.read_rows_pk_contains(
                pk_value,
                csrname=csrname,
                count=pagination.limit + 1,
                offset=pagination.offset,
                with_category=True
            ), start=1
    ):
        yield MoreAvailable() if rownum > pagination.limit else row
