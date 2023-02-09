from pydantic import BaseModel


# Поиск по id в filter
class IDSValues(BaseModel):
    """ids: ..."""
    values: list[str] = []


# Поиск по id в filter
class IDS(BaseModel):
    """filter: ..."""
    ids: IDSValues = IDSValues()


def ids(values: list[str] = []) -> IDS:
    ids = IDSValues(values=values)
    return IDS(ids=ids)