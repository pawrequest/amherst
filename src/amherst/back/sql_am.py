from sqlmodel import SQLModel

from amherst.models.hire import HireTable


class HireSql(HireTable, SQLModel):
    pass
