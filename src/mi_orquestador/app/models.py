from typing import Literal

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Lo que el usuario pide investigar."""

    topic: str = Field(min_length=3, description="Tema a investigar")
    sections: list[str] = ["hallazgos", "riesgos", "recomendaciones"]
    detail_level: Literal["low", "high"] = "low"

    max_sources: int = Field(default=4, ge=1, le=10)


class Source(BaseModel):
    """Un fragmento de documento que respalda una afirmación."""

    file: str
    excerpt: str
    score: float | None = None


class RouteDecision(BaseModel):
    """Decision del supervisor sobre quien actua despues."""

    next: Literal["researcher", "analyst", "synthesizer", "finish"]
    reason: str = Field(description="Una frase que explica por que")
