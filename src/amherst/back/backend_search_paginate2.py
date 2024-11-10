from __future__ import annotations

from fastapi import Body, Depends, Form
from loguru import logger
from pydantic import BaseModel, model_validator

from amherst.back.backend_search_paginate import Pagination
from pycommence.filters import FieldFilter, Logic, SortOrder
from pycommence.pycmc_types import MoreAvailable
from amherst.models.amherst_models import AmherstHire, AmherstSale
from amherst.models.maps import AmherstTableName


# class SearchRequest2(BaseModel):
#     csrname: AmherstTableName
#     row_id: str | None = None
#     pk_value: str | None = None
#     search_dict: SearchDict | None = None
#     pagination: Pagination = Pagination()
#     max_rtn: int | None = None
#     dflt_filter: bool = False
#
#     @classmethod
#     def from_body(
#         cls,
#         csrname: AmherstTableName = Body(...),
#         row_id: str = Body(None),
#         name: str = Body(None),
#         search_dict: dict | None = Body(None),
#         pagination: Pagination = Depends(Pagination.from_query),
#         max_rtn: int = Body(None),
#         dflt_filter: bool = Body(False),
#     ):
#         res = cls(
#             csrname=csrname, name=name, pagination=pagination, row_id=row_id, max_rtn=max_rtn, dflt_filter=dflt_filter
#         )
#         if search_dict:
#             res.search_dict = SearchDict(**search_dict)
#         return res
#
#     @classmethod
#     def from_form(
#         cls,
#         csrname: AmherstTableName = Form(...),
#         row_id: str = Form(None),
#         name: str = Form(None),
#         search_dict: dict | None = Body(None),
#         max_rtn: int = Form(None),
#         dflt_filter: bool = Form(False),
#         pagination: Pagination = Depends(Pagination.from_query),
#     ):
#         res = cls(
#             csrname=csrname,
#             row_id=row_id,
#             name=name,
#             max_rtn=max_rtn,
#             dflt_filter=dflt_filter,
#             pagination=pagination,
#         )
#         if search_dict:
#             res.search_dict = SearchDict(**search_dict)
#         logger.info(f'{cls.__name__}.from_form: {res}')
#         return res
#
#     @property
#     def q_str(self):
#         return self.q_str_paginate()
#
#     @property
#     def query_str_json(self):
#         return self.q_str_paginate(api=True)
#
#     @property
#     def next_q_str(self):
#         return self.q_str_paginate(self.pagination.next_page())
#
#     @property
#     def next_q_str_json(self):
#         return self.q_str_paginate(self.pagination.next_page(), api=True)
#
#     def q_str_paginate(self, pagination: Pagination = None, api: bool = False):
#         # todo package?
#         pagination = pagination or self.pagination
#         qstr = '/api' if api else ''
#         qstr += f'/search?csrname={self.csrname}'
#         if self.dflt_filter:
#             qstr += f'&filtered={str(self.dflt_filter).lower()}'
#         if self.pk_value:
#             qstr += f'&pkvalue={self.pk_value}'
#         if self.row_id:
#             qstr += f'&row_id={self.row_id}'
#         if self.search_dict.customer_name:
#             qstr += f'&customer_name={self.search_dict.customer_name}'
#         qstr += f'&limit={pagination.limit}&offset={pagination.offset}'
#         return qstr
#
#     def next_request(self):
#         return self.model_copy(update={'pagination': self.pagination.next_page()})
#
#     def prev_request(self):
#         return self.model_copy(update={'pagination': self.pagination.prev_page()})
#
#
# class SearchDict(BaseModel):
#     customer_name: str | None = None
#     filters: list[FieldFilter] | None = None
#     logics: list[Logic] | None = None
#     sorts: list[list[str, SortOrder]] | None = None
#
#     @model_validator(mode='after')
#     def val_(self):
#         if self.filters and not self.logics:
#             self.logics = ['And'] * (len(self.filters) - 1)
#         return self
#
#
# # class SearchResponse2(BaseModel):
# #     records: list[AMHERST_TABLE_MODELS]
# #     length: int = 0
# #     search_request: SearchRequest2 | None = None
# #     more: MoreAvailable | None = None
# #
# #     @model_validator(mode='after')
# #     def set_length(self):
# #         self.length = len(self.records)
# #         return self
#
#
# class CustomerRequest(BaseModel):
#     name: str
#
#
# class CustomerResponse(BaseModel):
#     name: str
#     hires: list[AmherstHire]
#     sales: list[AmherstSale]
#     length: int = 0
#     more: MoreAvailable | None = None
#
#     @model_validator(mode='after')
#     def set_length(self):
#         self.length = sum((len(self.hires), len(self.sales)))
#         return self
