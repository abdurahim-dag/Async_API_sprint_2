from pydantic import BaseModel
from .match import Match
from .nested import Nested
from .term import Term
from .ids import IDS


class QueryBool(BaseModel):
    """bool: ..."""
    must: list[Match | Nested] | None
    filter: Term | IDS | None
