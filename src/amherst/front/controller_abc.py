from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from fastui import components as c
from pydantic import BaseModel, Field, field_validator
from sqlmodel import SQLModel

from amherst.shipping.pfcom import AmShipper
from shipr.express.shared import BaseRequest


class UIState(SQLModel, ABC):
    ...


class UI(BaseModel, ABC):
    pfcom: AmShipper = Field(default_factory=AmShipper.from_env)
    source_model: BaseModel
    state: UIState

    @abstractmethod
    async def get_components(self) -> list[c.AnyComponent]:
        raise NotImplementedError

    async def get_page(self) -> list[c.AnyComponent]:
        raise NotImplementedError




class PartialRequest(BaseModel):
    request_type: type[BaseRequest]
    attr_dict: Optional[dict] = None

    @field_validator('attr_dict', mode='after')
    def get_attr_dict(cls, v, info):
        return v or {
            attr: None for attr in info.data['request_type'].model_fields
        }

    def get_request(self):
        dict_attrs = list(self.attr_dict.keys())
        model_attrs = list(self.request_type.model_fields)
        if dict_attrs != model_attrs:
            raise ValueError(f"attrs {dict_attrs} do not match {model_attrs}")
        return self.request_type(**self.attr_dict)

    def set_attr(self, attr, value):
        if attr not in self.request_type.model_fields:
            raise ValueError(f"{attr} is not a valid attribute")
        self.attr_dict[attr] = value
        return self
