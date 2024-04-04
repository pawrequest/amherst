# # from __future__ import annotations
# import os
#
# import fastapi
# import fastui
# from fastapi import APIRouter, Depends
# from fastui import FastUI, components as c, events
# from loguru import logger
# from sqlmodel import Session
#
# import amherst.routers.back_funcs
# from amherst import am_db
# from amherst.am_db import get_session
# from amherst.front.pages import shipping_page
# from amherst.models import am_shared, managers
# from amherst.routers import back_funcs
# from pawdantic import paw_types
# from pawdantic.pawui import builders
# from shipr.ship_ui import forms as ship_forms, states
#
# ACOUNTER = 0
# router = APIRouter()
#
#
# @router.get('/view/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def view_shipment(
#         manager_id: int,
#         session: Session = Depends(get_session),
# ) -> list[c.AnyComponent]:
#     logger.info(f'hire route: {manager_id}')
#     man_in = await amherst.routers.back_funcs.get_manager(manager_id, session)
#     man_out = managers.BookingManagerOut.model_validate(man_in)
#     if not man_in:
#         raise ValueError(f'manager id {manager_id} not found')
#     return await shipping_page.ship_page(manager=man_out)
#
#
# @router.get('/view_manual/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def view_shipment_manual(
#         manager_id: int,
#         session: Session = Depends(get_session),
#         manual: bool = False,
# ) -> list[c.AnyComponent]:
#     logger.info(f'hire route: {manager_id}')
#     man_in = await amherst.routers.back_funcs.get_manager(manager_id, session)
#     man_out = managers.BookingManagerOut.model_validate(man_in)
#     if not man_in:
#         raise ValueError(f'manager id {manager_id} not found')
#     return await shipping_page.ship_page(manager=man_out, manual_entry=manual)
#
#
# # @router.get('/open_hire_sheet/{manager_id}')
# # async def open_hire_sheet(
# #         manager_id: int,
# #         session: Session = Depends(get_session),
# # ):
# #     man_in = await get_manager(manager_id, session)
# #     hire_sheet = man_in.hire.record.get()
#
#
# @router.get('/invoice/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def open_invoice(
#         manager_id: int,
#         session: Session = Depends(get_session),
# ) -> list[c.AnyComponent]:
#     man_in = await amherst.routers.back_funcs.get_manager(manager_id, session)
#     man_out = managers.BookingManagerOut.model_validate(man_in)
#     inv_file = man_in.item.record.get(am_shared.HireFields.INVOICE)
#
#     try:
#         os.startfile(inv_file)
#     except (FileNotFoundError, TypeError):
#         logger.error(f'Invoice file not found: {inv_file}')
#         return await shipping_page.ship_page(
#             manager=man_out,
#             alert_dict={'INVOICE NOT FOUND': 'WARNING'}
#         )
#         # alert = pf_shared.Alert(code=11, message=f'Invoice file not found: {inv_file}', type='ERROR')
#
#     return [c.FireEvent(event=events.GoToEvent(url=f'/hire/view/{manager_id}'))]
#
#     # return await builders.page_w_alerts(
#     #     components=[`
#     #         c.Button(
#     #             text='Back',
#     #             # on_click=c.FireEvent(event=events.GoToEvent(url=f'/book/view/{manager_id}')),
#     #             on_click=events.GoToEvent(
#     #                 url=f'/hire/invoice/{manager_id}',
#     #             ),
#     #         )
#     #     ],
#     #     title='back',
#     # )
#
#     # return c.FireEvent(event=events.GoToEvent(url=f'/book/view/{manager_id}'))
#
#
# @router.get(
#     '/update/{booking_id}/{update_64}',
#     response_model=fastui.FastUI,
#     response_model_exclude_none=True
# )
# async def update_shipment(
#         booking_id: int,
#         update_64: str | None = None,
#         session: Session = Depends(get_session),
# ) -> list[c.AnyComponent]:
#     updt = states.ShipStatePartial.model_validate_64(update_64)
#     # man_in = await back_funcs.get_manager(booking_id, session)
#     man_out = await back_funcs.update_and_commit(booking_id, updt, session)
#     # man_in_upd = await back_funcs.update_state(man_in, updt)
#     # session.add(man_in)
#     # session.commit()
#     return await shipping_page.ship_page(manager=man_out)
#
#     # return [c.Text(text="Booking not found")]
#
#
# @router.get('/view/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def clickme_div(
#         manager_id: int,
#         session=fastapi.Depends(am_db.get_session)
# ) -> list[c.AnyComponent]:
#     manager = await back_funcs.get_manager(manager_id, session)
#     return await builders.page_w_alerts(
#         components=[
#             c.Link(
#                 components=[c.Text(text='click me')],
#
#                 # on_click=e.PageEvent(name='clickme', context={'manager': manager.model_dump_json()}),
#                 on_click=events.PageEvent(
#                     name='clickme',
#                     push_path=f'/ship/view/{manager_id}',
#                     context={'manager': manager.id},
#                 ),
#
#             ),
#             c.ServerLoad(
#                 path=f'/ship/clickme/content/{manager.model_dump_json()}',
#                 load_trigger=events.PageEvent(name='clickme'),
#                 components=await clickme_content(manager.model_dump_json()),
#
#             ),
#         ],
#     )
#
#
# async def add_butts(manager):
#     return [
#         c.Div(
#             class_name='row my-2',
#             components=[
#                 c.Button(
#                     text=can.address_line1,
#                     on_click=events.PageEvent(
#                         name='clickme',
#                         push_path=f'/ship/view/{manager.id}',
#                         context={'manager_id': manager.id},
#                     ),
#                 )
#             ],
#         )
#         for can in manager.state.candidates
#     ]
#
#
# @router.get(
#     '/clickme/content/{manager_json}',
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def clickme_content(
#         manager_json: str,
# ) -> list[c.AnyComponent]:
#     manager = managers.BookingManagerOut.model_validate_json(manager_json)
#     logger.warning('clickme_content')
#     contact = manager.state.contact
#     return [
#         c.Heading(text='cliiiick me', level=2),
#         c.Paragraph(text='clickem'),
#         *await add_butts(manager),
#         c.ModelForm(
#             model=ship_forms.FullForm,
#             submit_url=f'/api/forms/full/{manager.id}',
#             initial={
#                 'ship_date': manager.state.ship_date,
#                 'boxes': manager.state.boxes,
#                 'direction': manager.state.direction,
#                 **paw_types.multi_model_dump(
#                     contact,
#                     manager.state.address,
#                 )
#             },
#         ),
#         # c.Form(
#         #     form_fields=await ship_forms.big_form_fields(manager.state),
#         #     submit_url=f'/api/forms/big/{manager.id}',
#         #
#         # )
#     ]
#
# #
# # @router.get('/new/{hire_name}')
# # async def hire_from_cmc_name_64(
# #         hire_name: str,
# #         session=Depends(get_session),
# #         # cursor: Csr = Depends(get_hire_cursor),
# #         pfcom: shipper.AmShipper = Depends(am_db.get_pfc),
# # ):
# #     hire_name = base64.urlsafe_b64decode(hire_name).decode()
# #     logger.info(f'hire_name: {hire_name}')
# #     with csr_context('Hire') as cursor:
# #         hire_record = cursor.get_record(hire_name)
# #
# #     added = rec_importer.records_to_managers(hire_record, session=session, pfcom=pfcom)[0]
# #
# #     # hire = hire_record_to_session(hire_record, session, pfcom)
# #     return [c.FireEvent(event=events.GoToEvent(url=f'/hire/view/{added.id}'))]
# #
# #
# # @router.get('/new/{category}/{record}')
# # async def from_deets(
# #         category: str,
# #         record: str,
# # ):
# #
# #     with pycommence.api.csr_context(category) as csr:
# #         record_ = csr.record_by_name(record)
# #         prep_db(category, record_)
# #
# #     return [c.FireEvent(event=events.GoToEvent(url=f'/hire/view/{added.id}'))]
#
# # def hire_record_to_session(record: dict, session: sqm.Session, pfcom) -> managers.BookingManagerDB:
# #     """Create a new hire and state in the database from a record dict."""
# #     hire_ = hire_model.Hire(record=record)
# #     ship = hire_model.ShipableItem.model_validate(hire_)
# #     state = shipr.ShipState.hire_initial(hire_, pfcom)
# #     manager = managers.BookingManagerDB(item=ship, state=state)
# #     manager = manager.model_validate(manager)
# #     session.add(manager)
# #     session.commit()
# #     session.refresh(manager)
# #     return manager
