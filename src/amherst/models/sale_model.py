# import datetime as dt
# import typing as _ty
#
# from shipr.models import pf_ext, pf_shared, pf_top
#
# from amherst.models import am_shared
# from amherst.models.am_shared import addr_lines_dict_am
#
#
# class Sale(pf_shared.BasePFType):
#     cmc_table_name: _ty.ClassVar[str] = 'Sale'
#     record: dict[str, str]
#
#     # @_p.computed_field
#     @property
#     def boxes(self) -> int:
#         return 1
#
#     # @_p.computed_field
#     @property
#     def name(self) -> str:
#         return self.record.get(am_shared.HireFields.NAME)
#
#     # @_p.computed_field
#     @property
#     def ship_date(self) -> dt.date:
#         """uses cmc cannonical format yyyymmdd"""
#         return dt.date.today()
#
#     # @_p.computed_field
#     @property
#     def input_address(self) -> pf_ext.AddressRecipient:
#         return pf_ext.AddressRecipient(
#             **addr_lines_dict_am(self.record.get(am_shared.HireFields.DELIVERY_ADDRESS)),
#             town='',
#             postcode=self.record.get(am_shared.HireFields.POSTCODE),
#         )
#
#     # @_p.computed_field
#     @property
#     def contact(self) -> pf_top.Contact:
#         return pf_top.Contact(
#             business_name=self.record.get(am_shared.HireFields.CUSTOMER),
#             email_address=self.record.get(am_shared.HireFields.DELIVERY_EMAIL),
#             mobile_phone=self.record.get(am_shared.HireFields.SALE_TELEPHONE),
#             contact_name=self.record.get(am_shared.HireFields.DELIVERY_CONTACT),
#         )
#
