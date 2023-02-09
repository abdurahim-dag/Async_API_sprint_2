from pydantic import BaseModel
from .term import Term
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


def nested(path: str, field: str, value) -> Nested:
    from .query import Query, QueryBool

    query = Query(bool=QueryBool())
    term = Term(
        term={field: value}
    )
    query.bool.filter = term
    nested_inner = NestedInner(
        path=path,
        query=query,
    )
    return Nested(nested=nested_inner)