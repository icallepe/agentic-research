from typing import Literal

from pydantic import  Basemodel, Field

class ResearchRequest(BaseModel):
    ""lo que el usuario pide ivestigar.""

    topic: str = Field(min_length=3, description="Tema a investigar")
    sections: list[str] = ["hallazgos", "riesgos", "recoemndaciones"]
    detail_level: Literal["low", "high"] = "low"

class Source(BaseModel):
    ""Un fragmento de documento que respalda una afirmación""

    file: str
    excerpt: str