# from __future__ import annotations
#
# from dataclasses import Field
# from datetime import date
# from typing import Optional
#
# from pydantic import BaseModel, ConfigDict
#
# from amherst.shipping.pfcom import AmShipper
# from amherst.models import Hire
# from pawsupport.fastui_ps import STYLES
# from pawsupport import fastui_ps as fui
# from shipr.express.types import AddressCandidates
#
#
# class UIState(BaseModel):
#     hire: Hire
#     boxes: int
#     ship_date: Optional[date]
#     candidates: Optional[AddressCandidates]
#
#
# class HireUI(BaseModel):
#     model_config = ConfigDict(
#         arbitrary_types_allowed=True
#     )
#     hire: Hire
#     pfcom: AmShipper
#     state: Optional[UIState] = None
#     ...
#
#
# class Page(fui.PagePR):
#     class_name: str = STYLES.PAGE
