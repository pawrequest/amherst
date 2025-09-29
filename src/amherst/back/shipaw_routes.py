# from pathlib import Path
#
# from combadge.core.errors import BackendError
# from fastapi import APIRouter, Body, Depends, Form
# from loguru import logger
# from starlette.requests import Request
# from starlette.responses import HTMLResponse, JSONResponse
#
# from amherst.actions.emailer import send_label_email
# from amherst.back.backend_pycommence import pycommence_get_one
# from amherst.back.ship_funcs import get_el_client, try_book_shipment, try_update_cmc
# from amherst.back.ship_queries import (
#     shipment_f_form,
#     shipment_req_str_to_shipment2,
#     shipment_str_to_shipment,
# )
# from amherst.config import amherst_settings
# from amherst.models.amherst_models import AmherstHire, AmherstShipableBase
# from amherst.models.shipment import AmherstShipment, AmherstShipmentrequest
#
#
# from parcelforce_expresslink.address import (
#     AddressChoice as AddressChoicePF,
#     AddressRecipient,
#     Contact as ContactPF,
# )
# from parcelforce_expresslink.client import ParcelforceClient
# from shipaw.fapi.responses import ShipawTemplateResponse
# from shipaw.config import shipaw_settings
# from shipaw.fapi.alerts import Alert, AlertType, Alerts, maybe_alert_phone_number
# from shipaw.fapi.requests import AddressRequest
# from shipaw.models.address import Address, AddressChoice
# from shipaw.models.shipment import Shipment
# from shipaw.providers.parcelforce_provider import full_contact_from_provider_contact_address
#
# from shipaw.fapi.json_routes import ship_form as shipaw_ship_form
# router = APIRouter()
#
#
# @router.get('/ship_form_am', response_class=HTMLResponse)
# async def ship_form(
#     request: Request,
#     record: AmherstShipableBase = Depends(pycommence_get_one),
# ) -> HTMLResponse:
#     # pf_settings = pf_sett()
#     template = 'ship/form_shape.html'
#     alerts: Alerts = request.app.alerts
#
#     if any(['prdev' in str(_).lower() for _ in Path(__file__).parents]):
#         msg = '"prdev" in cwd tree - BETA MODE - This is a development version of Amherst Shipper'
#         logger.warning(msg)
#         alerts += Alert(message=msg, type=AlertType.WARNING)
#
#     if isinstance(record, AmherstHire) and 'parcelforce' not in record.delivery_method.lower():
#         msg = f'"Parcelforce" not in delivery_method: {record.delivery_method}'
#         logger.warning(msg)
#         alerts += Alert(message=msg, type=AlertType.WARNING)
#
#     if shipaw_settings().shipper_live:
#         msg = 'Shipper Live is True - Real Shipments will be booked'
#     else:
#         msg = 'Shipper_live is False - No Shipments will be booked'
#     logger.warning(msg)
#     alerts += Alert(message=msg, type=AlertType.NOTIFICATION)
#
#     shipment = record.shipment()
#
#     resp = await shipaw_ship_form(request=request, shipment=shipment)
#     if isinstance(resp, ShipawTemplateResponse):
#         logger.warning(f'Rendering SHIPAW template {resp.template_path} with context keys: {list(resp.context.keys())}')
#         return shipaw_settings().templates.TemplateResponse(request, resp.template_path, resp.context)
#
#     ctx = {'request': request, 'record': record, 'shipment': shipment}
#     return amherst_settings().templates.TemplateResponse(template, ctx)
#
#
# @router.post('/order_review_am', response_class=HTMLResponse)
# async def order_review(
#     request: Request,
#     shipment: AmherstShipment = Depends(shipment_f_form),
#     # record: AmherstShipableBase = Depends(record_str_to_record),
#     provider_name: str = Form(...),
# ) -> HTMLResponse:
#     alerts = await maybe_alert_phone_number(shipment.remote_full_contact.contact.mobile_phone)
#     logger.info('Shipment Form Posted')
#     template = 'ship/order_review.html'
#     ship_req = AmherstShipmentrequest(shipment=shipment, provider_name=provider_name)
#     return amherst_settings().templates.TemplateResponse(
#         template, {'request': request, 'shipment_request': ship_req, 'alerts': alerts}
#     )
#
#
# @router.post('/post_confirm_am', response_class=HTMLResponse)
# async def order_confirm(
#     request: Request,
#     shipment_req: AmherstShipmentrequest = Depends(shipment_req_str_to_shipment2),
#     # record: AmherstShipableBase = Depends(record_str_to_record),
# ) -> HTMLResponse:
#     logger.info('Booking Shipment')
#
#     # shipment_req.context['cmc_record'] = record
#
#     shipment_response = await try_book_shipment(shipment_req)
#     shipment_req.provider.handle_response(shipment_req, shipment_response)
#     record = shipment_req.shipment.record
#
#     if not shipment_response or not shipment_response.success:
#         logger.error(f'Booking failed')
#         return amherst_settings().templates.TemplateResponse(
#             'alerts.html',
#             {
#                 'request': request,
#                 'alerts': shipment_response.alerts,
#                 'shipment': shipment_req.shipment,
#             },
#         )
#
#     # get label
#     await shipment_response.write_label_file()
#
#     # update commence
#     await try_update_cmc(record, shipment_req.shipment, shipment_response)
#
#     return amherst_settings().templates.TemplateResponse(
#         'ship/order_confirmed.html',
#         {
#             'request': request,
#             'shipment': shipment_req.shipment,
#             'response': shipment_response,
#             'alerts': shipment_response.alerts,
#         },
#     )
#
#
# #
# # class AddressRequest(ShipawBaseModel):
# #     postcode: str
# #     address: Address | None = None
# #     contact: Contact | None = None
#
#
# @router.get('/home_mobile_phone_am', response_class=HTMLResponse)
# async def home_mobile_phone():
#     mobile_phone = shipaw_settings().mobile_phone
#     return f"""
#     <input type="tel" id="mobile_phone" name="mobile_phone" value="{mobile_phone}" required>
#     """
#
#
# @router.post('/cand_am', response_model=list[AddressChoice], response_class=JSONResponse)
# async def get_addr_choices(
#     request: Request,
#     body: AddressRequest = Body(...),
#     el_client: ParcelforceClient = Depends(get_el_client),
# ) -> list[AddressChoice]:
#     """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.
#
#     Args:
#         request: Request - FastAPI request object
#         body: Address - request body containing postcode and optional address
#         el_client: ELClient - Parcelforce ExpressLink client
#     """
#     # address = ParcelforceShippingProvider.provider_address(address)
#     postcode = body.postcode
#     address_agnost = body.address
#     pf_address = (
#         AddressRecipient(
#             address_line1=address_agnost.address_lines[0],
#             address_line2=address_agnost.address_lines[1] if len(address_agnost.address_lines) > 1 else '',
#             address_line3=address_agnost.address_lines[2] if len(address_agnost.address_lines) > 2 else '',
#             town=address_agnost.town,
#             postcode=address_agnost.postcode,
#             country=address_agnost.country,
#         )
#         if address_agnost
#         else None
#     )
#
#     try:
#         res = el_client.get_choices(postcode=postcode, address=pf_address)
#         res_agnost = [await convert_choice(_) for _ in res]
#         return res_agnost
#     except BackendError as e:
#         alert = Alert(
#             message=f'Error fetching candidates: {e}',
#             type=AlertType.ERROR,
#         )
#         request.app.alerts += alert  # todo is this received frontend?
#         logger.warning(f'Error fetching candidates: {e}')
#         addr = Address(address_lines=['ERROR:', str(e)], town='Error', postcode='Error', business_name='Error')
#         chc = AddressChoice(address=addr, score=0)
#         return [chc]
#
#
# async def convert_choice(choice: AddressChoicePF) -> AddressChoice:
#     fc = full_contact_from_provider_contact_address(contact=ContactPF.empty(), address=choice.address)
#     return AddressChoice(
#         address=fc.address,
#         score=choice.score,
#     )
#
#
# @router.post('/email_label', response_class=HTMLResponse)
# async def email_label_am(
#     shipment: Shipment = Depends(shipment_str_to_shipment),
#     label: Path = Form(...),
# ):
#     shipment._label_file = label
#     await send_label_email(shipment)
#     return '<span>Re</span>'
