import datetime as dt
import typing as _ty

from amherst.models import am_shared
from shipr.models import pf_ext, pf_shared, pf_top

from amherst.models.am_shared import addr_lines_dict_am


class Sale(pf_shared.BasePFType):
    cmc_table_name: _ty.ClassVar[str] = 'Sale'

    record: dict[str, str]

    # @pyd.computed_field
    @property
    def boxes(self) -> int:
        return 1

    # @pyd.computed_field
    @property
    def name(self) -> str:
        return self.record.get(am_shared.AmherstFields.NAME)

    # @pyd.computed_field
    @property
    def ship_date(self) -> dt.date:
        """uses cmc cannonical format yyyymmdd"""
        return dt.date.today()

    # @pyd.computed_field
    @property
    def input_address(self) -> pf_ext.AddressRecipient:
        return pf_ext.AddressRecipient(
            **addr_lines_dict_am(self.record.get(am_shared.AmherstFields.ADDRESS)),
            town='',
            postcode=self.record.get(am_shared.AmherstFields.POSTCODE),
        )

    # @pyd.computed_field
    @property
    def contact(self) -> pf_top.Contact:
        return pf_top.Contact(
            business_name=self.record.get(am_shared.AmherstFields.CUSTOMER),
            email_address=self.record.get(am_shared.AmherstFields.EMAIL),
            mobile_phone=self.record.get(am_shared.AmherstFields.SALE_TELEPHONE),
            contact_name=self.record.get(am_shared.AmherstFields.CONTACT),
        )

