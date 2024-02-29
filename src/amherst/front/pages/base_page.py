from __future__ import annotations

from abc import ABC, abstractmethod

from fastui import components as c
from pydantic import BaseModel

from shipr.models.booking_state import BaseUIState


class BasePage(BaseModel, ABC):
    state: BaseUIState

    @abstractmethod
    async def get_page(self) -> list[c.AnyComponent]:
        raise NotImplementedError
