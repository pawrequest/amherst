from typing import Optional

from sqlmodel import Column, Field, JSON, Relationship, SQLModel

from amherst.models.hire_in import HireIn
from amherst.models import hire_db_parts as parts
from amherst.front.hire_ui import HireState


class HireStateDB(HireState, table=True):
    __tablename__ = "hire_state"
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id", unique=True)
    # hire: Optional[HireDB] = Relationship(back_populates="hire_state")


class HireDB(SQLModel, table=True):
    """ Primary Hire Type """
    __tablename__ = "hire"

    id: Optional[int] = Field(default=None, primary_key=True)
    cmc_in_model: HireIn = Field(sa_column=Column(JSON))

    hire_shipping_id: Optional[int] = Field(
        default=None,
        foreign_key="hireshipping.id",
        unique=True
    )
    hire_shipping: Optional[parts.HireShipping] = Relationship(
        # back_populates="hire",
        sa_relationship_kwargs={
            "primaryjoin": "HireShipping.hire_id==HireDB.id",
            "lazy": "joined",
        },
    )

    hire_dates_id: Optional[int] = Field(default=None, foreign_key="hiredates.id")
    hire_dates: Optional[parts.HireDates] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "HireDates.hire_id==HireDB.id",
            "lazy": "joined",
        },
    )

    hire_status_id: Optional[int] = Field(default=None, foreign_key="hirestatus.id")
    hire_status: Optional[parts.HireStatus] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "HireStatus.hire_id==HireDB.id",
            "lazy": "joined",
        },
    )

    hire_delivery_address_id: Optional[int] = Field(default=None, foreign_key="addressam.id")
    hire_delivery_address: Optional[parts.AddressAm] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "AddressAm.hire_id==HireDB.id",
            "lazy": "joined",
        },
    )

    hire_payment_id: Optional[int] = Field(default=None, foreign_key="hirepayment.id")
    hire_payment: Optional[parts.HirePayment] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "HirePayment.hire_id==HireDB.id",
            "lazy": "joined",
        },
    )

    hire_order_id: Optional[int] = Field(default=None, foreign_key="hireorder.id")
    hire_order: Optional[parts.HireOrder] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "HireOrder.hire_id==HireDB.id",
            "lazy": "joined",
        },
    )

    hire_staff_id: Optional[int] = Field(default=None, foreign_key="hirestaff.id")
    hire_staff: Optional[parts.HireStaff] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "HireStaff.hire_id==HireDB.id",
            "lazy": "joined",
        },
    )

    hire_state_id: Optional[int] = Field(default=None, foreign_key="hire_state.id", unique=True)
    hire_state: Optional['HireStateDB'] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "HireStateDB.hire_id==HireDB.id",
            "lazy": "joined",
        },
    )

    # @field_validator('dates', mode='after')
    # def get_dates(cls, v):
    #     dates = sub_model_from_cmc_db(parts.HireDates, hire_fxt, test_session)

    # @classmethod
    # def from_raw(cls, cmc_obj: HireRaw, session) -> Self:
    #     return cls.model_validate(
    #         dict(
    #             name=cmc_obj.name,
    #             customer=cmc_obj.customer,
    #             dates=sub_model_from_cmc_db(parts.HireDates, cmc_obj, session),
    #         )
    #     )

    # @classmethod
    # def from_raw(cls, cmc_obj: HireRaw, session) -> Self:
    #     hire = cls.model_validate(cmc_obj.model_dump())
    #     hire.hire_dates = sub_model_from_cmc_db(parts.HireDates, cmc_obj, session)
    #     # mod.status = sub_model_from_cmc_db(HireStatus, cmc_obj, session)
    #     hire.hire_shipping = sub_model_from_cmc_db(parts.HireShipping, cmc_obj, session)
    #     # mod.delivery_address = sub_model_from_cmc_db(
    #     #     parts.AddressAm,
    #     #     cmc_obj,
    #     #     session,
    #     #     prepend='delivery_'
    #     # )
    #     hire.hire_payment = sub_model_from_cmc_db(parts.HirePayment, cmc_obj, session)
    #     hire.hire_order = sub_model_from_cmc_db(parts.HireOrder, cmc_obj, session)
    #     hire.hire_staff = sub_model_from_cmc_db(parts.HireStaff, cmc_obj, session)
    #     return hire
