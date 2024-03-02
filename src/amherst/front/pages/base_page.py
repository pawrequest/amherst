from __future__ import annotations

from abc import ABC, abstractmethod

from fastui import components as c, AnyComponent
from pydantic import BaseModel

from shipr.models.ui_states.abc import BaseUIState


class BasePage(BaseModel, ABC):
    booking: BaseUIState
    @classmethod
    async def from_booking(cls, booking) -> list[AnyComponent]:
        page = cls(booking=booking)
        return await page.get_page()

    @abstractmethod
    async def get_page(self) -> list[c.AnyComponent]:
        raise NotImplementedError
