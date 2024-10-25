from __future__ import annotations

from typing import Self

from fastapi import Body, Depends, Path, Query
from loguru import logger
from pydantic import BaseModel, Field, model_validator
from starlette.requests import Request
from pycommence.cursor_v2 import CursorAPI
from pycommence.filters import ConditionType, FilterArray
from pycommence.pycmc_types import MoreAvailable, Pagination as _Pagination

# from amherst.back.pyc_backend import pycmc_f_path
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.filters import get_customer_filter, get_hire_filter, get_sale_filter
from amherst.models.maps import AmherstTableName

PAGE_SIZE = 30


class Pagination(_Pagination):
    @classmethod
    def from_query(cls, request: Request, limit: int | bool = Query(PAGE_SIZE), offset: int = Query(0)) -> Self:
        logger.debug(f'Pagination.from_query({limit=}, {offset=})')
        return cls(limit=limit, offset=offset)


class SearchRequest(BaseModel):
    csrname: AmherstTableName
    filtered: bool = True
    package: dict = Field(default_factory=dict)
    pagination: Pagination = Pagination()
    pk_value: str | None = None
    condition: ConditionType = ConditionType.CONTAIN
    row_id: str | None = None
    max_rtn: int = None

    def src_filter(self, csr: CursorAPI | None = None) -> FilterArray:
        # I DONT LIKE THIS AT ALL!!
        if self.pk_value and not csr:
            raise ValueError('pk_value requires csr')
        if self.filtered:
            match self.csrname:
                case 'Hire':
                    return get_hire_filter(self.pk_value)
                case 'Sale':
                    return get_sale_filter(self.pk_value)
                case 'Customer':
                    return get_customer_filter(self.pk_value)
        if self.pk_value:
            return csr.pk_filter_array(pk=self.pk_value, condition=self.condition)
            # return FilterArray.from_filters(csr.pk_filter_array(pk=self.pk_value, condition=self.condition))
        return FilterArray()

    # def __hash__(self):
    #     return hash(
    #         (
    #             self.csrname,
    #             self.filtername,
    #             self.pk_value,
    #             self.pagination.offset,
    #             self.pagination.limit,
    #             *list(self.package.items()),
    #         )
    #     )

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
        if self.filtered:
            qstr += f'&filtered={str(self.filtered).lower()}'
        if self.pk_value:
            qstr += f'&pkvalue={self.pk_value}'
        qstr += f'&limit={pagination.limit}&offset={pagination.offset}'
        return qstr

    def next_request(self):
        return self.model_copy(update={'pagination': self.pagination.next_page()})

    def prev_request(self):
        return self.model_copy(update={'pagination': self.pagination.prev_page()})

    @classmethod
    def from_path(
            cls,
            csrname: AmherstTableName = Path(...),
            filtered: bool = Query(True),
            pk_value: str = Path(...),
            pagination: Pagination = Depends(Pagination.from_query),
    ):
        logger.debug(f'SearchRequest.from_path({csrname=}, {pk_value=}, {pagination=})')
        return cls(
            csrname=csrname,
            pagination=pagination,
            pk_value=pk_value,
            filtered=filtered,
        )

    @classmethod
    def get_all(
            cls,
            csrname: AmherstTableName = Path(...),
            filtered: bool = Query(True),
            pagination: Pagination = Depends(Pagination.from_query),
    ):
        logger.warning(f'SearchRequest.from_path({csrname=}, {pagination=})')
        return cls(
            csrname=csrname,
            pagination=pagination,
            filtered=filtered,
        )

    @classmethod
    def from_query(
            cls,
            csrname: AmherstTableName = Path(...),
            filtered: bool = Query(True),
            pk_value: str = Query(''),
            pagination: Pagination = Depends(Pagination.from_query),
    ):
        logger.warning(f'SearchRequest.from_query({csrname=}, {filtered=}, {pk_value=}, {pagination=})')
        return cls(
            csrname=csrname,
            pagination=pagination,
            pk_value=pk_value,
            filtered=filtered,
        )

    @classmethod
    def from_body(
            cls,
            csrname: AmherstTableName = Body(...),
            filtered: bool = Body(True),
            pk_value: str = Body(None),
            package: dict = Body(default_factory=dict),
            pagination: Pagination = Depends(Pagination.from_query),
            condition: ConditionType = Body(ConditionType.CONTAIN),
            row_id: str = Body(None),
            max_rtn: int = Body(None)
    ):

        logger.warning(f'SearchRequest.from_body({csrname=}, {filtered=}, {pk_value=}, {package=}, {pagination=})')
        return cls(
            csrname=csrname,
            filtered=filtered,
            pagination=pagination,
            pk_value=pk_value,
            package=package,
            condition=condition,
            row_id=row_id,
            max_rtn=max_rtn,
        )


class SearchResponse[T: AMHERST_TABLE_MODELS](BaseModel):
    records: list[T]
    length: int = None
    search_request: SearchRequest | None = None
    more: MoreAvailable | None = None

    @model_validator(mode='after')
    def set_length(self):
        if self.length is None and self.records:
            self.length = len(self.records)
        return self
