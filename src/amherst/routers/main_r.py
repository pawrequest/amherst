import fastapi
from fastui import FastUI, components as c, events

from pawdantic.pawui import builders, styles
from ..front import styles as am_styles

router = fastapi.APIRouter()


# @router.get('/')
@router.get('/', response_model=FastUI, response_model_exclude_none=True)
async def default_route():
    print('main route')
    # return fastapi.responses.RedirectResponse(url='/hire/view/1')

    return await builders.page_w_alerts(
        components=[
            builders.wrap_divs(
                components=[
                    c.Button(
                        text='go',
                        on_click=events.GoToEvent(url='/hire/view/1'),
                        class_name=am_styles.BOXES_BUTTON
                    ),
                ],
                class_name=styles.ROW_STYLE,
            ),
        ],
    )
