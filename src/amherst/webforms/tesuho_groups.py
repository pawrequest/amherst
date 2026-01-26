from pydantic import BaseModel


class TesunhoGroup(BaseModel):
    name: str
    members: list[str] = Field(default_factory=list[str])
