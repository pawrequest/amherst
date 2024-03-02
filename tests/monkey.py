# import os
# from datetime import date, timedelta
# from pathlib import Path
# from typing import Annotated, Callable, ClassVar, List, Literal, Optional, Self
# from enum import Enum, StrEnum
# import typing as _ty
#
# from loguru import logger
# from pydantic import (
#     AliasGenerator,
#     BaseModel,
#     ConfigDict,
#     PositiveInt,
#     StringConstraints,
#     condate,
#     field_validator,
# )
# from pydantic.alias_generators import to_pascal, to_snake
# from sqlalchemy import Column, JSON, TypeDecorator
# from sqlmodel import Field, SQLModel
# import sqlalchemy as sqa
# import sqlmodel as sqm
#
# from pawsupport.get_set import hash_simple_md5
# from .test_client import ELClient
# from pawsupport import convert_print_silent2
# from pawsupport.pydantic.pyd_types import TruncatedSafeMaybeStr, TruncatedSafeStr
# import pycommence
#
#
# class BasePFType(SQLModel):
#     model_config = ConfigDict(
#         alias_generator=AliasGenerator(
#             alias=to_pascal,
#         ),
#         use_enum_values=True,
#         populate_by_name=True,
#     )
#
#
# class Notifications(BasePFType):
#     notification_type: List[str] = Field(default_factory=list)
#
#
# class Contact(BasePFType):
#     business_name: str
#     email_address: TruncatedSafeStr(50)
#     mobile_phone: str
#
#     contact_name: TruncatedSafeMaybeStr(30)
#     telephone: Optional[str] = None
#     fax: Optional[str] = None
#
#     senders_name: TruncatedSafeMaybeStr(25)
#     notifications: Optional[Notifications] = None
#
#
# class AddressJson(TypeDecorator):
#     impl = JSON
#
#     def process_bind_param(self, value, dialect):
#         return value.model_dump_json() if value is not None else ""
#
#     def process_result_value(self, value, dialect):
#         return AddressRecipient.model_validate_json(value) if value else None
#
#
# class ContactJson(TypeDecorator):
#     impl = JSON
#
#     def process_bind_param(self, value, dialect):
#         return value.model_dump_json() if value is not None else ""
#
#     def process_result_value(self, value, dialect):
#         return Contact.model_validate_json(value) if value else None
#
#
# def addr_lines_dict_am(address: str) -> dict[str, str]:
#     addr_lines = address.splitlines()
#     if len(addr_lines) < 3:
#         addr_lines.extend([""] * (3 - len(addr_lines)))
#     elif len(addr_lines) > 3:
#         addr_lines[2] = ",".join(addr_lines[2:])
#     return {f"address_line{num}": line for num, line in enumerate(addr_lines, start=1)}
#
#
# INITIAL_FILTER_ARRAY2 = pycommence.FilterArray().add_filters(
#     pycommence.CmcFilter(
#         cmc_col="Status",
#         condition='Equal To',
#         value="BOOKED_IN",
#     ),
#     pycommence.CmcFilter(
#         cmc_col="Send Out Date",
#         condition='After',
#         value="2023-01-01",
#     ),
# )
#
#
# class AmherstFields(StrEnum):
#     ACTUAL_RETURN_DATE = "Actual Return Date"
#     ADDRESS = "Delivery Address"
#     AERIAL_ADAPT = "Number Aerial Adapt"
#     ALL_ADDRESS = "All Address"
#     BATTERIES = "Number Batteries"
#     BOOKED_DATE = "Booked Date"
#     BOXES = "Boxes"
#     BUSINESS_NAME = "Delivery Name"
#     CASES = "Number Cases"
#     CLIPON_AERIAL = "Number Clipon Aerial"
#     CLOSED = "Closed"
#     CONTACT = "Delivery Contact"
#     CUSTOMER = "To Customer"
#     DB_LABEL_PRINTED = "DB label printed"
#     DELIVERY_COST = "Delivery Cost"
#     DISCOUNT_DESCRIPTION = "Discount Description"
#     DISCOUNT_PERCENTAGE = "Discount Percentage"
#     DUE_BACK_DATE = "Due Back Date"
#     EM = "Number EM"
#     EMAIL = "Delivery Email"
#     EMC = "Number EMC"
#     HEADSET = "Number Headset"
#     HEADSET_BIG = "Number Headset Big"
#     ICOM = "Number Icom"
#     ICOM_CAR_LEAD = "Number ICOM Car Lead"
#     ICOM_PSU = "Number ICOM PSU"
#     INVOICE = "Invoice"
#     MAGMOUNT = "Number Magmount"
#     MEGAPHONE = "Number Megaphone"
#     MEGAPHONE_BAT = "Number Megaphone Bat"
#     MISSING_KIT = "Missing Kit"
#     NAME = "Name"
#     PACKED_BY = "Packed By"
#     PACKED_DATE = "Packed Date"
#     PACKED_TIME = "Packed Time"
#     PARROT = "Number Parrot"
#     PAYMENT_TERMS = "Payment Terms"
#     PICKUP_ARRANGED = "Pickup Arranged"
#     POSTCODE = "Delivery Postcode"
#     PURCHASE_ORDER = "Purchase Order"
#     RADIO_TYPE = "Radio Type"
#     RECURRING_HIRE = "Recurring Hire"
#     REFERENCE_NUMBER = "Reference Number"
#     REPEATER = "Number Repeater"
#     REPROGRAMMED = "Reprogrammed"
#     RETURN_NOTES = "Return Notes"
#     SENDING_STATUS = "Sending Status"
#     SEND_COLLECT = "Send / Collect"
#     SEND_METHOD = "Send Method"
#     SEND_OUT_DATE = "Send Out Date"
#     SGL_CHARGER = "Number Sgl Charger"
#     SPECIAL_KIT = "Special Kit"
#     STATUS = "Status"
#     TELEPHONE = "Delivery Tel"
#     TRACKING_NUMBERS = "Tracking Numbers"
#     UHF = "Number UHF"
#     UHF_6WAY = "Number UHF 6-way"
#     UNPACKED_BY = "Unpacked by"
#     UNPACKED_DATE = "Unpacked Date"
#     UNPACKED_TIME = "Unpacked Time"
#     VHF = "Number VHF"
#     VHF_6WAY = "Number VHF 6-way"
#     WAND = "Number Wand"
#     WAND_BAT = "Number Wand Battery"
#     WAND_CHARGER = "Number Wand Charger"
#
#
# class SaleFields(StrEnum):
#     CUSTOMER = "To Customer"
#     NAME = "Name"
#     LOST_EQUIPMENT = "Lost Equipment"
#     STATUS = "Status"
#     DATE_ORDERED = "Date Ordered"
#     DATE_SENT = "Date Sent"
#     INVOICE_TERMS = "Invoice Terms"
#     INVOICE = "Invoice"
#     PURCHASE_ORDER_PRINT = "Purchase Order Print"
#     PURCHASE_ORDER = "Purchase Order"
#     ITEMS_ORDERED = "Items Ordered"
#     SERIAL_NUMBERS = "Serial Numbers"
#     ORDER_PACKED_BY = "Order Packed By"
#     ORDER_TAKEN_BY = "Order Taken By"
#     DELIVERY_METHOD = "Delivery Method"
#     OUTBOUND_ID = "Outbound ID"
#     NOTES = "Notes"
#     DELIVERY_NOTES = "Delivery Notes"
#     DELIVERY_ADDRESS = "Delivery Address"
#     DELIVERY_CONTACT = "Delivery Contact"
#     DELIVERY_EMAIL = "Delivery Email"
#     DELIVERY_NAME = "Delivery Name"
#     DELIVERY_POSTCODE = "Delivery Postcode"
#     DELIVERY_TELEPHONE = "Delivery Telephone"
#     INVOICE_ADDRESS = "Invoice Address"
#     INVOICE_CONTACT = "Invoice Contact"
#     INVOICE_EMAIL = "Invoice Email"
#     INVOICE_NAME = "Invoice Name"
#     INVOICE_POSTCODE = "Invoice Postcode"
#     INVOICE_TELEPHONE = "Invoice Telephone"
#
#
# DeliveryType = Literal["DELIVERY"]
#
#
# class DeliveryTypeEnum(StrEnum):
#     DELIVERY = "DELIVERY"
#
#
# class DropOffInd(StrEnum):
#     PO = "PO"
#     DEPOT = "DEPOT"
#
#
# class DepartmentEnum(Enum):
#     MAIN = 1
#
#
# class ServiceCode(str, Enum):
#     FLEX_DELIVERY_SERVICE_PRODUCT = "S09"
#     EXPRESS9 = "09"
#     EXPRESS9_SECURE = "SEN"
#     EXPRESS9_COURIER_PACK = "SC9"
#     EXPRESS10 = "S10"
#     EXPRESS10_SECURE = "SEE"
#     EXPRESS10_EXCHANGE = "SWN"
#     EXPRESS10_SECURE_EXCHANGE = "SSN"
#     EXPRESS10_COURIER_PACK = "SC0"
#     EXPRESSAM = "S12"
#     EXPRESSAM_LARGE = "SAML"
#     EXPRESSAM_SECURE = "SET"
#     EXPRESSAM_EXCHANGE = "SWT"
#     EXPRESSAM_SECURE_EXCHANGE = "SST"
#     EXPRESSAM_COURIER_PACK = "SC2"
#     EXPRESSAM_SUNDAY_B2B = "SC2P"
#     EXPRESSPM = "SPM"
#     EXPRESSPM_SECURE = "SEM"
#     EXPRESSPM_EXCHANGE = "SWP"
#     EXPRESSPM_SECURE_EXCHANGE = "SSP"
#     EXPRESS24 = "SND"
#     EXPRESS24_LARGE = "S24L"
#     EXPRESS24_SECURE = "SEF"
#     EXPRESS24_EXCHANGE = "SWR"
#     EXPRESS24_SECURE_EXCHANGE = "SSF"
#     EXPRESS24_COURIER_PACK = "SCD"
#     EXPRESS24_SUNDAY = "SCDP"
#     EXPRESS48 = "SUP"
#     EXPRESS48_LARGE = "SID"
#     PARCELRIDER_PLUS_NI_ONLY = "SPR"
#     EXPRESSCOLLECT = "SMS"
#     GLOBALBULK_DIRECT = "GBD"
#     GLOBALECONOMY = "IPE"
#     GLOBALEXPRESS = "GEX"
#     GLOBALEXPRESS_ENVELOPE_DELIVERY = "GXE"
#     GLOBALEXPRESS_PACK_DELIVERY = "GXP"
#     GLOBALPRIORITY = "GPR"
#     GLOBALPRIORITY_H_M_FORCES = "GPR"
#     GLOBALPRIORITY_RETURNS = "EPR"
#     GLOBALVALUE = "GVA"
#     EURO_ECONOMY = "EPH"
#     EURO_PRIORITY = "EPB"
#     EURO_PRIORITY_PACK = "EPK"
#     EUROPRIORITY_HOME_PO_BOXES = "EPP"
#     IRELANDEXPRESS = "I24"
#
#
# class AlertType(Enum):
#     error = "ERROR"
#     warning = "WARNING"
#     notification = "NOTIFICATION"
#
#
# def valid_ship_date_type() -> type[date]:
#     tod = date.today()
#     return condate(ge=tod, le=tod + timedelta(days=7))
#
#
# ValidShipDate = valid_ship_date_type()
#
# SALE_CUSTOMERS = pycommence.Connection(
#     name="SaleCustomers",
#     to_table="Customers",
#     from_table="Sale",
# )
#
# HIRE_CUSTOMERS = pycommence.Connection(
#     name="HireCustomers",
#     to_table="Customers",
#     from_table="Hire",
# )
#
#
# class HireStatusEnum(StrEnum):
#     BOOKED_IN = "Booked in"
#     PACKED = "Booked in and packed"
#     PARTIALLY_PACKED = "Partially packed"
#     OUT = "Out"
#     RTN_OK = "Returned all OK"
#     RTN_PROBLEMS = "Returned with problems"
#     QUOTE_GIVEN = "Quote given"
#     CANCELLED = "Cancelled"
#     EXTENDED = "Extended"
#     SOLD = "Sold To Customer"
#
#
# class BaseUIState(BaseModel):
#     model_config = ConfigDict(
#         use_enum_values=True,
#     )
#
#     @staticmethod
#     def call_and_get_method_query(method: Callable, *args, **kwargs) -> dict[str, str]:
#         """returns {update_func name: jsonified result of update_func}"""
#         json_res = method(*args, **kwargs).model_dump_json(exclude_none=True)
#         return {to_snake(method.__name__): json_res}
#
#     def update(self, updater: "BookingStateUpdater") -> Self:
#         """return a new BookingStateUpdate with the values of other merged into self."""
#         for update in updater.model_fields_set:
#             setattr(self, update, getattr(updater, update))
#         return self
#
#     def update_query(self) -> dict[str, str]:
#         return {"updater": self.model_dump_json(exclude_none=True)}
#
#     def update_get_query(self, *, updater: "BookingStateUpdater") -> dict[str, str]:
#         """returns {'update': updated json}"""
#         return self.call_and_get_method_query(self.update, updater)
#
#
# Max80 = Annotated[str, StringConstraints(max_length=80)]
#
#
# class Authentication(BasePFType):
#     user_name: Max80
#     password: Max80
#
#     @classmethod
#     def from_env(cls):
#         username = os.getenv("PF_EXPR_SAND_USR")
#         password = os.getenv("PF_EXPR_SAND_PWD")
#         return cls(user_name=username, password=password)
#
#
# class BaseRequest(BasePFType):
#     authentication: Optional[Authentication] = Field(None)
#
#     def req_dict(self):
#         return self.model_dump(by_alias=True)
#
#     @property
#     def authorised(self):
#         return self.authentication is not None
#
#     def authorise(self, auth: Authentication):
#         self.authentication = auth
#
#     def auth_request_dict(self) -> dict:
#         if not self.authorised:
#             raise ValueError("Authentication is required")
#         all_obs = [self.authentication, *self.objs]
#         return self.alias_dict(all_obs)
#
#
# class Alert(BasePFType):
#     code: int = Field(...)
#     message: str = Field(...)
#     type: AlertType = Field(...)
#
#
# class Alerts(BasePFType):
#     alert: List[Alert] = Field(..., description="")
#
#
# class BaseResponse(BasePFType):
#     alerts: Optional[Alerts] = Field(None)
#
#     @field_validator("alerts")
#     def check_alerts(cls, v):
#         if v:
#             for alt in v.alert:
#                 if alt.type == "WARNING":
#                     logger.warning(f"ExpressLink Warning: {alt.message}")
#                 elif alt.type == "ERROR":
#                     logger.error(f"ExpressLink Error: {alt.message}")
#                 else:
#                     logger.info(f"ExpressLink {alt.type}: {alt.message}")
#         return v
#
#
# class BaseAddress(BasePFType):
#     address_line1: TruncatedSafeStr(24)
#     address_line2: TruncatedSafeMaybeStr(24)
#     address_line3: TruncatedSafeMaybeStr(24)
#     town: TruncatedSafeStr(24)
#     postcode: str
#     country: str = Field("GB")
#
#     #
#     @classmethod
#     def from_lines_str_and_postcode(cls, addr_lines_str: str, postcode: str):
#         return cls.AddressRecipientPF(
#             **cls.address_string_to_dict(addr_lines_str),
#             town="",
#             postcode=postcode,
#         )
#
#     def address_lines_list(self):
#         return [self.address_line1, self.address_line2, self.address_line3, self.town,
#                 self.postcode, self.country]
#
#     def address_lines_str(self):
#         return "\n".join(self.address_lines_list())
#
#     def address_lines_dict(self):
#         return {
#             "address_line1": self.address_line1,
#             "address_line2": self.address_line2,
#             "address_line3": self.address_line3,
#         }
#
#     def address_string_to_dict(self, address_str: str) -> dict[str, str]:
#         addr_lines = address_str.splitlines()
#         if len(addr_lines) < 3:
#             addr_lines.extend([""] * (3 - len(addr_lines)))
#         elif len(addr_lines) > 3:
#             addr_lines[2] = ",".join(addr_lines[2:])
#         return {
#             "address_line1": addr_lines[0],
#             "address_line2": addr_lines[1],
#             "address_line3": addr_lines[2],
#         }
#
#
# class AddressSender(BaseAddress):
#     town: TruncatedSafeStr(24)
#     postcode: str
#     country: str = Field("GB")
#
#
# class AddressRecipient(BaseAddress):
#     address_line1: TruncatedSafeStr(40)
#     address_line2: TruncatedSafeMaybeStr(50)
#     address_line3: TruncatedSafeMaybeStr(60)
#     town: TruncatedSafeStr(30)
#
#
# class SpecifiedNeighbour(BasePFType):
#     address: Optional[List[AddressRecipient]] = Field(None, description="")
#
#
# class PAF(BasePFType):
#     postcode: Optional[str] = None
#     count: Optional[int] = Field(None)
#     specified_neighbour: Optional[List[SpecifiedNeighbour]] = Field(None, description="")
#
#
# class BookingStateUpdater(BaseUIState):
#     boxes: Optional[PositiveInt] = None
#     ship_date: Optional[ValidShipDate] = None
#     ship_service: Optional[ServiceCode] = None
#     contact: Optional[Contact] = Field(sa_column=sqm.Column(sqm.JSON))
#     address: Optional[AddressRecipient] = Field(sa_column=sqm.Column(sqm.JSON))
#     input_address: Optional[AddressRecipient] = Field(sa_column=sqm.Column(sqm.JSON))
#
#
# class BookingStateIn(BookingStateUpdater):
#     @classmethod
#     def from_shipable(cls, hire):
#         return cls(**hire.model_dump())
#
#     boxes: PositiveInt = Field(1)
#     ship_date: ValidShipDate
#     ship_service: ServiceCode
#     contact: Contact = Field(sa_column=sqm.Column(sqm.JSON))
#     address: AddressRecipient = Field(sa_column=sqm.Column(sqm.JSON))
#
#     @classmethod
#     def hire_initial(cls, hire, pfcom: ELClient):
#         return cls(
#             boxes=hire.boxes,
#             ship_date=hire.ship_date,
#             ship_service=ServiceCode.EXPRESS24,
#             contact=hire.contact,
#             address=pfcom.choose_address(hire.input_address),
#             # candidates=pfcom.get_candidates(hire.address.postcode),
#         )
#
#
# class Enhancement(BasePFType):
#     enhanced_compensation: Optional[str] = Field(None)
#     saturday_delivery_required: Optional[bool] = Field(None)
#
#
# class HazardousGood(BasePFType):
#     lqdgun_code: Optional[str] = Field(None)
#     lqdg_description: Optional[str] = Field(None)
#     lqdg_volume: Optional[float] = Field(None)
#     firearms: Optional[str] = Field(None)
#
#
# class Returns(BasePFType):
#     returns_email: Optional[str] = Field(None)
#     email_message: Optional[str] = Field(None)
#     email_label: bool = Field(...)
#
#
# class ContentDetail(BasePFType):
#     country_of_manufacture: str = Field(...)
#     country_of_origin: Optional[str] = Field(None)
#     manufacturers_name: Optional[str] = Field(None)
#     description: str = Field(...)
#     unit_weight: float = Field(...)
#     unit_quantity: int = Field(...)
#     unit_value: float = Field(...)
#     currency: str = Field(...)
#     tariff_code: Optional[str] = Field(None)
#     tariff_description: Optional[str] = Field(None)
#     article_reference: Optional[str] = Field(None)
#
#
# class DateTimeRange(BasePFType):
#     from_: str = Field(...)
#     to: str = Field(...)
#
#
# class ContentData(BasePFType):
#     name: str = Field(...)
#     data: str = Field(...)
#
#
# class LabelItem(BasePFType):
#     name: str = Field(...)
#     data: str = Field(...)
#
#
# class Barcode(BasePFType):
#     name: str = Field(...)
#     data: str = Field(...)
#
#
# class Image(BasePFType):
#     name: str = Field(...)
#     data: str = Field(...)
#
#
# PrintType = Literal["ALL_PARCELS", "SINGLE_PARCEL"]
#
#
# class Document(BasePFType):
#     data: bytes = Field(...)
#
#     def download(self, outpath: Path = Path("label_out.pdf")) -> Path:
#         with open(outpath, "wb") as f:
#             f.write(self.data)
#         return outpath
#
#     def print_doc_arrayed(self):
#         output = self.download()
#         convert_print_silent2(output)
#
#
# class ManifestShipment(BasePFType):
#     shipment_number: str = Field(...)
#     service_code: str = Field(...)
#
#
# class CompletedShipment(BasePFType):
#     shipment_number: Optional[str] = Field(None)
#     out_bound_shipment_number: Optional[str] = Field(None)
#     in_bound_shipment_number: Optional[str] = Field(None)
#     partner_number: Optional[str] = Field(None)
#
#
# class CompletedReturnInfo(BasePFType):
#     status: str = Field(...)
#     shipment_number: str = Field(...)
#     collection_time: DateTimeRange = Field(...)
#
#
# class CompletedCancelInfo(BasePFType):
#     status: Optional[str] = Field(None)
#     shipment_number: Optional[str] = Field(None)
#
#
# class SafePlacelist(BasePFType):
#     safe_place: Optional[list[str]] = Field(None, description="")
#
#
# class NominatedDeliveryDatelist(BasePFType):
#     nominated_delivery_date: Optional[list[str]] = Field(None, description="")
#
#
# class ServiceCodes(BasePFType):
#     service_code: Optional[list[str]] = Field(None, description="")
#
#
# class Hours(BasePFType):
#     open: Optional[str] = Field(None)
#     close: Optional[str] = Field(None)
#     close_lunch: Optional[str] = Field(None)
#     after_lunch_opening: Optional[str] = Field(None)
#
#
# class Position(BasePFType):
#     longitude: Optional[float] = Field(None)
#     latitude: Optional[float] = Field(None)
#
#
# class InBoundDetails(BasePFType):
#     contract_number: str = Field(...)
#     service_code: str = Field(...)
#     total_shipment_weight: Optional[str] = Field(None)
#     enhancement: Optional[Enhancement] = Field(None)
#     reference_number1: Optional[str] = Field(None)
#     reference_number2: Optional[str] = Field(None)
#     reference_number3: Optional[str] = Field(None)
#     reference_number4: Optional[str] = Field(None)
#     reference_number5: Optional[str] = Field(None)
#     special_instructions1: Optional[str] = Field(None)
#     special_instructions2: Optional[str] = Field(None)
#     special_instructions3: Optional[str] = Field(None)
#     special_instructions4: Optional[str] = Field(None)
#
#
# class HazardousGoods(BasePFType):
#     hazardous_good: list[HazardousGood] = Field(..., description="")
#
#
# class ContentDetails(BasePFType):
#     content_detail: list[ContentDetail] = Field(..., description="")
#
#
# class CollectionInfo(BasePFType):
#     collection_contact: Contact = Field(...)
#     collection_address: AddressRecipient = Field(...)
#     collection_time: Optional[DateTimeRange] = Field(None)
#
#
# class ParcelContents(BasePFType):
#     item: list[ContentData] = Field(..., description="")
#
#
# class LabelData(BasePFType):
#     item: list[LabelItem] = Field(..., description="")
#
#
# class Barcodes(BasePFType):
#     barcode: list[Barcode] = Field(..., description="")
#
#
# class Images(BasePFType):
#     image: list[Image] = Field(..., description="")
#
#
# class ManifestShipments(BasePFType):
#     manifest_shipment: list[ManifestShipment] = Field(..., description="")
#
#
# class CompletedShipments(BasePFType):
#     completed_shipment: list[CompletedShipment] = Field(..., description="")
#
#
# class CompletedCancel(BasePFType):
#     completed_cancel_info: Optional[CompletedCancelInfo] = Field(None)
#
#
# class Department(BasePFType):
#     department_id: Optional[list[int]] = Field(None, description="")
#     service_codes: Optional[list[ServiceCodes]] = Field(None, description="")
#     nominated_delivery_date_list: Optional[NominatedDeliveryDatelist] = Field(None)
#
#
# class Mon(BasePFType):
#     hours: Optional[Hours] = Field(None)
#
#
# class Tue(BasePFType):
#     hours: Optional[Hours] = Field(None)
#
#
# class Wed(BasePFType):
#     hours: Optional[Hours] = Field(None)
#
#
# class Thu(BasePFType):
#     hours: Optional[Hours] = Field(None)
#
#
# class Fri(BasePFType):
#     hours: Optional[Hours] = Field(None)
#
#
# class Sat(BasePFType):
#     hours: Optional[Hours] = Field(None)
#
#
# class Sun(BasePFType):
#     hours: Optional[Hours] = Field(None)
#
#
# class BankHol(BasePFType):
#     hours: Optional[Hours] = Field(None)
#
#
# class Parcel(BasePFType):
#     weight: Optional[float] = Field(None)
#     length: Optional[int] = Field(None)
#     height: Optional[int] = Field(None)
#     width: Optional[int] = Field(None)
#     purpose_of_shipment: Optional[str] = Field(None)
#     invoice_number: Optional[str] = Field(None)
#     export_license_number: Optional[str] = Field(None)
#     certificate_number: Optional[str] = Field(None)
#     content_details: Optional[ContentDetails] = Field(None)
#     shipping_cost: Optional[float] = Field(None)
#
#
# class ParcelLabelData(BasePFType):
#     parcel_number: Optional[str] = Field(None)
#     shipment_number: Optional[str] = Field(None)
#     journey_leg: Optional[str] = Field(None)
#     label_data: Optional[LabelData] = Field(None)
#     barcodes: Optional[Barcodes] = Field(None)
#     images: Optional[Images] = Field(None)
#     parcel_contents: Optional[list[ParcelContents]] = Field(None, description="")
#
#
# class CompletedManifestInfo(BasePFType):
#     department_id: int = Field(...)
#     manifest_number: str = Field(...)
#     manifest_type: str = Field(...)
#     total_shipment_count: int = Field(...)
#     manifest_shipments: ManifestShipments = Field(...)
#
#
# class CompletedShipmentInfoCreatePrint(BasePFType):
#     lead_shipment_number: Optional[str] = Field(None)
#     shipment_number: Optional[str] = Field(None)
#     delivery_date: Optional[str] = Field(None)
#     status: str = Field(...)
#     completed_shipments: CompletedShipments = Field(...)
#
#
# class Departments(BasePFType):
#     department: Optional[list[Department]] = Field(None, description="")
#
#
# class OpeningHours(BasePFType):
#     mon: Optional[Mon] = Field(None)
#     tue: Optional[Tue] = Field(None)
#     wed: Optional[Wed] = Field(None)
#     thu: Optional[Thu] = Field(None)
#     fri: Optional[Fri] = Field(None)
#     sat: Optional[Sat] = Field(None)
#     sun: Optional[Sun] = Field(None)
#     bank_hol: Optional[BankHol] = Field(None)
#
#
# class Parcels(BasePFType):
#     parcel: list[Parcel] = Field(..., description="")
#
#
# class ShipmentLabelData(BasePFType):
#     parcel_label_data: list[ParcelLabelData] = Field(..., description="")
#
#
# class CompletedManifests(BasePFType):
#     completed_manifest_info: list[CompletedManifestInfo] = Field(..., description="")
#
#
# class NominatedDeliveryDates(BasePFType):
#     service_code: Optional[str] = Field(None)
#     departments: Optional[Departments] = Field(None)
#
#
# class PostcodeExclusion(BasePFType):
#     delivery_postcode: Optional[str] = Field(None)
#     collection_postcode: Optional[str] = Field(None)
#     departments: Optional[Departments] = Field(None)
#
#
# class PostOffice(BasePFType):
#     post_office_id: Optional[str] = Field(None)
#     business: Optional[str] = Field(None)
#     address: Optional[AddressRecipient] = Field(None)
#     opening_hours: Optional[OpeningHours] = Field(None)
#     distance: Optional[float] = Field(None)
#     availability: Optional[bool] = Field(None)
#     position: Optional[Position] = Field(None)
#     booking_reference: Optional[str] = Field(None)
#
#
# class InternationalInfo(BasePFType):
#     parcels: Optional[Parcels] = Field(None)
#     exporter_customs_reference: Optional[str] = Field(None)
#     recipient_importer_vat_no: Optional[str] = Field(None)
#     original_export_shipment_no: Optional[str] = Field(None)
#     documents_only: Optional[bool] = Field(None)
#     documents_description: Optional[str] = Field(None)
#     value_under200_us_dollars: Optional[bool] = Field(None)
#     shipment_description: Optional[str] = Field(None)
#     comments: Optional[str] = Field(None)
#     invoice_date: Optional[str] = Field(None)
#     terms_of_delivery: Optional[str] = Field(None)
#     purchase_order_ref: Optional[str] = Field(None)
#
#
# class ConvenientCollect(BasePFType):
#     postcode: Optional[str] = Field(None)
#     post_office: Optional[list[PostOffice]] = Field(None, description="")
#     count: Optional[int] = Field(None)
#     post_office_id: Optional[str] = Field(None)
#
#
# class SpecifiedPostOffice(BasePFType):
#     postcode: Optional[str] = Field(None)
#     post_office: Optional[list[PostOffice]] = Field(None, description="")
#     count: Optional[int] = Field(None)
#     post_office_id: Optional[str] = Field(None)
#
#
# class DeliveryOptions(BasePFType):
#     convenient_collect: Optional[ConvenientCollect] = Field(None)
#     irts: Optional[bool] = Field(None)
#     letterbox: Optional[bool] = Field(None)
#     specified_post_office: Optional[SpecifiedPostOffice] = Field(None)
#     specified_neighbour: Optional[str] = Field(None)
#     safe_place: Optional[str] = Field(None)
#     pin: Optional[int] = Field(None)
#     named_recipient: Optional[bool] = Field(None)
#     address_only: Optional[bool] = Field(None)
#     nominated_delivery_date: Optional[str] = Field(None)
#     personal_parcel: Optional[str] = Field(None)
#
#
# # class AddressChoice(BasePFType):
# #     address: AddressRecipient
# #     score: int
#
#
# class HireStateLink(SQLModel, table=True):
#     hire_id: Optional[int] = Field(default=None, foreign_key="hire.id", primary_key=True)
#     state_id: Optional[int] = Field(default=None, foreign_key="hirestate.id", primary_key=True)
#
#
# class HireState(BookingStateIn, SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     hire_id: int = Field(foreign_key="hire.id", unique=True, index=True)
#     hire: "Hire" = sqm.Relationship(back_populates="state", link_model=HireStateLink)
#
#
# class HireIn(SQLModel):
#     cmc_table_name: ClassVar[str] = "Hire"
#     initial_filter_array: ClassVar[pycommence.FilterArray] = Field(
#         default=INITIAL_FILTER_ARRAY2, sa_column=Column(JSON)
#     )
#     record: dict = Field(sa_column=sqa.Column(JSON))
#     state: Optional[BookingStateIn] = Field(None, sa_column=Column(JSON))
#
#     input_address: Optional[AddressRecipient] = Field(default=None, sa_column=Column(JSON))
#     name: Optional[str] = Field(default=None, unique=True)
#     contact: Optional[Contact] = Field(default=None)
#     boxes: Optional[int] = 1
#     ship_date: Optional[date] = None
#
#     # booking_state: BookingStateIn | None = Field(None, sa_column=Column(JSON))
#
#     @property
#     def get_hash(self):
#         return hash_simple_md5([self.name, self.ship_date.isoformat()])
#
#     @field_validator("name", mode="after")
#     def name_is_none(cls, v, info):
#         v = v or info.data.get("record").get(AmherstFields.NAME)
#         return v
#
#     @field_validator("boxes", mode="before")
#     def boxes_is_none(cls, v, info):
#         v = v if v is not None else info.data.get("record").get(AmherstFields.BOXES)
#         if not v:
#             v = 1
#         return v
#
#     @field_validator("input_address", "input_address", mode="after")
#     def input_address_is_none(cls, v, info):
#         v = v or AddressRecipient(
#             **addr_lines_dict_am(info.data.get("record").get(AmherstFields.ADDRESS)),
#             town="",
#             postcode=info.data.get("record").get(AmherstFields.POSTCODE),
#         )
#         return v
#
#     # @field_validator("contact", mode="after")
#     # def contact_is_none(cls, v, info):
#     #     # todo check api reqs vis combinations of fields
#     #     v = v or Contact(
#     #         business_name=info.data.get("record").get(AmherstFields.CUSTOMER),
#     #         email_address=info.data.get("record").get(AmherstFields.EMAIL),
#     #         mobile_phone=info.data.get("record").get(AmherstFields.TELEPHONE),
#     #         contact_name=info.data.get("record").get(AmherstFields.CONTACT),
#     #     )
#     #     return v
#
#     @field_validator("ship_date", mode="after")
#     def ship_date_validate(cls, v, info):
#         v = v or info.data.get("record").get("ship_date")
#         tod = date.today()
#         v = v if v and v > tod else tod
#         return v
#
#     @classmethod
#     def records_to_sesh(cls, records: _ty.Sequence[dict[str, str]], session: sqm.Session):
#         session.add_all([cls(record=record) for record in records])
#         session.commit()
#
#
# #
# class Hire(HireIn, table=True):
#     """Primary Hire Type"""
#
#     id: Optional[int] = Field(default=None, primary_key=True)
#     contact: Optional[Contact] = Field(sa_column=Column(ContactJson), default=None)
#
#     state: Optional["HireState"] = sqm.Relationship(back_populates="hire", link_model=HireStateLink)
#
#     def update_hire_state(self, booking_update: BookingStateUpdater, session):
#         state = self.state.update(booking_update)
#         self.state = state
#         session.add_all([self, state])
#         session.commit()
#         session.refresh(self, state)
#         return self
#
#
# class AddressRecipientDB(AddressRecipient, sqm.SQLModel, table=True):
#     id: Optional[int] = sqm.Field(default=None, primary_key=True)
