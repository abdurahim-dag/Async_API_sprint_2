from pydantic import BaseModel
from .qbool import QueryBool


class Query(BaseModel):
    """query: ..."""
    bool: QueryBool = QueryBool()


