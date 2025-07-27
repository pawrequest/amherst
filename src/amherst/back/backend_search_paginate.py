from __future__ import annotations

import dataclasses
import json
from functools import wraps
from typing import Self
from collections.abc import Sequence

from fastapi import Depends, Form, Query
from loguru import logger
from pycommence import MoreAvailable
from pycommence.resolvers import resolve_row_id
from pydantic import BaseModel, Field, model_validator
from pycommence.filters import ConditionType, ConnectedFieldFilter, FieldFilter, FilterArray
from pycommence.pycmc_types import MoreAvailable, Pagination as _Pagination

from amherst.models.commence_adaptors import CursorName, CustomerAliases
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.filters import FilterVariant
from amherst.models.maps import CategoryName, mapper_from_query_csrname, AmherstMap

PAGE_SIZE = 50


async def get_condition(condition: str = Query('')) -> ConditionType:
    return getattr(ConditionType, condition.upper(), ConditionType.CONTAIN)


class Pagination(_Pagination):
    @classmethod
    def from_query(cls, limit: int = Query(PAGE_SIZE), offset: int = Query(0)) -> Self:
        return cls(limit=limit, offset=offset)


class SearchRequest(BaseModel):
    csrname: CursorName | None = None
    csrnames: list[CursorName] | None = None
    row_id: str | None = None
    pk_value: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    customer_names: list[str] | None = Field(default_factory=list)
    condition: ConditionType = ConditionType.CONTAIN
    max_rtn: int | None = None
    search_dict: dict = Field(default_factory=dict)
    pagination: Pagination | None = Pagination()
    cmc_filter_i: int = 0
    py_filter_i: int = 0

    @model_validator(mode='after')
    def cursornames(self):
        if not self.csrname and not self.csrnames:
            raise ValueError('No csrname or csrnames provided')
        if self.csrname and not self.csrnames:
            self.csrnames = [self.csrname]
        return self

    def __str__(self):
        return (
            f'Csr: {self.csrname if self.csrname else ', '.join(self.csrnames)}'
            f'{' | pk=:' + self.pk_value if self.pk_value else ''}'
            f'{' | row_id=:' + self.row_id if self.row_id else ''}'
            f'{' | customer_name="' + self.customer_name + '"' if self.customer_name else ''}'
            f'{' | customer_id="' + self.customer_id + '"' if self.customer_id else ''}'
            f'{' | cmc_filter_i=' + str(self.cmc_filter_i) if self.cmc_filter_i else ''}'
            f'{' | py_filter_i=' + str(self.py_filter_i) if self.py_filter_i else ''}'
            f'{' | ' + str(self.pagination) if self.pagination else ''}'
        )

    @property
    def q_str(self):
        return self.q_str_paginate()

    @property
    def query_str_json(self):
        return self.q_str_paginate(api=True)

    @property
    def next_q_str(self):
        return self.q_str_paginate(self.pagination.next_page()) if self.pagination else None

    @property
    def next_q_str_json(self):
        return self.q_str_paginate(self.pagination.next_page(), api=True) if self.pagination else None

    def q_str_paginate(self, pagination: Pagination = None, api: bool = False):
        pagination = pagination or self.pagination
        qstr = '/api' if api else ''
        qstr += f'/search?csrname={self.csrname}'
        for attr in [
            'condition',
            'max_rtn',
            'cmc_filter_i',
            'py_filter_i',
            'pk_value',
            'row_id',
            'customer_id',
            'customer_name',
        ]:
            if val := getattr(self, attr):
                qstr += f'&{attr}={val}'
        if pagination:
            if pagination.limit:
                qstr += f'&limit={pagination.limit}'
            if pagination.offset:
                qstr += f'&offset={pagination.offset}'
        return qstr

    def next_request(self):
        return self.model_copy(update={'pagination': self.pagination.next_page()})

    def prev_request(self):
        return self.model_copy(update={'pagination': self.pagination.prev_page()})

    # @classmethod
    # @resolve_row_id
    # def from_id_or_pk(
    #     cls,
    #     csrname: CursorName = Query(...),
    #     pk: str = Query(''),
    #     row_id: str = Query(None),
    # ):
    #     return cls(
    #         csrname=csrname,
    #         pk_value=pk,
    #         row_id=row_id,
    #     )

    @classmethod
    def from_query(
        cls,
        csrname: CategoryName = Query(None),
        csrnames: list[CategoryName] = Query(None),
        pk_value: str = Query(''),
        pagination: Pagination = Depends(Pagination.from_query),
        condition: ConditionType = Depends(get_condition),
        max_rtn: int = Query(None),
        row_id: str = Query(None),
        customer_name: str = Query(None),
        customer_id: str = Query(None),
        py_filter_i: int = Query(0),
        cmc_filter_i: int = Query(0),
    ):
        return cls(
            csrname=csrname,
            csrnames=csrnames,
            pagination=pagination,
            pk_value=pk_value,
            condition=condition,
            max_rtn=max_rtn,
            row_id=row_id,
            customer_name=customer_name,
            customer_id=customer_id,
            cmc_filter_i=cmc_filter_i,
            py_filter_i=py_filter_i,
        )

    async def filter_array(self):
        mapper: AmherstMap = await mapper_from_query_csrname(self.csrname)
        fil_array = mapper.cmc_filters[self.cmc_filter_i].model_copy() if self.cmc_filter_i else FilterArray()
        # fil_array = getattr(mapper.cmc_filters, self.cmc_filter).__deepcopy__() if self.cmc_filter else FilterArray()
        if self.pk_value:
            fil_array.add_filter(FieldFilter(column=mapper.aliases.NAME, condition=self.condition, value=self.pk_value))

        if self.customer_name:
            if cust_con := mapper.connections.customer:
                customer_filter = FieldFilter(
                    column=CustomerAliases.CUSTOMER_NAME,
                    condition=self.condition,
                    value=self.customer_name,
                )
                fil_array.add_filter(ConnectedFieldFilter.from_fil(field_fil=customer_filter, connection=cust_con))
        return fil_array


class SearchResponse[T: AMHERST_TABLE_MODELS](BaseModel):
    records: list[T]
    length: int = 0
    search_request: SearchRequest
    more: MoreAvailable | None = None

    # @model_validator(mode='after')
    # def set_more(self):
    #     if self.more:
    #         self.more.html_link = ''
    #     return self

    def __str__(self):
        return (
            f'Search Response: {self.length}x {self.search_request.csrname if self.search_request.csrname else ', '.join(self.search_request.csrnames)} records'
            f'{' (' + str(self.more.n_more) + ' more available),' if self.more else '. '} '
            f'SearchRequest[{str(self.search_request)}]'
        )

    @model_validator(mode='after')
    def set_length(self):
        self.length = len(self.records)
        return self


class SearchResponseMulti(SearchResponse):
    search_request: Sequence[SearchRequest]

    def __str__(self):
        rtypes = '/'.join([req.csrname for req in self.search_request])
        return (
            f'Search Response with {self.length}x {rtypes} records. '
            f'SearchRequests[{'; '.join(str(_) for _ in self.search_request)}]'
            f'{', ' + str(self.more.n_more) + ' more available' if self.more else ''} '
        )


@dataclasses.dataclass
class MoreAvailableFront(MoreAvailable):
    json_link: str = None
    html_link: str = None
