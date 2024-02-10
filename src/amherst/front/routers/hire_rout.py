# from __future__ import annotations
from amherst.front.amui import am_default_page, hire_row
from amherst.models.hire import Hire
from fastui import AnyComponent, FastUI
from fastapi import APIRouter
from pawsupport import fastui_ps as fuis

router = APIRouter()


# FastUI
@router.get("/{hire_name}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view(hire_name: str) -> list[AnyComponent]:
    # cursor = Depends....
    dummy = "NOOR Relief Fund (NRF) - 08/12/2023 ref 31808"
    # hire = Hire.from_name(hire_name)
    hire = Hire.from_name(dummy)

    bl = fuis.back_link()
    hire_ro = hire_row(hire)
    title = hire.name

    page = am_default_page([bl, hire_ro], title)
    return page

#
# @router.get("/", response_model=FastUI, response_model_exclude_none=True)
# def episode_list_view(
#     page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)
# ) -> list[AnyComponent]:
#     logger.info("episode_filter")
#     data, filter_form_initial = guru_filter_init(guru_name, session, Episode)
#     data.sort(key=lambda x: x.date, reverse=True)
#
#     total = len(data)
#     data = data[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]
#
#     return dtg_default_page(
#         title="Episodes",
#         components=[
#             guru_filter(filter_form_initial, "episodes"),
#             objects_ui_with(data),
#             c.Pagination(page=page, page_size=PAGE_SIZE, total=total),
#         ],
#     )
#
#
# def guru_filter_init(guru_name, session, clazz):
#     filter_form_initial = {}
#     if guru_name:
#         guru = session.exec(select(Guru).where(Guru.name == guru_name)).one()
#         # data = guru.episodes
#         statement = select(clazz).where(clazz.gurus.any(Guru.id == guru.id))
#         data = session.exec(statement).all()
#         filter_form_initial["guru"] = {"value": guru_name, "label": guru.name}
#     else:
#         data = session.query(clazz).all()
#     return data, filter_form_initial
