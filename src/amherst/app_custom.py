from typing import Any, cast

from fastapi import FastAPI
from pydantic import Field
from shipaw.fapi.app_custom import AppSettings as AppSettings_
from shipaw.fapi.app_custom import AppState as AppState_
from shipaw.fapi.app_custom import ShipawRequest

from amherst.config import AmherstSettings


class AppSettings(AppSettings_):
    amherst: AmherstSettings = Field(default_factory=AmherstSettings.from_env)


class AppState(AppState_):
    settings: AppSettings
    category: str
    row_id: str

    @classmethod
    def create(cls) -> 'AppState':
        state = super().create()
        state = cast(AppState, state)
        state.settings = AppSettings()
        return state


class AmherstApp(FastAPI):
    state: AppState


class AmherstRequest(ShipawRequest):
    @property
    def app(self) -> AmherstApp:
        return super().app  # type: ignore[return-value]

    def amherst_setting(self, field_name: str) -> Any:
        return getattr(self.app.state.settings.amherst, field_name)
