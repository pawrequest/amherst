"""Pages and Enpoints for Post-Booking Actions."""
from __future__ import annotations

import fastapi
from fastui import FastUI, components as c, events as e
from fastui.components.display import DisplayLookup, DisplayMode
from loguru import logger
from pawdantic.pawui import builders
from shipaw.ship_ui.shipment_states import response_alert_dict

from amherst import am_db
from amherst.front import shared, support
from amherst.front.support import prnt_label_arrayed
from amherst.models.shipment_record import ShipmentRecordInDB

from shipaw import BookingState
router = fastapi.APIRouter()


# noinspection DuplicatedCode
async def booked_page(shiprec: ShipmentRecordInDB, alert_dict=None) -> list[c.AnyComponent]:
    """Page for post-booking actions including printing and emailing labels.

    Args:
        shiprec: The shiprec object.
        alert_dict: Dictionary of alerts.

    Returns:
        FastUI.Page: The page with the post-booking actions.

    """
    shipment_alert_dict = response_alert_dict(shiprec.booking_state.response)
    alert_dict = shipment_alert_dict.update(alert_dict or {})
    # nice_date = paw_strings.date_string(shiprec.shipment.ship_date)

    ret = await builders.page_w_alerts(
        components=[
            c.Heading(
                text=f"Shipment Booked for {shiprec.record.name}",
                level=1,
                class_name="row mx-auto my-5"
            ),
            await print_div(shiprec),
            await shared.invoice_div(shiprec),
            await shared.email_div(shiprec, ["invoice", "label"]),
            await shared.close_div(),
            await booked_state_details(shiprec),
        ],
        title="Shipment Booked",
        alert_dict=alert_dict,
    )
    return ret


async def booked_state_details(shiprec):
    return c.Details(
        data=shiprec.booking_state,
        fields=[
            DisplayLookup(
                field='request',
                mode=DisplayMode.json,

            ),
            DisplayLookup(
                field='response',
                mode=DisplayMode.json,
            ),
        ]

    )


async def print_div(shiprec):
    """Html Div with button to print labels."""
    return c.Div(
        class_name="row my-3",
        components=[
            c.Button(
                text=rf"Array and Re/Print Labels for {shiprec.record.name}",
                on_click=e.GoToEvent(
                    url=f"/booked/print/{shiprec.id}",
                ),
                class_name="btn btn-lg btn-primary",
            )
        ],
    )


@router.get("/print/{shiprec_id}", response_model=FastUI, response_model_exclude_none=True)
async def print_label(shiprec_id: int, session=fastapi.Depends(am_db.get_session)):
    """Endpoint to print the label for a booking."""
    logger.warning(f"printing id: {shiprec_id}")
    shiprec = await support.get_shiprec(shiprec_id, session)
    if label := shiprec.booking_state.label_dl_path:
        await prnt_label_arrayed(label)
        return await booked_page(shiprec=shiprec)
    raise ValueError("label not downloaded")
