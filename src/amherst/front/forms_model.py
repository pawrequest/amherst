from __future__ import annotations

from typing import Annotated

import fastapi
from fastui import FastUI, components as c
from fastui.forms import fastui_form

from amherst import am_db, shipper
from shipr.models import pf_top

router = fastapi.APIRouter()
