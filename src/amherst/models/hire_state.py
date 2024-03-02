# from __future__ import annotations
import base64
import datetime as dt
import pathlib

import pydantic as pyd

from shipr.models import (pf_ext, pf_msg, pf_shared, pf_top)
from shipr.models.ui_states import states


# if _ty.TYPE_CHECKING:
#     pass


# ship_date: pf_shared.ValidShipDate = sqm.Field(default_factory=date.today)


