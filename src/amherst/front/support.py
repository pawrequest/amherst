from __future__ import annotations

import pathlib
import time
import typing as _t

import fastapi
import pdf_tools
import sqlmodel as sqm
from fastui import components as c
from loguru import logger

import shipr
from amherst import am_config, shipper
from amherst.models import am_shared, managers
from amherst.models.shipable_item import ShipableItem
from shipr.models import pf_shared
from shipr.ship_ui import states


class ManagerNotFound(Exception):
    pass


async def get_manager(manager_id: int, session: sqm.Session):
    man_in = session.get(managers.BookingManagerDB, manager_id)
    if not isinstance(man_in, managers.BookingManagerDB):
        raise fastapi.HTTPException(status_code=404, detail='Booking not found')

    return man_in


async def update_state(man_in, updt):
    updated_state_ = man_in.state.get_updated(updt)
    updated_state = shipr.ShipState.model_validate(updated_state_)
    man_in.state = updated_state
    return man_in


async def update_and_commit(manager_id, partial, session) -> managers.BookingManagerOut:
    man_in = await get_manager(manager_id, session)
    updated_state_ = man_in.state.get_updated(partial)
    updated_state = shipr.ShipState.model_validate(updated_state_)
    man_in.state = updated_state
    session.add(man_in)
    session.commit()
    man_out = managers.BookingManagerOut.model_validate(man_in)

    return man_out


async def wait_label(state: shipr.ShipState, pfcom: shipper.AmShipper) -> bool:
    label_path = pfcom.get_label(
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


async def get_invoice_path(item: ShipableItem):
    if item.cmc_table_name == 'Customer':
        raise ValueError('invoice not for customer')
    return item.record.get(item.fields_enum.INVOICE)


async def invoice_num_f_path(invoice_path: pathlib.Path):
    return str(invoice_path).split('\\')[-1].split('.')[0]


async def get_missing(item: ShipableItem) -> list[str]:
    if not item.cmc_table_name == 'Hire':
        raise ValueError('missing kit only for hire')
    return item.record.get(am_shared.HireFields.MISSING_KIT).splitlines()


FormKind: _t.TypeAlias = _t.Literal['manual', 'select']  # noqa: UP040 fastui not support
type Fui_Page = list[c.AnyComponent]


def get_named_labelpath(state: shipr.ShipState):
    """Get a unique path (for saving) for the label."""
    sett = am_config.AmSettings()
    pdir = sett.parcelforce_labels_dir
    label_name = f'Parcelforce Collection Label for {state.contact.business_name} on {state.ship_date}'
    return pdir / f'{label_name}.pdf'


async def prnt_label_arrayed(label_path: pathlib.Path) -> None:
    """Print the labels. Arrays A6 Labels 2 to a A4 page.
    Uses pdf_tools.array_pdf.convert_many to print the labels.

    Args:
        label_path: The path to the label.

    """

    if not label_path.exists():
        logger.error(f'label_path {label_path} does not exist')

    pdf_tools.array_pdf.convert_many(label_path, print_files=True)


def state_notification_labels_str(state: states.ShipState):
    indent = ' ' * 4
    lines = [
        f'{indent}{pf_shared.notification_label_map[notification]} - {state_notification_contact_detail(state, notification)}'
        for notification in state.contact.notifications.notification_type
    ]
    return '\n'.join(lines)


def state_notification_contact_detail(state: states.ShipState, notification: str):
    if 'EMAIL' in notification or notification == 'DELIVERYNOTIFICATION':
        return state.contact.email_address
    elif 'SMS' in notification:
        return state.contact.mobile_phone
    else:
        raise ValueError('Invalid notification type')


async def get_manager_label_path(man_in):
    return man_in.state.booking_state.label_dl_path


async def update_manager_state(manager_id, session, state):
    man_in = await get_manager(manager_id, session)
    man_in.state = state
    session.add(man_in)
    session.commit()
    session.refresh(man_in)
    return man_in
