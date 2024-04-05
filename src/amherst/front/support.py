from __future__ import annotations

import time
import typing as _t

import fastapi
import sqlmodel as sqm
from loguru import logger

import shipr
from amherst import shipper
from amherst.models import managers
from shipr.models import pf_top


class ManagerNotFound(Exception):
    pass


async def get_manager(manager_id: int, session: sqm.Session):
    man_in = session.get(managers.BookingManagerDB, manager_id)
    if not isinstance(man_in, managers.BookingManagerDB):
        # raise ManagerNotFound()
        raise fastapi.HTTPException(status_code=404, detail='Booking not found')

    return man_in
    # return man_in.model_validate(man_in)


async def update_state(man_in, updt):
    # res= shipr.ShipState.model_validate(
    #     man_in.state.get_updated(updt)
    # )
    # return res

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


async def wait_label(ship_num: str, pfcom: shipper.AmShipper):
    label_path = pfcom.get_label(ship_num=ship_num).resolve()

    for i in range(20):
        if label_path:
            return label_path
        else:
            print('waiting for file to be created')
            time.sleep(1)
    else:
        raise ValueError(f'file not created after 20 seconds {label_path=}')


async def wait_label2(state: shipr.ShipState, pfcom: shipper.AmShipper) -> bool:
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


ModelKind: _t.TypeAlias = _t.Literal[
    'zero', 'minimum', 'simple', 'collect']  # fui not support
valid_model_kinds = _t.get_args(ModelKind)


async def get_model_form_type(model_kind: ModelKind):
    logger.debug(f'getting model form type for {model_kind}')
    match model_kind:
        case 'zero':
            return pf_top.RequestedShipmentZero
        case 'minimum':
            return pf_top.RequestedShipmentMinimum
        case 'simple':
            return pf_top.RequestedShipmentSimple
        case 'collect':
            return pf_top.CollectionMinimum
        case _:
            raise ValueError(f'Invalid kind {model_kind!r}')
