# # from __future__ import annotations
# from __future__ import annotations
#
# from abc import ABC
# from datetime import date
#
# from pydantic import AliasGenerator, BaseModel, ConfigDict
#
# from shipaw.models.pf_msg import ShipmentResponse
# from shipaw.models.pf_shipment import Shipment, ShipmentAwayCollection, ShipmentAwayDropoff
# from amherst.models.commence_adaptors import (
#     AM_DATE,
#     CategoryName,
#     HireStatus,
#     SaleStatus,
#     customer_alias,
#     hire_alias,
#     sale_alias,
#     trial_alias,
# )
# from shipaw.ship_types import limit_daterange_no_weekends
#
#
# # TableLit = Literal['Hire', 'Sale', 'Customer']
# # SHIP_DATE = Annotated[
# #     date,
# #     _p.BeforeValidator(limit_daterange_no_weekends),
# # ]
#
#
# def split_addr_str(address: str) -> dict[str, str]:
#     addr_lines = address.splitlines()
#     if len(addr_lines) < 3:
#         addr_lines.extend([''] * (3 - len(addr_lines)))
#     elif len(addr_lines) > 3:
#         addr_lines[2] = ','.join(addr_lines[2:])
#         addr_lines = addr_lines[:3]
#
#     used_lines = [_ for _ in addr_lines if _]
#     town = used_lines.pop() if len(used_lines) > 1 else ''
#     return {f'address_line{num}': line for num, line in enumerate(used_lines, start=1)} | {'town': town}
#
#
# class AmherstTableBase(BaseModel, ABC):
#     model_config = ConfigDict(
#         populate_by_name=True,
#         use_enum_values=True,
#     )
#     row_id: str
#     name: str
#     customer_name: str
#     category: CategoryName
#
#     delivery_contact_name: str
#     delivery_contact_business: str
#     delivery_contact_phone: str
#     delivery_contact_email: str
#
#     delivery_address_str: str
#     delivery_address_pc: str
#
#     send_date: AM_DATE = date.today()
#
#     boxes: int = 1
#
#     tracking_numbers: str = ''
#     track_in: str = ''
#     track_out: str = ''
#
#     def contact_dict(self) -> dict:
#         return {
#             'contact_name': self.delivery_contact_name,
#             'business_name': self.delivery_contact_business,
#             'mobile_phone': self.delivery_contact_phone,
#             'email_address': self.delivery_contact_email,
#         }
#
#     def address_dict(self) -> dict:
#         return {
#             **split_addr_str(self.delivery_address_str),
#             'postcode': self.delivery_address_pc,
#         }
#
#     @property
#     def og_address(self):
#         return self.address_dict()
#
#     def shipment_dict(self):
#         return {
#             'recipient_address': self.address_dict(),
#             'recipient_contact': self.contact_dict(),
#             'total_number_of_parcels': self.boxes,
#             'shipping_date': limit_daterange_no_weekends(self.send_date),
#             **shipment_refs_dict_from_str(self.customer_name),
#         }
#
#     def amherst_shipment_dict(self):
#         return {
#             'category': self.category,
#             'row_id': self.row_id,
#             **self.shipment_dict(),
#         }
#
#     def shipment(self):
#         return Shipment.model_validate(self.shipment_dict())
#
#     def am_shipment(self):
#         return AmherstShipment.model_validate(self.amherst_shipment_dict())
#
#
# class AmherstCustomer(AmherstTableBase):
#     model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=customer_alias))
#     # model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=customer_alias, )) WHY comma?!
#     category: CategoryName = 'Customer'
#     invoice_email: str = ''
#     accounts_email: str = ''
#     hires: str = ''
#     sales: str = ''
#
#
#
# class AmherstOrderBase(AmherstTableBase, ABC):
#     boxes: int = 1
#     invoice: str = ''
#     arranged_out: bool = False
#     arranged_in: bool = False
#     delivery_method: str = ''
#     status: str
#
#
# class AmherstTrial(AmherstOrderBase):
#     model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=trial_alias))
#     category: CategoryName = 'Trial'
#     status: str
#
#
# class AmherstSale(AmherstOrderBase):
#     category: CategoryName = 'Sale'
#     model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=sale_alias))
#     status: SaleStatus
#
#
# class AmherstHire(AmherstOrderBase):
#     category: CategoryName = 'Hire'
#     model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=hire_alias))
#     status: HireStatus
#
#
# class AmherstShipment(Shipment):
#     category: CategoryName
#     row_id: str
#
#     def shipment(self):
#         shipdict = self.model_dump(exclude={'category', 'row_id'})
#         return Shipment.model_validate(shipdict)
#
#
# class AmherstShipmentAwayCollection(AmherstShipment, ShipmentAwayCollection): ...
#
#
# class AmherstShipmentAwayDropoff(AmherstShipment, ShipmentAwayDropoff): ...
#
#
# class AmherstShipmentResponse(ShipmentResponse):
#     row_id: str
#     category: str
#
#
# AMHERST_ORDER_MODELS = AmherstHire | AmherstSale | AmherstTrial
# AMHERST_TABLE_MODELS = AMHERST_ORDER_MODELS | AmherstCustomer
#
#
# #
# # def dt_ordinal(dt: datetime | date) -> str:
# #     return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')
# #     # return dt.strftime('%a {th} %b %Y').replace('{th}', date_int_w_ordinal(dt.day))
#
#
# def shipment_refs_dict_from_str(ref_str: str, max_len: int = 24) -> dict[str, str]:
#     reference_numbers = {}
#
#     for i in range(1, 6):
#         start_index = (i - 1) * max_len
#         end_index = i * max_len
#         if start_index < len(ref_str):
#             reference_numbers[f'reference_number{i}'] = ref_str[start_index:end_index]
#         else:
#             break
#     return reference_numbers
#
#
# def address_from_str(add_str: str, postcode: str):
#     return {
#         **split_addr_str(add_str),
#         'postcode': postcode,
#     }
