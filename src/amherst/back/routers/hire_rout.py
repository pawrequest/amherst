# from __future__ import annotations
from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from amherst.back.database import get_cmc, get_session
from amherst.front.amui import am_default_page, hire_row
from amherst.models.hire import HireTable,  Hire
from pawsupport import fastui_ps as fuis
from pycommence import Cmc, get_csr

router = APIRouter()

PAGE_SIZE = 20


# # FastUI
# @router.get("/{hire_name}", response_model=FastUI, response_model_exclude_none=True)
# async def hire_view(hire_name: str) -> list[AnyComponent]:
#     # cursor = Depends....
#     dummy = "NOOR Relief Fund (NRF) - 08/12/2023 ref 31808"
#     # hire = Hire.from_name(hire_name)
#     hire = Hire.from_name(dummy)
#
#     bl = fuis.back_link()
#     hire_ro = hire_row(hire)
#     title = hire.name
#
#     page = am_default_page([bl, hire_ro], title)
#     return page

#
# FastUI
# @router.get("/{hire_name_b64}", response_model=FastUI, response_model_exclude_none=True)
# async def hire_view2(hire_name: str) -> list[AnyComponent]:
#     # cursor = Depends....
#     # hire = Hire.from_name(hire_name)
#     hire_name = base64_decode(hire_name)
#     hire = Hire.from_name(hire_name)
#
#     bl = fuis.back_link()
#     hire_ro = hire_row(hire)
#     title = hire.name
#
#     page = am_default_page([bl, hire_ro], title)
#     return page


@router.get("/{hire_id}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view2(hire_id: int, session=Depends(get_session)) -> list[AnyComponent]:
    hire = session.get(HireTable, hire_id)
    hb = Hire.model_validate(hire)

    bl = fuis.back_link()
    hire_ro = hire_row(hire)
    title = hire.name

    page = am_default_page([bl, hire_ro], title)
    return page


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def hire_list_view(
        page: int = 1, customer: str | None = None, cmc: Cmc = Depends(get_cmc)
) -> list[AnyComponent]:
    data, filter_form_initial = hire_filter_init(customer, cmc)
    # data.sort(key=lambda x: x.date, reverse=True)

    total = len(data)
    data = data[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]

    return am_default_page(
        title="Hires",
        components=[
            hire_filter(filter_form_initial),
            [hire_row(hire) for hire in data],
            c.Pagination(page=page, page_size=PAGE_SIZE, total=total),
        ],
    )


#

def hire_filter_init(customer: str, cmc: Cmc):
    filter_form_initial = {}
    cursor = get_csr('Hire')
    if customer:
        cursor.filter_by_field("Customer", 'Equal To', customer)
        data = cursor.get_all_records()
        data = [HireTable.from_record(_) for _ in data]
        filter_form_initial["customer"] = {"value": customer, "label": customer}
    else:
        data = cursor.get_all_records()
    return data, filter_form_initial


def hire_filter(filter_form_initial):
    return c.ModelForm(
        model=HireCustomerFilter,
        submit_url=".",
        initial=filter_form_initial,
        method="GOTO",
        submit_on_change=True,
        display_mode="inline",
    )


class HireCustomerFilter(BaseModel):
    customer: str = Field(
        # json_schema_extra={"search_url": "/api/forms/episodes/", "placeholder": "Filter by Guru..."}
        json_schema_extra={
            "search_url": "/api/forms/search/hire/",
            "placeholder": "Filter by Customer...",
        }
    )
