from __future__ import annotations

import typing as _t

from loguru import logger

from shipr.models import pf_top

ModelKind: _t.TypeAlias = _t.Literal['zero', 'minimum', 'simple', 'collect']  # noqa: UP040
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
