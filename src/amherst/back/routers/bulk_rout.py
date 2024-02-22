from fastui import AnyComponent
from pydantic import BaseModel, Field

from amherst.models import HireTable
from pycommence import get_csr


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def hire_list_view(
        page: int = 1, customer: str | None = None, cmc: Cmc = Depends(get_cmc)
) -> list[AnyComponent]:
    # data, filter_form_initial = hire_filter_init(customer, cmc)
    # data.sort(key=lambda x: x.date, reverse=True)

    total = len(data)
    data = data[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]

    return Page.amherst(
        title="Hires",
        components=[
            # hire_filter(filter_form_initial),
            [Row.hire(hire) for hire in data],
            c.Pagination(page=page, page_size=PAGE_SIZE, total=total),
        ],
    )




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
