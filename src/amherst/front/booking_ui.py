from typing import Optional
from pathlib import Path

from fastui import components as c
from fastui.events import GoToEvent

from amherst.front.controller_abc import UIBase
from amherst.front.state import ShipState


class ResponseState(ShipState):
    label_path: Optional[Path] = None


class BookingUI(UIBase):
    async def get_page(self) -> list[c.AnyComponent]:
        ret = [
            *self.alert_texts,
            c.Button(
                text=f'Download and Print Label for Shipment {self.shipment_number}',
                on_click=GoToEvent(url=f'/book/print/{self.shipment_number}'),
            ),
        ]
        return ret

    @property
    def alert_texts(self):
        return [c.Text(text=al.message) for al in self.alerts]

    @property
    def alerts(self):
        return self.state.response.alerts.alert

    @property
    def shipment_number(self):
        return self.state.response.completed_shipment_info.completed_shipments.completed_shipment[
            0].shipment_number
