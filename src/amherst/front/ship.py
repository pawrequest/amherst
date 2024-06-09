import fastapi
import sqlmodel
from fastapi import APIRouter, Depends
from fastui import FastUI, class_name as class_name_, components as c
from fastui.events import GoToEvent, PageEvent
from pawdantic.pawui import builders, pawui_types

from shipaw import ELClient, pf_config, ship_types
from shipaw.ship_ui.forms import get_form_fields
from amherst.models.shipment_record import ShipmentRecordDB
from amherst.front import shared, support
from amherst import am_db

router = APIRouter()


@router.get('/{formkind}/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
async def shipping_page(
    shiprec_id: int,
    formkind: ship_types.FormKind = 'select',
    session: sqlmodel.Session = fastapi.Depends(am_db.get_session),
    alert_dict: pawui_types.AlertDict | None = None,
) -> support.Fui_Page:
    """Endpoint for shipping page.

    Presents form for user input, prepopulated from commence data.
    Can provide 'select' or 'manual' form, i.e. choose an address from those at the postcode, or override with manual entry.

    Args:
        shiprec_id: Booking shiprec ID
        formkind: Which input form to use
        session: sqlmodel session
        alert_dict: Alert dictionary

    Returns:
        FastUI page (support.Fui_Page): FastUI page

    """
    pf_sett = pf_config.pf_sett()

    bg_col = ' bg-light' if pf_sett.ship_live else ' bg-warning'
    page_style = f'container{bg_col}'

    shiprec = await support.get_shiprec(shiprec_id, session)
    if 'parcelforce' not in shiprec.record.send_method.lower():
        alert = {'Commence Send Method not include "parcelforce"': 'WARNING'}
        alert_dict = alert | alert_dict if alert_dict else alert
    return await builders.page_w_alerts(
        page_class_name=page_style,
        alert_dict=alert_dict,
        components=[
            await left_col(shiprec),
            c.Div(class_name='col', components=[await form_div(formkind, shiprec.id, session)]),
        ],
        title='Forms',
    )


async def jinji_div(shiprec_id: int) -> c.Div:
    return c.Div(
        components=[
            c.Button(
                text='Jinji',
                on_click=GoToEvent(url=f'/jinji/manual/{shiprec_id}'),
            ),
        ],
        class_name='row mx-auto',
    )


async def left_col(shiprec: ShipmentRecordDB) -> c.Div:
    """Left column of shipping page.
    Displays:
        - data direct from commence for cross-reference
        - options to send email to customer with invoice or missing kit query

    Args:
        shiprec: Booking shiprec

    Returns:
        c.Div: Left column div
    """
    return c.Div(
        class_name='col col-4 mx-auto',
        components=[
            await address_from_cmc_div(shiprec),
            await shared.email_div(shiprec, ['invoice', 'missing_kit']),
            await shared.close_div(),
            await address_from_pc_div(shiprec.id),
        ],
    )


async def form_div(formkind: ship_types.FormKind, shiprec_id: int, session) -> c.Div:
    """Load prepopulated form.

    Args:
        formkind: Form kind - 'manual' or 'select'
        shiprec_id: Booking shiprec ID
        session: sqlmodel session

    Returns:
        c.Div: Div with form and button to switch form kind

    """

    return builders.wrap_divs(
        class_name='col col-8 mx-auto mb-5',
        inner_class_name='row my-1',
        components=[
            # await jinji_div(shiprec_id),
            await go_to_other_form(formkind, shiprec_id),
            await get_form(shiprec_id, formkind, session),
            # c.ServerLoad(
            #     path=f'/forms/get_form/{formkind}/{shiprec_id}',
            #     load_trigger=PageEvent(name='change-form'),
            #     components=[await get_form(shiprec_id, formkind, session)],
            # ),
        ],
    )


async def swapform_button(shiprec_id: int):
    return c.Button(
        text='Swap Form',
        on_click=PageEvent(
            name='change-form',
            context={'formkind': 'manual', 'shiprec_id': shiprec_id},
        ),
    )


async def go_to_other_form(kind, shiprec_id: int):
    match kind:
        case 'manual':
            other_kind = 'select'
            button_text = 'Choose Address From Postcode'
        case 'select':
            other_kind = 'manual'
            button_text = 'Manual Address Override'
        case _:
            raise ValueError(f'Invalid kind {kind!r}')

    return c.Button(
        class_name='my-2 btn btn-primary',
        text=button_text,
        on_click=GoToEvent(url=f'/ship/{other_kind}/{shiprec_id}'),
    )


# async def server_load_form(kind, shiprec, session):
#     return c.ServerLoad(
#         path=f"/forms/get_form/{shiprec.id}/{kind}",
#         load_trigger=e.PageEvent(name="change-form"),
#         components=[await get_form(shiprec.id, kind, session)],
#     )


@router.get('/get_form/{formkind}/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
async def get_form(
    shiprec_id: int,
    formkind: ship_types.FormKind,
    session=Depends(am_db.get_session),
) -> c.Form:
    """Endpoint to get form for shipping page.

    Args:
        shiprec_id: Booking shiprec ID
        formkind: Form kind
        session: sqlmodel session

    Returns:
        c.Form:

    """
    expresslink = ELClient()
    shiprec = await support.get_shiprec(shiprec_id, session)
    candidates = expresslink.get_candidates(shiprec.shipment.address.postcode)
    return c.Form(
        form_fields=await get_form_fields(formkind, shiprec.shipment, candidates),
        submit_url=f'/api/forms/{formkind}/{shiprec_id}',
        # class_name='row mx-auto',
    )


async def address_from_cmc_div(
    shiprec, class_name: class_name_.ClassName = 'row', inner_class_name: class_name_.ClassName = 'row'
) -> c.Div:
    """Div for displaying commence data.

    Args:
        shiprec: Booking shiprec
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
                    *builders.dict_strs_texts(shiprec.record.contact.model_dump(), title='Contact'),
                    *builders.dict_strs_texts(shiprec.record.input_address.model_dump(), title='Address'),
                ],
            ),
        ],
    )


async def address_from_pc_div(shiprec_id) -> c.Div:
    """Div for selecting address from postcode.

    Args:
        shiprec_id: Booking shiprec

    Returns:
        c.Div: Div with form for selecting address from postcode

    """
    return c.Div(
        components=[
            c.Form(
                form_fields=[
                    c.FormFieldInput(
                        name='postcode',
                        title='New Postcode to Get Addresses',
                    ),
                ],
                submit_url=f'/api/forms/postcode/{shiprec_id}',
            ),
        ],
        class_name='row mx-auto my-3',
    )


# @router.get(
#     '/update/{shiprec_id}/{update_64}',
#     response_model=fastui.FastUI,
#     response_model_exclude_none=True
# )
# async def update_shipment(
#         shiprec_id: int,
#         update_64: str | None = None,
#         session: sqlmodel.Session = Depends(am_db.get_session),
# ) -> support.Fui_Page:
#     """Endpoint for updating shipment.
#
#     Args:
#         shiprec_id: Booking shiprec ID
#         update_64: BookingshiprecState as base64 encoded json
#         session: sqlmodel session
#
#     Returns:
#         FastUI page
#     """
#     logger.info(f'UPDATE_SHIPMENT {shiprec_id=}, {update_64=}')
#     updt = states.ShipmentPartial.model_validate_64(update_64)
#     man_out = await support.update_and_commit(shiprec_id, updt, session)
#     return await shipping_page(shiprec=man_out)
