from __future__ import annotations

import json
from typing import Self

from fastapi import Body, Depends, Form, Query
from loguru import logger
from pydantic import BaseModel, Field, model_validator
from starlette.requests import Request

from pycommence.filters import ConditionType
from pycommence.pycmc_types import MoreAvailable, Pagination as _Pagination
# from amherst.back.pyc_backend import pycmc_f_path
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.maps import AmherstTableName, CMAP

PAGE_SIZE = 30


class Pagination(_Pagination):
    @classmethod
    def from_query(cls, request: Request, limit: int | bool = Query(PAGE_SIZE), offset: int = Query(0)) -> Self:
        return cls(limit=limit, offset=offset)


class SearchRequest(BaseModel):
    csrname: AmherstTableName
    row_id: str | None = None
    pk_value: str | None = None
    filtered: bool = True
    condition: ConditionType = ConditionType.CONTAIN
    max_rtn: int | None = None
    package: dict = Field(default_factory=dict)
    pagination: Pagination = Pagination()

    @property
    def q_str(self):
        return self.q_str_paginate()

    @property
    def query_str_json(self):
        return self.q_str_paginate(api=True)

    @property
    def next_q_str(self):
        return self.q_str_paginate(self.pagination.next_page())

    @property
    def next_q_str_json(self):
        return self.q_str_paginate(self.pagination.next_page(), api=True)

    def q_str_paginate(self, pagination: Pagination = None, api: bool = False):
        # todo package?
        pagination = pagination or self.pagination
        qstr = '/api' if api else ''
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
    def from_query(
        cls,
        csrname: AmherstTableName = Query(...),
        filtered: bool = Query(True),
        pk_value: str = Query(''),
        pagination: Pagination = Depends(Pagination.from_query),
        condition: ConditionType = Query(ConditionType.CONTAIN),
        max_rtn: int = Query(None),
        row_id: str = Query(None),
    ):
        logger.info(f'SearchRequest.from_query({csrname=}, {filtered=}, {pk_value=}, {pagination=})')
        return cls(
            csrname=csrname,
            pagination=pagination,
            pk_value=pk_value,
            filtered=filtered,
            condition=condition,
            max_rtn=max_rtn,
            row_id=row_id,
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
        max_rtn: int = Body(None),
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
    length: int = 0
    search_request: SearchRequest | None = None
    more: MoreAvailable | None = None

    @model_validator(mode='after')
    def set_length(self):
        self.length = len(self.records)
        return self


async def record_from_json_str_form(
    record_str: str = Form(...),
) -> AMHERST_TABLE_MODELS:
    record_dict = json.loads(record_str)
    category = record_dict['category']
    model = CMAP[category].record_model
    print(record_str)
    return model.model_validate(**record_dict)

    # return record_type.model_validate_json(record_str)
