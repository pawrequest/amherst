from sqlmodel import SQLModel

from amherst.commence_am.hire import Hire


class HireSql(Hire, SQLModel):
    pass
