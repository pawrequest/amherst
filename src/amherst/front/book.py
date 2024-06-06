# """
# Pages and Endpoints for Booking Shipments.
# """
# from __future__ import annotations
#
# import datetime as dt
# import os
#
# import fastapi
# import sqlmodel as sqm
# from comtypes import CoInitialize, CoUninitialize
# from fastui import FastUI, components as c, events, events as e
# from fastui.components.display import DisplayLookup, DisplayMode
# from loguru import logger
# from pawdantic import paw_strings
# from pawdantic.pawui import builders, pawui_types
# import shipaw
# from pycommence import PyCommence
# from shipaw import ELClient
# from shipaw.ship_ui import states as ship_states
#
# from amherst import am_db
# from amherst.front import booked, ship, support
# from amherst.front.support import update_shiprec_shipment
# from amherst.models.shipment_record import ShipmentRecordDB, ShipmentRecordInDB, ShipmentRecordOut
#
# router = fastapi.APIRouter()
#
#
# @router.get(
#     '/confirm/{shiprec_id}/{shipment_64}',
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def confirm_or_back(
#         shiprec_id: int,
#         shipment_64: str,
#         el_client: ELClient = fastapi.Depends(am_db.get_el_client),
#         session: sqm.Session = fastapi.Depends(am_db.get_session),
# ) -> list[c.AnyComponent]:
#     """Endpoint to submit shipment and return 'Confirm or Back' page.
#
#     Args:
#         shiprec_id (int): BookingManager id.
#         shipment_64 (str): State as Base64 encoded JSON.
#         el_client (ELClient, optional): The shipper object - defaults to fastapi.Depends(amherst.am_db.get_pfc).
#         session (sqm.Session, optional): The database session - defaults to fastapi.Depends(amherst.am_db.get_session).
#
#     Returns:
#         c.Page: :meth:`~confirm_book_page`
#
#     """
#     shipment = ship_states.Shipment.model_validate_64(shipment_64)
#     shipment.candidates = el_client.get_candidates(shipment.address.postcode)
#
#     man_in = await update_shiprec_shipment(shiprec_id, session, shipment)
#     return await confirm_or_back_page(man_in)
#
#
# async def confirm_or_back_page(
#         shiprec: ShipmentRecordInDB, alert_dict: pawui_types.AlertDict = None
# ) -> list[c.AnyComponent]:
#     """Confirm or Back page.
#
#     Display the current shipment and buttons to proceed with booking or go back.
#
#     Args:
#         shiprec (managers.MANAGER_IN_DB): The shiprec object.
#         alert_dict (pawui_types.AlertDict, optional): The alert dictionary - defaults to None.
#
#     Returns:
#         c.Page: Pre-Confirmation page.
#
#     """
#     return await builders.page_w_alerts(
#         components=[
#             c.Heading(
#                 text=f'Confirm details for {shiprec.record.name}',
#                 level=1,
#                 class_name='row mx-auto my-5'
#             ),
#             c.ServerLoad(path=f'/book/check_state/{shiprec.id}'),
#             await confirm_div(shiprec),
#             await back_div(shiprec.id),
#         ],
#         title='booking',
#         alert_dict=alert_dict,
#     )
#
#
# @router.get('/check_state/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
# async def check_shipment(
#         shiprec_id: int,
#         session=fastapi.Depends(am_db.get_session),
# ) -> list[c.AnyComponent]:
#     """Html Div with the current shipment of the shiprec.
#
#     Args:
#         shiprec_id (int): The BookingManger id.
#         session (sqm.Session, optional): The database session - defaults to fastapi.Depends(am_db.get_session).
#
#     Returns:
#         list(c.Div): A list containing a single DIV with each attribute of shipment as a text element.
#
#     """
#     shiprec = await support.get_shiprec(shiprec_id, session)
#     texts = builders.dict_strs_texts(
#         shiprec.shipment.model_dump(exclude={'candidates'}),
#         with_keys='YES'
#     )
#     match shiprec.shipment.direction:
#         case 'in':
#             dircol = 'success'
#         case 'out':
#             ...
#         case 'dropoff':
#             ...
#
#     cont_deets = c.Details(
#         data=shiprec.shipment,
#         fields=[
#             DisplayLookup(
#                 field='contact',
#                 mode=DisplayMode.json,
#
#             ),
#             DisplayLookup(
#                 field='address',
#                 mode=DisplayMode.json,
#             ),
#         ]
#
#     )
#     row_style = 'row mx-auto my-1'
#     nice_date = paw_strings.date_string(shiprec.shipment.ship_date)
#     ship_deets = [
#         c.Paragraph(text=f'SHIPPING ON:     {nice_date}', class_name=row_style),
#         c.Paragraph(text=f'BOXES:     {shiprec.shipment.boxes}', class_name=row_style),
#         c.Paragraph(text=f'DIRECTION:     {shiprec.shipment.direction}', class_name=row_style),
#         c.Paragraph(text=f'SERVICE:     {shiprec.shipment.service.name}', class_name=row_style),
#     ]
#     return [c.Div(
#         # components=builders.list_of_divs(class_name='row my-1 mx-auto', components=texts),
#         components=[cont_deets, *ship_deets],
#         class_name='row'
#     )]
#
#
# @router.get('/go_book/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
# async def do_booking(
#         shiprec_id: int,
#         el_client: ELClient = fastapi.Depends(am_db.get_el_client),
#         session: sqm.Session = fastapi.Depends(am_db.get_session),
# ) -> list[c.AnyComponent]:
#     """Endpoint for booking a shipment.
#
#     Args:
#         shiprec_id (int): The shiprec's id.
#         el_client (ELClient, optional): The shipper object - defaults to fastapi.Depends(amherst.am_db.get_pfc).
#         session (sqm.Session, optional): The database session - defaults to fastapi.Depends(amherst.am_db.get_session).
#
#     Returns:
#         - :meth:`~amherst.front.booked.booked_page`: Post-Booking Page on success.
#         - :meth:`~amherst.front.ship.shipping_page`: Shipping Page on failure, which may include alerts.
#
#     """
#     CoInitialize()
#
#     logger.warning(f'booking_id: {shiprec_id}')
#     shiprec = await support.get_shiprec(shiprec_id, session)
#
#     if shiprec.shipment.booking_state is not None:
#         logger.error(f'booking {shiprec_id} already booked')
#         alert_dict = {'ALREADY BOOKED': 'ERROR'}
#         return await booked.booked_page(manager=shiprec, alert_dict=alert_dict)
#
#     try:
#         if shiprec.shipment.direction == 'in':
#             tod = dt.date.today()
#             if shiprec.shipment.ship_date <= tod:
#                 raise ValueError('CAN NOT COLLECT TODAY')
#
#         req, resp = await book_shipment(shiprec, el_client)
#         processed_manager = await process_shipment(shiprec, el_client, req, resp)
#         # record_tracking(man_in)
#
#         session.add(processed_manager)
#         session.commit()
#         man_out = ShipmentRecordOut.model_validate(processed_manager)
#         return await booked.booked_page(manager=man_out)
#
#     except Exception as err:
#         alert_dict = {str(err): 'ERROR'}
#         man_out = ShipmentRecordOut.model_validate(shiprec)
#
#         return await ship.shipping_page(man_out.id, session=session, alert_dict=alert_dict)
#     finally:
#         CoUninitialize()
#
#
# async def book_shipment(manager: ShipmentRecordInDB, pfcom: ELClient):
#     """Book a shipment.
#
#     Args:
#         manager (shipment_record.ShipmentRecordDB): The :class:`~managers.MANAGER_IN_DB` object.
#         pfcom (ELClient): :class:`~ELClient` object.
#
#     Returns:
#         tuple: The request and response objects.
#
#     """
#     req = pfcom.shipment_to_request(manager.shipment)
#     logger.warning(f'BOOKING ({manager.shipment.direction.title()}) {manager.record.name}')
#     resp = pfcom.send_shipment_request(req)
#     return req, resp
#
#
# async def process_shipment(shiprec: ShipmentRecordDB, el_client: ELClient, req, resp):
#     """Process the shipment.
#
#     Update the shiprec with the booking shipment and wait for the label to download.
#     Open the label file in OS default pdf handler.
#
#     Args:
#         shiprec (shipment_record.ShipmentRecordDB): The shiprec object.
#         el_client (ELClient): :class:`~ELClient` object.
#         req: The request object.
#         resp: The response object.
#
#     Returns:
#         managers.ShipmentRecordDB: The shiprec object.
#
#     Raises:
#         shipaw.ExpressLinkError: If the shipment is not completed.
#
#     """
#     booked_state = ship_states.BookingState.model_validate(dict(request=req, response=resp))
#     if alt := booked_state.alerts:
#         raise shipaw.ExpressLinkError(str(alt))
#         # if not resp.completed_shipment_info:
#         # raise shipaw.ExpressLinkError(str(ship_states.response_alert_dict(resp)))
#
#     new_ship_state = shiprec.shipment.model_copy(update={'booking_state': booked_state})
#     val_ship_state = shipaw.Shipment.model_validate(new_ship_state)
#     await support.wait_label(val_ship_state, el_client)
#     os.startfile(val_ship_state.booking_state.label_dl_path)
#     shiprec.shipment = val_ship_state
#     return shiprec
#
#
# async def process_shipment2(shiprec: ShipmentRecordDB, el_client: ELClient, req, resp):
#     booked_state = ship_states.BookingState.model_validate(dict(request=req, response=resp))
#     if alt := booked_state.alerts:
#         raise shipaw.ExpressLinkError(str(alt))
#         # if not resp.completed_shipment_info:
#         # raise shipaw.ExpressLinkError(str(ship_states.response_alert_dict(resp)))
#
#     new_ship_state = shiprec.shipment.model_copy(update={'booking_state': booked_state})
#     val_ship_state = shipaw.Shipment.model_validate(new_ship_state)
#     await support.wait_label_decon(shipment_num='')
#     os.startfile(val_ship_state.booking_state.label_dl_path)
#     shiprec.shipment = val_ship_state
#     return shiprec
#
#
# async def back_div(manager_id: int):
#     """Back button."""
#     return c.Div(
#         class_name='row my-3',
#         components=[
#             c.Button(
#                 class_name='row btn btn-lg btn-primary',
#                 text='Back',
#                 on_click=events.GoToEvent(url=f'/ship/select/{manager_id}'),
#             )
#         ],
#     )
#
#
# async def confirm_div(manager):
#     """Confirm button."""
#     return c.Div(
#         class_name='row my-3',
#         components=[
#             c.Button(
#                 text='Confirm Booking',
#                 on_click=e.GoToEvent(url=f'/book/go_book/{manager.id}'),
#                 class_name='row btn btn-lg btn-primary',
#             )
#         ],
#     )
#
#
# # unused?
# # @router.post('/confirm_post/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
# # async def confirm_post(
# #         shiprec_id: int,
# #         form: _t.Annotated[
# #             ship_states.ShipmentPartial, fastui_form(ship_states.ShipmentPartial)],
# #         el_client: ELClient = fastapi.Depends(am_db.get_el_client),
# #         session=fastapi.Depends(am_db.get_session),
# #
# # ):
# #     """Endpoint for posting confirmation form."""
# #     update = ship_states.ShipmentPartial.model_validate(form.model_dump())
# #     if update.address.postcode:
# #         update.candidates = el_client.get_candidates(update.address.postcode)
# #     await support.update_and_commit(shiprec_id, update, session)
# #     return responses.RedirectResponse(url=f'/ship/select/{shiprec_id}')
#
#
# def record_tracking(man_in: ShipmentRecordInDB):
#     CoInitialize()
#
#     try:
#         tracking_number = man_in.shipment.booking_state.response.shipment_num
#         category = man_in.record.cmc_table_name
#         if category == 'Customer':
#             logger.error('CANT LOG TO CUSTOMER')
#             return
#         record_name = man_in.record.name
#         direction = man_in.shipment.direction
#         do_record_tracking(category, direction, record_name, tracking_number)
#
#     except Exception as exce:
#         logger.error(f'Failed to record tracking for {man_in.record.name} due to:\n{exce}')
#
#     finally:
#         CoUninitialize()
#
#
# def do_record_tracking(category, direction, record_name, tracking_number):
#     py_cmc = PyCommence.from_table_name(table_name=category)
#     tracking_link_field = 'Track Inbound' if direction == 'in' else 'Track Outbound'
#     pf_url = 'https://www.parcelforce.com/track-trace?trackNumber='
#     tracking_link = pf_url + tracking_number
#     py_cmc.edit_record(
#         record_name,
#         {tracking_link_field: tracking_link, 'DB label printed': True}
#     )
#     logger.info(
#         f'Updated "{record_name}" {tracking_link_field} to {tracking_link}'
#     )
