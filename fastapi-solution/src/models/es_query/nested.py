from pydantic import BaseModel
from .match import match_field
from typing import ForwardRef

QueryRef = ForwardRef("Query")

# Поиск по вложенные полям.
class NestedInner(BaseModel):
    """nested: ..."""
    path: str
    query: QueryRef


# Поиск по вложенные полям.
class Nested(BaseModel):
    """must: ..."""
    nested: NestedInner

def nested(path: str) -> Nested:
    from .query import Query, QueryBool
    query = Query(bool=QueryBool(must = []))
    nested_inner = NestedInner(
        path=path,
        query=query,
    )
    return Nested(nested=nested_inner)