from enum import StrEnum, auto

from pydantic import BaseModel, Field


class RadioEncoding(StrEnum):
    DIGITAL = auto()
    ANALOG = auto()
    DIGITAL_TO_ANALOG = auto()
    ANALOG_TO_DIGITAL = auto()


class ChannelWidth(StrEnum):
    NARROW = auto()
    WIDE = auto()


class ChannelPower(StrEnum):
    LOW = auto()
    HIGH = auto()


class TX_ADMIT_CRITERIA(StrEnum):
    ALWAYS = auto()
    COLOR_CODE_FREE = auto()
    CHANNEL_FREE = auto()


class Channel(BaseModel):
    alias: str
    encoding: RadioEncoding
    rx_freq: int = Field(description='In Khz')
    tx_freq: int = Field(description='In Khz')
    rx_group_list: str | None = None
    privacy_code: str | None = None
    slot: int | None = None
    scan_list: str | None = None
    tx_contact: str | None = None
    emergency_system: str | None = None
    tx_admit_criteria: str = TX_ADMIT_CRITERIA.ALWAYS
    power: ChannelPower = ChannelPower.HIGH
    rx_only: bool = False
    wide_narrow: ChannelWidth = ChannelWidth.NARROW
    decode_emergency: bool = False
    decode_emergency_alarm: bool = False
    ack_emergency: bool = False
    encryption: bool = False


class Decodes(BaseModel):
    stun: bool = False
    kill: bool = False
    revive: bool = False
    radio_check: bool = False
    remote_monitor: bool = False
    private_call: bool = True
    group_call: bool = True


class ContactType(StrEnum):
    USER = auto()
    GROUP = auto()
    ALL_CALL = auto()


class Contact(BaseModel):
    id: str
    alias: str
    type: ContactType


class EmergencySystem(BaseModel):
    name: str
    type: str
    mode: str


class Group(Contact):
    type: ContactType = ContactType.GROUP


class GroupList(BaseModel):
    id: int
    alias: str
    groups: list[Group]


class Enhancements(BaseModel):
    man_down: bool = False
    gps: bool = False


class Buttons(BaseModel):
    side1_short: str | None = None
    side1_long: str | None = None
    side2_short: str | None = None
    side2_long: str | None = None
    side3_short: str | None = None
    side3_long: str | None = None
    top1_short: str | None = None
    top1_long: str | None = None
    top2_short: str | None = None
    top2_long: str | None = None
    top3_short: str | None = None
    top3_long: str | None = None

    @classmethod
    def default(cls):
        return cls(
            top1_long='EMERGENCY ON',
            top2_short='EMERGENCY OFF',
        )


class ManDown(BaseModel):
    enabled: bool = False
    interval: int | None = None  # in minutes
    warning_duration: int | None = None  # in minutes
    angle_threshold: int | None = None  # in degrees


class CodePlugAgnostic(BaseModel):
    # REQUIRED
    id: int
    alias: str
    channels: dict[int, Channel]  # key is channel number

    # OPTIONAL
    emergency: EmergencySystem | None = None
    lone_worker: bool = False
    enhancements: Enhancements | None = None
    decodes: Decodes = Field(default_factory=Decodes)
    contacts: list[Contact] = Field(default_factory=list[Contact])
    buttons: Buttons | None = Field(default_factory=Buttons.default)


if __name__ == '__main__':
    ch1 = Channel(
        alias='Channel 1',
        encoding=RadioEncoding.DIGITAL,
        rx_freq=450000,
        tx_freq=455000,
    )
    plug = CodePlugAgnostic(
        id=1,
        alias='Test Codeplug',
        channels={1:ch1},
    )
    decodes = Decodes()

