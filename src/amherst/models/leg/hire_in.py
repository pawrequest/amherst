from typing import Self

from loguru import logger
from sqlmodel import Field, Column, JSON

from pycommence.api.filters import CmcFilter, FilterArray, FilterCondition
from pycommence.models.cmc_models import CmcModelIn, sub_model_from_cmc
from . import hire_db_parts as parts
from amherst.models.shared import AddressAm, HireStatusEnum, INITIAL_FILTER_ARRAY2
from amherst.models.hire_raw import HireRaw




class HireIn(CmcModelIn):
    raw_table_class = HireRaw
    initial_filter_array = INITIAL_FILTER_ARRAY2

    name: str
    customer: str

    hire_shipping: parts.HireShipping = Field(default=None, sa_column=Column(JSON))
    hire_dates: parts.HireDates = Field(default=None, sa_column=Column(JSON))
    hire_status: parts.HireStatus = Field(default=None, sa_column=Column(JSON))
    hire_address_am: AddressAm = Field(default=None, sa_column=Column(JSON))
    hire_payment: parts.HirePayment = Field(default=None, sa_column=Column(JSON))
    hire_order: parts.HireOrder = Field(default=None, sa_column=Column(JSON))
    staff: parts.HireStaff = Field(default=None, sa_column=Column(JSON))

    @classmethod
    def from_raw_cmc(cls, cmc_raw: HireRaw) -> Self:
        submodels = {
            'hire_dates': parts.HireDates,
            'hire_status': parts.HireStatus,
            'hire_shipping': parts.HireShipping,
            'hire_address_am': AddressAm,
            'hire_payment': parts.HirePayment,
            'hire_order': parts.HireOrder,
            'staff': parts.HireStaff,
        }
        out_dict = {}
        for model_name, model_class in submodels.items():
            out_dict[model_name] = sub_model_from_cmc(model_class, cmc_raw)
        out_dict['name'] = cmc_raw.name
        out_dict['customer'] = cmc_raw.customer

        return cls.model_validate(out_dict)

    @classmethod
    def rout_prefix(cls) -> str:
        return '/hire/'

    @property
    def contact_dict(self) -> dict[str, str]:
        ret = dict(
            business_name=self.customer,
            email_address=self.hire_address_am.email,
            mobile_phone=self.hire_address_am.telephone
        )
        return ret

    @property
    def address_dict(self) -> dict[str, str]:
        try:
            # add = self.delivery_address.address.strip()
            add_lines = self.hire_address_am.address.strip().splitlines()
            town = add_lines[-1]

            # if len(add_lines) < 3:
            #     add_lines.extend([''] * (3 - len(add_lines)))
            if len(add_lines) > 3:
                add_lines[2] = ','.join(add_lines[2:])

            lines_dict = {
                f'address_line{num}': line
                for num, line in enumerate(add_lines, start=1)
            }

            return dict(
                **lines_dict,
                town=town,
                postcode=self.hire_address_am.postcode,
            )
        except AttributeError:
            logger.warning(f'Could not build address dict for hire "{self.name}"')
            return dict()

    #
    # shipping: parts.HireShipping = Field(default=None, sa_column=Column(JSON))
    # dates: parts.HireDates = Field(default=None, sa_column=Column(JSON))
    # status: parts.HireStatus = Field(default=None, sa_column=Column(JSON))
    # delivery_address: AmAddress = Field(default=None, sa_column=Column(JSON))
    # payment: parts.HirePayment = Field(default=None, sa_column=Column(JSON))
    # items: HireItems = Field(default=None, sa_column=Column(JSON))
    # staff: parts.HireStaff = Field(default=None, sa_column=Column(JSON))
    #
    # shipping: SerializeAsAny[parts.HireShipping] = Field(default=None, sa_column=Column(JSON))
    # dates: SerializeAsAny[parts.HireDates] = Field(default=None, sa_column=Column(JSON))
    # status: SerializeAsAny[parts.HireStatus] = Field(default=None, sa_column=Column(JSON))
    # delivery_address: SerializeAsAny[AmAddress] = Field(default=None, sa_column=Column(JSON))
    # payment: SerializeAsAny[parts.HirePayment] = Field(default=None, sa_column=Column(JSON))
    # items: SerializeAsAny[HireItems] = Field(default=None, sa_column=Column(JSON))
    # staff: SerializeAsAny[parts.HireStaff] = Field(default=None, sa_column=Column(JSON))
