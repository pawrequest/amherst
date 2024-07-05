from __future__ import annotations

from collections.abc import Generator

from fastapi import Body, Depends, Path
from sqlmodel import SQLModel, Session, and_, or_, select

from amherst.db import Pagination, get_pyc, get_session
from amherst.models.am_record_smpl import (
    AMHERST_TABLE_TYPES,
    AmherstCustomerDB,
    AmherstHireDB,
    AmherstSaleDB,
    dict_to_amtable,
)
from pycommence.pycommence_v2 import PyCommence


# def select_more_f_q(stmt, pagination: Pagination = Depends(Pagination.from_query)):
#     if pagination.offset:
#         stmt = stmt.offset(pagination.offset)
#     if pagination.limit:
#         stmt = stmt.limit(pagination.limit + 1)
#     return stmt


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


def search_column_stmt(model: type[SQLModel], column: str | None, search_str: str | None = None):
    if not column or not search_str:
        return select(model)
    search_ = f'%{search_str}%'
    colly = getattr(model, column)
    stmt = select(model).where(colly.ilike(search_))
    return stmt


async def model_type_from_path(csrname: str = Path(...)) -> type[SQLModel]:
    match csrname:
        case 'hire':
            return AmherstHireDB
        case 'sale':
            return AmherstSaleDB
        case 'customer':
            return AmherstCustomerDB


async def template_name_from_path(csrname: str = Path(...)):
    match csrname.lower():
        case 'hire' | 'sale':
            return 'orders.html'
        case 'customer':
            return 'customers.html'
        case _:
            raise ValueError(f'No template for {csrname}')


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


async def amrecs_and_more(
        stmt: select = Depends(stmt_from_q),
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query),
) -> tuple[list[AMHERST_TABLE_TYPES], bool]:
    return await select_and_more(stmt, session, pagination)


async def import_rows_contain_pk(
        pycmc: PyCommence = Depends(get_pyc),
        csrname: str = Path(...),
        pk_value: str = Path(...),
        session=Depends(get_session),
        model_type: type[AMHERST_TABLE_TYPES] = Depends(model_type_from_path),
) -> Generator[AMHERST_TABLE_TYPES, None, None]:
    csr = pycmc.csr(csrname)
    for row in csr.read_rows_pk_contains(pk_value):
        stmt = select(model_type).where(model_type.name == row['Name'])
        if exists := session.exec(stmt).first():
            yield exists
        amtable = dict_to_amtable(row)
        session.add(amtable)
        session.commit()
        yield amtable

        ...
