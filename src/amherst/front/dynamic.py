# from __future__ import annotations
#
# from abc import ABC
# from datetime import date, timedelta
# from enum import Enum
#
# from pydantic import BaseModel
#
# import shipr.models.pf_shared
# from amherst.front import amui
# from amherst.front.ui_helpers import BoxesEnum
#
# import shipr.models.pf_ext
#
#
# def date_range_enum():
#     return Enum(
#         "DateRange", {str(d): amui.date_string(d) for d in [date.today() + timedelta(days=i) for i in range(7)]}
#     )
#
#
# def make_address_enum(candidates: list[shipr.models.exp.AddressRecipient]):
#     return Enum("AddressChoice", {f"address {i}": cand.address_line1 for i, cand in enumerate(candidates)})
#
#
# class BookingForm(BaseModel, ABC):
#     boxes: BoxesEnum
#     address: Enum
#     ship_date: date_range_enum()
#     ship_service: shipr.models.shared.ServiceCode = shipr.models.shared.ServiceCode.EXPRESS24
#
#
# def make_starting_form(candidates: list[shipr.models.exp.AddressRecipient]) -> type[BaseModel]:
#     addr_enum = make_address_enum(candidates)
#
#     class _Form(BookingForm):
#         boxes: BoxesEnum
#         address: addr_enum
#         ship_date: date_range_enum()
#         ship_service: shipr.models.shared.ServiceCode = shipr.models.shared.ServiceCode.EXPRESS24
#
#     return _Form
