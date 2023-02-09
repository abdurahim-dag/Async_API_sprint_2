from pydantic import BaseModel
from .match import Match
from .term import Term
from .ids import IDS
from .nested import Nested

class QueryBool(BaseModel):
    """bool: ..."""
    must: list[Match| Nested | None ] = []
    filter: Term | IDS | None = None
