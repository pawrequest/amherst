import fastapi
from fastui import FastUI, components as c, events

from pawdantic.pawui import builders

router = fastapi.APIRouter()


# @router.get('/')
@router.get('/', response_model=FastUI, response_model_exclude_none=True)
async def default_route():
    print('main route')
    return c.FireEvent(event=events.GoToEvent(url='/ship/select/1'))
    # return c.FireEvent(event=events.GoToEvent(url='/ship_model/zero/1'))

    # return await builders.page_w_alerts(
    #     # page_class_name='',
    #     components=[
    #         c.Div(
    #             class_name=' row my-5 mx-auto',
    #             components=[
    #                 c.Button(
    #                     text='go',
    #                     # on_click=events.GoToEvent(url='/forms_test/login/1'),
    #                     on_click=events.GoToEvent(url='/ship_model/zero/1'),
    #                     # on_click=events.GoToEvent(url='/ship/select/1'),
    #                     class_name='btn btn-primary h-300px ',
    #
    #                 ),
    #             ],
    #         ),
    #     ],
    # )
