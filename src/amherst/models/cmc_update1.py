# from __future__ import annotations
#
# from collections.abc import Awaitable, Callable
# from datetime import date
# from typing import Any
#
# from shipaw.fapi.responses import ShipmentResponse
# from shipaw.models.ship_types import ShipDirection
#
# from amherst.models.amherst_models import (
#     AmherstHire,
#     AmherstShipableBase,
# )
# from amherst.models.shipment import AmherstShipment
#
# CmcUpdateFuncAgnost = Callable[
#     [AmherstShipableBase, AmherstShipment, ShipmentResponse], Awaitable[dict[str, str]]
# ]
#
#
# def split_com_sep_str_field(record, fieldname: str) -> list[str]:
#     data_s: str = getattr(record, fieldname, None)
#     data_l = data_s.split(',') if data_s else []
#     return data_l
#
#
# def add_to_com_sep_str_field(data: list, value) -> str:
#     data.append(value)
#     return ','.join(data)
#
#
# async def add_tracking_to_list(record: AmherstShipableBase, resp: ShipmentResponse) -> str:
#     tracks = split_com_sep_str_field(record, 'tracking_numbers')
#     return add_to_com_sep_str_field(tracks, resp.shipment_num)
#
#
# async def make_update_dict(shipment: AmherstShipment, shipment_response: ShipmentResponse) -> dict[str, Any]:
#     """Adds tracking numbers and link."""
#     record = shipment.record
#     update_package = await cmc_update_dict(shipment, shipment_response)
#     if isinstance(record, AmherstHire):
#         extra = await cmc_update_dict_hire(shipment)
#         update_package.update(extra)
#     return update_package
#
#
# async def cmc_update_dict(shipment: AmherstShipment, shipment_response: ShipmentResponse):
#     record = shipment.record
#     shipdir = shipment.direction
#     tracks = await add_tracking_to_list(record, shipment_response)
#     update_package = {record.alias_lookup('tracking_numbers'): tracks}
#     if shipdir in [ShipDirection.INBOUND, ShipDirection.DROPOFF]:
#         update_package.update({record.alias_lookup('track_in'): shipment_response.tracking_link})
#     elif shipdir == ShipDirection.OUTBOUND:
#         update_package.update({record.alias_lookup('track_out'): shipment_response.tracking_link})
#     else:
#         raise ValueError(f'Invalid shipment direction: {shipdir}')
#     return update_package
#
#
# async def cmc_update_dict_hire(shipment: AmherstShipment):
#     record = shipment.record
#     if not isinstance(record, AmherstHire):
#         raise ValueError('Record is not an AmherstHire')
#     shipdir = shipment.direction
#     if shipdir in [ShipDirection.INBOUND, ShipDirection.DROPOFF]:
#         return await cmc_update_dict_hire_in(record, shipment)
#     elif shipdir == ShipDirection.OUTBOUND:
#         return await cmc_update_dict_hire_out(record)
#     else:
#         raise ValueError(f'Invalid shipment direction: {shipdir}')
#
#
# async def cmc_update_dict_hire_in(record: AmherstHire, shipment: AmherstShipment):
#     ret_notes = f'{date.today().strftime('%d/%m')}: pickup arranged for {shipment.shipping_date.strftime('%d/%m')}\r\n{record.return_notes}'
#     return {
#         record.alias_lookup('arranged_in'): 'True',
#         record.alias_lookup('pickup_date'): f'{shipment.shipping_date:%Y-%m-%d}',
#         record.alias_lookup('return_notes'): ret_notes,
#     }
#
#
# async def cmc_update_dict_hire_out(record: AmherstHire):
#     return {
#         record.alias_lookup('arranged_out'): 'True',
#     }
