import operator
from typing import Annotated, TypedDict

class ResearchState(TypedDict, total=False):
    topic: str
    sections: list[str]
    detail_level: str

    contributions: Annotated[list[dict], operator.add]
    references: Annotated[list[dict], operator.add]

    next_route: str
    step_count: int
    delegation_trace: Annotated[list[dict], operator.add]


    draft: str

    feedback: str
    revision: int
    approved: bool


def current(items: list[dict], state: ResearchState) -> list[dict]:
    """Devuelve solo los aportes de la revisión actual"""
    rev = state.get("revision", 0)
    return [i for i in items if i.get("revision", 0) == rev]
