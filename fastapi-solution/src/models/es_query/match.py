from pydantic import BaseModel, Field


# Внутренности, для полей поиска.
class MatchFieldQuery(BaseModel):
    """[field_name]: ..."""
    query: str = ''
    fuzziness: str = ''


class Match(BaseModel):
    """must: ..."""
    match: dict = {}


def match_field(field_name: str, query: str, fuzziness: str = 'AUTO'):
    mfq = MatchFieldQuery(query=query, fuzziness=fuzziness)
    m = Match(match={field_name: mfq})
    return m
