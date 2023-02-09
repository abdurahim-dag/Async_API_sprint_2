from pydantic import BaseModel, Field


# Внутренности, для полей поиска.
class MatchFieldQuery(BaseModel):
    """[field_name]: ..."""
    query: str
    fuzziness: str = Field(default='AUTO')


class Match(BaseModel):
    """must: ..."""
    match: dict


def match_field(field_name: str, query: str):
    mfq = MatchFieldQuery(query=query)
    m = Match(match={field_name: mfq})
    return m
