import fastapi
from fastui import FastUI, components as c, events

from pawdantic.pawui import builders

router = fastapi.APIRouter()


# @router.get('/')
@router.get('/', response_model=FastUI, response_model_exclude_none=True)
async def default_route():
    print('main route')
    # return fastapi.responses.RedirectResponse(url='/hire/view/1')

    return await builders.page_w_alerts(
        components=[
            c.Div(
                class_name=' row my-5 mx-auto',
                components=[
                    c.Button(
                        text='go',
                        on_click=events.GoToEvent(url='/ship/view/1'),
                        class_name='btn btn-primary h-300px',

                    ),
                ],
            ),
        ],
    )
