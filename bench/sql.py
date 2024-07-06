from __future__ import annotations

import contextlib
import functools

import sqlalchemy as sqa
import sqlmodel as sqm
from fastapi import Depends, Body, Path
from sqlmodel import SQLModel, select, and_, or_, Session

from amherst.db import get_session
from amherst.models.am_record_smpl import AmherstHireDB, AmherstSaleDB, AmherstCustomerDB, AMHERST_TABLE_TYPES
from amherst.route_depends import Pagination, model_type_from_path


async def model_type_from_path(csrname: str = Path(...)) -> type[SQLModel]:
    match csrname.lower():
        case 'hire':
            return AmherstHireDB
        case 'sale':
            return AmherstSaleDB
        case 'customer':
            return AmherstCustomerDB


def search_column_stmt(model: type[SQLModel], column: str | None, search_str: str | None = None):
    if not column or not search_str:
        return select(model)
    search_ = f'%{search_str}%'
    colly = getattr(model, column)
    stmt = select(model).where(colly.ilike(search_))
    return stmt


async def query_filters(
        model_type: type[SQLModel] = Depends(model_type_from_path),
        queries: dict[str, str] | None = Body(None),
) -> list:
    return [getattr(model_type, colname).ilike(f'%{val}%') for colname, val in queries.items()] if queries else []


async def stmt_from_q(
        filters: select = Depends(query_filters),
        model_type: type[SQLModel] = Depends(model_type_from_path),
        logic_operator: str = Body('and', regex='^(and|or)$')
) -> select:
    stmt = select(model_type)
    if filters:
        match logic_operator:
            case 'and':
                stmt = stmt.where(and_(*filters))
            case 'or':
                stmt = stmt.where(or_(*filters))

    return stmt


async def select_and_more(
        sqlselect,
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query)
) -> tuple[list, bool]:
    if pagination.offset:
        sqlselect = sqlselect.offset(pagination.offset)
    if pagination.limit:
        sqlselect = sqlselect.limit(pagination.limit + 1)
    res = session.exec(sqlselect).all()
    if not res:
        return [], False
    more = len(res) > pagination.limit if pagination.limit else False
    return res[: pagination.limit], more


async def amrecs_and_more(
        stmt: select = Depends(stmt_from_q),
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query),
) -> tuple[list[AMHERST_TABLE_TYPES], bool]:
    return await select_and_more(stmt, session, pagination)


async def new_amrec_f_path(
        row_id: str = Path(),
        model_type: type[SQLModel] = Depends(model_type_from_path),
        session: Session = Depends(get_session)
) -> AMHERST_TABLE_TYPES:
    ret = session.get(model_type, id)
    if not isinstance(ret, model_type):
        raise ValueError(f'No record found with id {row_id}')
    return ret


async def amrec_from_path(
        row_id: str = Path(),
        category: type[SQLModel] = Depends(model_type_from_path),
        session: Session = Depends(get_session)
):
    return session.get(category, row_id)


@functools.lru_cache(maxsize=1)
def get_engine() -> sqa.engine.base.Engine:
    connect_args = {'check_same_thread': False}
    return sqa.create_engine(settings().db_url, echo=False, connect_args=connect_args)
    # return sqa.create_engine('sqlite:///:memory:', echo=False, connect_args=connect_args)


def get_session(engine=None) -> sqm.Session:
    if engine is None:
        engine = get_engine()
    with sqm.Session(engine) as session:
        yield session


@contextlib.contextmanager
def get_session_cm(engine=None):
    if engine is None:
        engine = get_engine()
    with sqm.Session(engine) as session:
        yield session
    session.close()


def create_db(engine=None):
    if engine is None:
        engine = get_engine()
    sqm.SQLModel.metadata.create_all(engine)
