from typing import Annotated

import fastapi
from fastui.forms import fastui_form
from fastui import FastUI, components as c

from amherst.front import ui_helpers
from amherst.front.pages.hire_page import PostcodeSelect

router = fastapi.APIRouter()


@router.post('/postcode', response_model=FastUI, response_model_exclude_none=True)
async def postcode_post(form: Annotated[PostcodeSelect, fastui_form(PostcodeSelect)]):
    print(form)
    return await ui_helpers.page_w_alerts(
        components=[c.Text(text="Form submitted"),
                    c.Text(text=f"Postcode: {form.postcode}")],
        title="Postcode submitted"
    )
