from __future__ import annotations, annotations

import time
import typing as _t
import pathlib

import fastapi
import pawdf
from fastui import components as c
from loguru import logger
import sqlmodel as sqm

from amherst.models.am_record import AmherstRecord
from amherst.models.shipment_record import ShipmentRecordDB, ShipmentRecordOut
from shipaw.models import pf_ext, pf_shared
import shipaw
from shipaw import ELClient, pf_config
from shipaw.ship_ui import states

type Fui_Page = list[c.AnyComponent]
type EmailChoices = _t.Literal['invoice', 'label', 'missing_kit']


async def get_manager(manager_id: int, session: sqm.Session) -> ShipmentRecordDB:
    man_in = session.get(ShipmentRecordDB, manager_id)
    if not isinstance(man_in, ShipmentRecordDB):
        raise fastapi.HTTPException(status_code=404, detail='Booking not found')

    return man_in


async def update_state(man_in, updt):
    updated_state_ = man_in.shipment.get_updated(updt)
    updated_state = shipaw.Shipment.model_validate(updated_state_)
    man_in.shipment = updated_state
    return man_in


async def update_and_commit(manager_id, partial, session) -> ShipmentRecordOut:
    man_in = await get_manager(manager_id, session)
    updated_state_ = man_in.shipment.get_updated(partial)
    updated_state = shipaw.Shipment.model_validate(updated_state_)
    man_in.shipment = updated_state
    session.add(man_in)
    session.commit()
    man_out = ShipmentRecordOut.model_validate(man_in)

    return man_out


async def wait_label(state: shipaw.Shipment, el_client: ELClient) -> bool:
    label_path = el_client.get_label(
        ship_num=state.booking_state.shipment_num(),
        dl_path=state.named_label_path if state.direction == 'in' else None,
    ).resolve()

    for i in range(20):
        if label_path:
            state.booking_state.label_downloaded = True
            state.booking_state.label_dl_path = label_path
            return True
        else:
            print('waiting for file to be created')
            time.sleep(1)
    else:
        raise ValueError(f'file not created after 20 seconds {label_path=}')


async def get_invoice_path(record: AmherstRecord) -> pathlib.Path | None:
    if record.cmc_table_name == 'Customer':
        raise ValueError('invoice not for customer')

    return record.invoice


async def get_missing(record: AmherstRecord) -> list[str]:
    if not record.cmc_table_name == 'Hire':
        raise ValueError('missing kit only for hire')
    return record.missing_kit


def get_named_labelpath(state: shipaw.Shipment):
    """Get a unique path (for saving) for the label."""
    sett = pf_config.PF_SETTINGS
    pdir = sett.label_dir
    label_name = f'Parcelforce Collection Label for {state.contact.business_name} on {state.ship_date}'
    return pdir / f'{label_name}.pdf'


async def prnt_label_arrayed(label_path: pathlib.Path) -> None:
    """Print the labels. Arrays A6 Labels 2 to a A4 page.
    Uses pawdf.array_pdf.convert_many to print the labels.

    Args:
        label_path: The path to the label.

    """

    if not label_path.exists():
        logger.error(f'label_path {label_path} does not exist')

    pawdf.array_pdf.convert_many(label_path, print_files=True)


def state_notification_labels_str(state: states.Shipment):
    indent = ' ' * 4
    lines = [
        f'{indent}{pf_shared.notification_label_map[notification]} - {state_notification_contact_detail(state, notification)}'
        for notification in state.contact.notifications.notification_type
    ]
    return '\n'.join(lines)


def state_notification_contact_detail(state: states.Shipment, notification: str):
    if 'EMAIL' in notification or notification == 'DELIVERYNOTIFICATION':
        return state.contact.email_address
    elif 'SMS' in notification:
        return state.contact.mobile_phone
    else:
        raise ValueError('Invalid notification type')


async def get_manager_label_path(man_in):
    return man_in.shipment.booking_state.label_dl_path


async def update_manager_state(manager_id, session, state):
    man_in = await get_manager(manager_id, session)
    man_in.shipment = state
    session.add(man_in)
    session.commit()
    session.refresh(man_in)
    return man_in


async def addr_class_f_direction(direction):
    return pf_ext.AddressRecipient if direction == 'out' else pf_ext.AddressCollection
