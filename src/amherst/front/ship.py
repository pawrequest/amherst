import fastapi
import sqlmodel
from fastapi import APIRouter, Depends
from fastui import FastUI, class_name as class_name_, components as c, events, events as e

from amherst.front import shared, support
from amherst import am_db
from amherst.models import managers
from pawdantic.pawui import builders, pawui_types
from shipr.ship_ui import forms as shipforms

router = APIRouter()


@router.get('/{kind}/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def shipping_page(
        manager_id: int,
        kind: support.FormKind = 'select',
        session: sqlmodel.Session = fastapi.Depends(am_db.get_session),
        alert_dict: pawui_types.AlertDict | None = None,
) -> support.Fui_Page:
    """Endpoint for shipping page.
    
    Presents form for user input, prepopulated from commence data.
    Can provide 'select' or 'manual' form, i.e. choose an address from those at the postcode, or override with manual entry.

    Args:
        manager_id: Booking Manager ID
        kind: Which input form to use
        session: sqlmodel session
        alert_dict: Alert dictionary

    Returns:
        FastUI page (support.Fui_Page): FastUI page

    """

    manager = await support.get_manager(manager_id, session)
    if send_method_column := getattr(manager.item.fields_enum, 'SEND_METHOD', None):
        if sm := manager.item.record.get(send_method_column):
            if 'parcelforce' not in sm.lower():
                alert = {'Commence Send Method not include "parcelforce"': 'WARNING'}
                alert_dict = alert | alert_dict if alert_dict else alert
    return await builders.page_w_alerts(
        alert_dict=alert_dict,
        components=[
            await left_col(manager),
            c.Div(
                class_name='col',
                components=[await form_div(kind, manager, session)]
            )
        ],
        title='Forms',
    )


async def left_col(manager: managers.MANAGER_IN_DB) -> c.Div:
    """Left column of shipping page.
    Displays:
        - data direct from commence for cross-reference
        - options to send email to customer with invoice or missing kit query
    
    Args:
        manager: Booking Manager
        
    Returns:
        c.Div: Left column div
    """
    return c.Div(
        class_name='col col-4 mx-auto',
        components=[
            await input_address_div(manager),
            await shared.email_div(manager, ['invoice', 'missing_kit']),
            # await address_from_pc_div(manager),
        ],
    )


async def form_div(kind: support.FormKind, manager, session) -> c.Div:
    """ Load prepopulated form.
    
    Args:
        kind: Form kind - 'manual' or 'select'
        manager: Booking Manager
        session: sqlmodel session
        
    Returns:
        c.Div: Div with form and button to switch form kind
        
    """
    match kind:
        case 'manual':
            button_text = 'Choose Address From Postcode'
            other_kind = 'select'
        case 'select':
            button_text = 'Manual Address Override'
            other_kind = 'manual'
        case _:
            raise ValueError(f'Invalid kind {kind!r}')
    return builders.wrap_divs(
        class_name='col col-8 mx-auto',
        inner_class_name='row my-3',
        components=[
            await server_load_form(kind, manager, session),
            await go_to_ship_button(button_text, other_kind, manager.id),
        ]
    )


async def go_to_ship_button(button_text, other_kind, manager_id: int):
    return c.Button(
        class_name='col col-4 my-3 btn btn-primary',
        text=button_text,
        on_click=events.GoToEvent(url=f'/ship/{other_kind}/{manager_id}'),
    )


async def server_load_form(kind, manager, session):
    return c.ServerLoad(
        path=f'/forms/get_form/{manager.id}/{kind}',
        load_trigger=e.PageEvent(name='change-form'),
        components=[await get_form(manager.id, kind, session)],
    )


@router.get(
    '/get_form/{manager_id}/{kind}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def get_form(
        manager_id: int,
        kind: support.FormKind,
        session=Depends(am_db.get_session)
) -> c.Form:
    """Endpoint to get form for shipping page.
    
    Args:
        manager_id: Booking Manager ID
        kind: Form kind
        session: sqlmodel session
        
    Returns:
        c.Form:
    
    """
    manager = await support.get_manager(manager_id, session)
    match kind:
        case 'manual':
            form_fields = await shipforms.ship_fields_manual(manager.state)
            submit_url = f'/api/forms/manual/{manager_id}'
        case 'select':
            form_fields = await shipforms.ship_fields_select(manager.state)
            submit_url = f'/api/forms/select/{manager_id}'
        case _:
            raise ValueError(f'Invalid kind {kind!r}')

    return c.Form(
        form_fields=form_fields,
        submit_url=submit_url,
    )


async def input_address_div(
        manager,
        class_name: class_name_.ClassName = 'row',
        inner_class_name: class_name_.ClassName = 'row'
) -> c.Div:
    """Div for displaying commence data.
    
    Args:
        manager: Booking Manager
        class_name: Outer div class name
        inner_class_name: 
        
    Returns:
        c.Div: Div with commence data
        
    """
    return c.Div(
        class_name=class_name,
        components=[
            *builders.list_of_divs(
                class_name=inner_class_name,
                components=[
                    *builders.dict_strs_texts(manager.item.contact.model_dump(), title='Contact'),
                    *builders.dict_strs_texts(
                        manager.item.input_address.model_dump(),
                        title='Address'
                    ),
                ],
            ),
        ],
    )


async def address_from_pc_div(manager) -> c.Div:
    """Div for selecting address from postcode.
    
    Args:
        manager: Booking Manager
        
    Returns:
        c.Div: Div with form for selecting address from postcode

    """
    return c.Div(
        components=[
            c.Form(
                form_fields=[
                    c.FormFieldInput(
                        name='postcode',
                        title='Postcode to Get Addresses',
                    ),
                ],
                submit_url=f'/api/forms/postcode2/{manager.id}',
            ),
        ],
        class_name='row mx-auto my-3',
    )

# @router.get(
#     '/update/{booking_id}/{update_64}',
#     response_model=fastui.FastUI,
#     response_model_exclude_none=True
# )
# async def update_shipment(
#         booking_id: int,
#         update_64: str | None = None,
#         session: sqlmodel.Session = Depends(am_db.get_session),
# ) -> support.Fui_Page:
#     """Endpoint for updating shipment.
#
#     Args:
#         booking_id: Booking Manager ID
#         update_64: BookingManagerState as base64 encoded json
#         session: sqlmodel session
#
#     Returns:
#         FastUI page
#     """
#     logger.info(f'UPDATE_SHIPMENT {booking_id=}, {update_64=}')
#     updt = states.ShipStatePartial.model_validate_64(update_64)
#     man_out = await support.update_and_commit(booking_id, updt, session)
#     return await shipping_page(manager=man_out)
