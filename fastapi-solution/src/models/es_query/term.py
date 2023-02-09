from pydantic import BaseModel


# Поле term
class Term(BaseModel):
    """filter: ..."""
    #term: FieldGenreID
    term: dict
