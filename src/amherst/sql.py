from __future__ import annotations

from fastapi import Depends, Body, Path
from sqlmodel import SQLModel, select, and_, or_

from amherst.models.am_record_smpl import AmherstHireDB, AmherstSaleDB, AmherstCustomerDB


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
