import fastapi
import fastuipr
from fastuipr import builders, components as c, events, styles

router = fastapi.APIRouter()


# @router.get('/')
@router.get('/', response_model=fastuipr.FastUI, response_model_exclude_none=True)
async def default_route():
    print('main route')
    # return fastapi.responses.RedirectResponse(url='/hire/view/1')

    return await builders.page_w_alerts(
        components=[
            c.Div.wrap(
                c.Button(
                    text='go',
                    on_click=events.GoToEvent(url='/hire/view/1'),
                    class_name=styles.BOXES_BUTTON
                ),
                class_name=styles.ROW_STYLE,
            ),
        ],
    )
