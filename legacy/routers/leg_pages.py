
# async def booking_div(
#         manager: managers.BookingManagerOut,
#         direction: _t.Literal['in', 'out'],
#         class_name='row'
# ) -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text=f'Ship {direction.title()}Bound',
#                 on_click=e.PageEvent(name=f'ship-{direction}'),
#                 class_name=amherst.front.am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title=f'Confirm {direction.title()}bound Shipping',
#                 body=[
#                     c.Button(
#                         text=f'Book {direction.title()}Bound',
#                         on_click=e.GoToEvent(
#                             url=f'/book/go_book/{direction}/{manager.id}',
#                         ),
#                         class_name=amherst.front.am_styles.BUTTON,
#                     ),
#                     c.ServerLoad(path=f'/sl/check_state/{manager.id}')
#                 ],
#                 footer=[
#                     c.Button(
#                         text='Close',
#                         on_click=e.PageEvent(name=f'ship-{direction}', clear=True)
#                     ),
#                 ],
#                 open_trigger=e.PageEvent(name=f'ship-{direction}'),
#             ),
#         ],
#         class_name=class_name,
#     )


#####
####
####

# async def boxes_modal_row(manager: managers.MANAGER_IN_DB) -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text=f'{manager.state.boxes} Boxes',
#                 on_click=e.PageEvent(name='manual-entry'),
#                 class_name=amherst.front.am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title='Manual Address and Contact Entry',
#                 body=await boxes_chooser_button_rows(),
#                 footer=[
#                     c.Button(text='Close', on_click=e.PageEvent(name='manual-entry', clear=True)),
#                 ],
#                 open_trigger=e.PageEvent(name='manual-entry'),
#             ),
#         ],
#         class_name=styles.ROW_STYLE,
#     )
#
#
# async def boxes_enum_select(manager_id):
#     return c.Div(
#         components=[
#             c.ModelForm(
#                 model=dynamic.BoxesModelForm,
#                 submit_url=f'/api/forms/boxes/{manager_id}',
#
#             )
#         ],
#     )
#
#


#
# async def manual_entry_modal(manager: managers.MANAGER_IN_DB) -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text='Manual Entry',
#                 on_click=e.PageEvent(name='manual-entry'),
#                 class_name=amherst.front.am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title='Manual Entry',
#                 body=[
#                     c.ModelForm(
#                         model=ship_forms.AddressForm,
#                         initial=manager.state.address.model_dump(),
#                         submit_url=f'/api/forms/address/{manager.id}',
#                     ),
#                 ],
#                 footer=[
#                     c.Button(text='Close', on_click=e.PageEvent(name='manual-entry', clear=True)),
#                 ],
#                 open_trigger=e.PageEvent(name='manual-entry'),
#             ),
#         ],
#         class_name=styles.ROW_STYLE,
#     )

# class DateEnum(str, Enum):
#     TODAY = datetime.date.today()
#


# return c.ServerLoad(path=f'/sl/booking_form/{manager.id}')


# async def right_col(manager):
#     return c.Div(
#         components=[
#             c.ModelForm(
#                 model=ship_forms.ContactAndAddressForm,
#                 initial=paw_types.multi_model_dump(
#                     manager.state.contact,
#                     manager.state.address,
#                 ),
#                 submit_url=f'/api/forms/address_contact/{manager.id}',
#                 class_name='row h6',
#                 submit_on_change=True,
#             ),
#         ],
#         class_name='col',
#     )

#
# async def right_col2(manager):
#     return c.Div(
#         components=[
#             c.ModelForm(
#                 model=ship_forms.FullForm,
#                 initial={
#                     'boxes': manager.state.boxes,
#                     'ship_date': manager.state.ship_date,
#                     'direction': manager.state.direction,
#                     **paw_types.multi_model_dump(
#                         manager.state.contact,
#                         manager.state.address,
#                     )
#                 },
#                 submit_url=f'/api/forms/big/{manager.id}',
#                 class_name='row h6',
#                 submit_on_change=True,
#             ),
#         ],
#         class_name='col',
#     )

# async def boxes_form(manager):
#     return c.Form(
#         form_fields=[
#             c.FormFieldSelect(
#                 name='boxes',
#                 title='Boxes',
#                 required=True,
#                 options=[
#                     fastui_forms.SelectOption(value=str(i), label=str(i))
#                     for i in range(1, 11)
#                 ],
#                 initial=str(manager.state.boxes),
#             ),
#         ],
#         submit_url=f'/api/forms/boxes/{manager.id}',
#         submit_on_change=True,
#
#     )