from sqlmodel import SQLModel

from amherst.models.hire import Hire


class HireSql(Hire, SQLModel):
    pass
