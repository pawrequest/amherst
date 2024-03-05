import fastapi

import fastuipr
from fastuipr import builders, events

router = fastapi.APIRouter()


# @router.get('/')
@router.get('/', response_model=fastuipr.FastUI, response_model_exclude_none=True)
async def default_route():
    print('main route')
    # return fastapi.responses.RedirectResponse(url='/hire/view/1')

    return await builders.page_w_alerts(
        components=[
            fastuipr.components.Button(
                text='go',
                on_click=events.GoToEvent(url='/hire/view/1')
            ),
        ],
    )
