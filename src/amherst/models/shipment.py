import pprint

from loguru import logger
from pydantic import BaseModel, Field
from unicodedata import category

from amherst.models.commence_adaptors import AmherstRowInfo
from amherst.models.meta import get_table_model
from shipaw.fapi.requests import ShipmentRequest
from shipaw.models.shipment import Shipment


class AmherstShipment(Shipment):
    context: dict = Field(default_factory=dict)

    @property
    def row_info(self) -> AmherstRowInfo:
        res = self.context.get('record').get('row_info')
        # logger.warning('ROW INFO:')

        logger.warning(pprint.pformat(res))
        return AmherstRowInfo(category=res[0], id=res[1])

    @property
    def record_dict(self):
        res = self.context.get('record')

        # logger.warning('RECORD DICT:')
        # logger.warning(pprint.pformat(res))

        if isinstance(res, dict):
            return res
        else:
            raise TypeError(f'Expected dict, got {type(res)}')

    @property
    def record(self):
        model_type = get_table_model(self.row_info.category)
        logger.warning(f'model_type = {model_type.__name__}')
        return model_type.model_validate(self.record_dict)


class AmherstShipmentrequest(ShipmentRequest):
    shipment: AmherstShipment
