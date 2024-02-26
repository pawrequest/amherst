# from __future__ import annotations, annotations
#
# import datetime
#
# from fastui.events import GoToEvent, PageEvent
# from fastui import components as c
#
# from pawsupport.fastui_ps import fui
# from shipr.express.types import AddressChoice
# from . import amui, css
# from .amui import address_col, date_string
# from .controller_abc import UIBase
#
#
# class HireUI(UIBase):
#
#     async def get_page(self) -> list[c.AnyComponent]:
#         return amui.Page.default_page(
#             fui.Container.wrap(
#                 await self.address_section(),
#                 await self.details_section()
#             ),
#             title="Hire Shipping"
#         )
#
#     async def address_section(self):
#         async def amherst_address_col():
#             return amui.Col.wrap(
#                 fui.Text(text=self.state.contact.business_name),
#                 *await address_col(self.state.input_address),
#                 wrap_inner=amui.Row
#             )
#
#         async def address_buttons_div(outer_wrap=amui.Col, wrap_inner=amui.Row):
#             return outer_wrap.wrap(
#                 fui.Text(text=f'Address score: {self.state.address_choice.score}'),
#                 c.Button(text="Choose this address"),
#                 c.Button(text="Enter address manually", on_click=None),
#                 c.Button(
#                     text='Choose a Different Address',
#                     on_click=PageEvent(name='address-chooser')
#                 ),
#                 await self.address_chooser_modal(),
#                 wrap_inner=wrap_inner,
#             )
#
#         return amui.Row(
#             components=[
#                 await amherst_address_col(),
#                 await address_buttons_div(),
#                 await address_col(self.state.address_choice.address, wrap_in=amui.Col)
#             ]
#         )
#
#     async def details_section(self):
#         async def boxes_btn():
#             num_b = self.state.boxes
#             return [c.Button(
#                 text=f'{num_b} Boxes',
#                 on_click=PageEvent(name='boxes-chooser'),
#                 class_name=css.BOXES_BTN
#             ),
#                 await self.boxes_modal()
#             ]
#
#         async def date_btn():
#             date_ = self.state.ship_date
#             text = await date_string(date_)
#             return [c.Button(
#                 text=text,
#                 on_click=PageEvent(
#                     name='date-chooser',
#                     context={'oc': 'date'}
#                 ),
#             ),
#                 await self.date_modal()
#             ]
#
#         async def request_btn():
#             return [c.Button(
#                 text="Request Shipping",
#                 on_click=GoToEvent(
#                     url='/book/',
#                     query={'state': self.state.model_dump_json()}
#                 ),
#             )]
#
#         return amui.Row.wrap(
#             *await date_btn(),
#             *await boxes_btn(),
#             *await request_btn(),
#             # wrap_inner=amui.Col
#         )
#
#     async def address_chooser_modal(self) -> c.Modal:
#         return c.Modal(
#             title='Address Modal',
#             body=await self.address_chooser_buttons(),
#             footer=[
#                 c.Button(text='Close', on_click=PageEvent(name='address-chooser', clear=True)),
#             ],
#             open_trigger=PageEvent(name='address-chooser'),
#         )
#
#     async def boxes_modal(self) -> c.Modal:
#         return c.Modal(
#             title='Number of Boxes',
#             body=await self.boxes_chooser_buttons(),
#             footer=[
#                 c.Button(text='Close', on_click=PageEvent(name='boxes-chooser', clear=True)),
#             ],
#             open_trigger=PageEvent(name='boxes-chooser'),
#             open_context={'oc': 'boxes'}
#         )
#
#     async def date_modal(self) -> c.Modal:
#         return c.Modal(
#             title='Date',
#             body=await self.date_chooser_buttons(),
#             footer=[
#                 c.Button(text='Close', on_click=PageEvent(name='date-chooser', clear=True)),
#             ],
#             open_trigger=PageEvent(name='date-chooser'),
#         )
#
#     async def address_chooser_buttons(self) -> list[c.AnyComponent]:
#         ret = [
#             c.Button(
#                 text=can.address_line1,
#
#                 on_click=GoToEvent(
#                     url=f'/hire/id2/{self.state.hire_id}',
#                     query={
#                         'state': self.state.update(
#                             address_choice=AddressChoice(address=can, score=100)
#                         ).model_dump_json()
#                     }
#                 )
#             )
#             for can in self.state.candidates
#         ]
#         return ret
#
#     async def boxes_chooser_buttons(self) -> list[c.AnyComponent]:
#         return [c.Button(
#             text=str(i),
#             on_click=GoToEvent(
#                 url=f'/hire/id2/{self.state.hire_id}',
#                 query={'state': self.state.update(boxes=i).model_dump_json()}
#             )
#         ) for i in range(1, 11)
#         ]
#
#     async def date_chooser_buttons(self) -> list[c.AnyComponent]:
#         start_date = datetime.date.today()
#         date_range = [start_date + datetime.timedelta(days=x) for x in
#                       range(7)]
#         weekday_dates = [d for d in date_range if d.weekday() < 5]  # 0-4 are weekdays
#
#         return [c.Button(
#             text=await date_string(ship_date),
#             on_click=GoToEvent(
#                 url=f'/hire/id2/{self.state.hire_id}',
#                 query={'state': self.state.update(ship_date=ship_date).model_dump_json()}
#             )
#         ) for ship_date in weekday_dates
#         ]
