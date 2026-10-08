from typing import Literal

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    topic: str
    sections: list[str]
    detail_level: Literal["low", "high"]
