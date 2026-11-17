import pytest
from pydantic import ValidationError

from agentic_research.app.agents import analyze_evidence
from agentic_research.app.models import ResearchRequest, ReviewRequest


def test_request_valida():
    r = ResearchRequest(topic="abandono del registro")
    assert r.detail_level == "low"

@pytest.mark.parametrize("campos", [{"topic": "a"}, {"topic": "abandono", "detail_level": "medio"}])
def test_request_invalida(campos):
    with pytest.raises(ValidationError):
        ResearchRequest(**campos)

def test_cambios_requieren_comentario():
    with pytest.raises(ValidationError):
        ReviewRequest(action="changes")
    assert ReviewRequest(action="changes", feedback="mas detalle").feedback == "mas detalle"
    assert ReviewRequest(action="approve").action == "approve"

def test_analyze_evidence_cuenta_y_agrupa():
    refs = [
        {"file": "a.md", "excerpt": "El abandono es de 41%."},
        {"file": "a.md", "excerpt": "Android 52% y iOS 33%."},
        {"file": "b.md", "excerpt": "Sin cifras aqui."},
    ]

    m = analyze_evidence(refs)
    assert m["num_fragmentos"] == 3
    assert m["num_archivos"] == 2
    assert m["fragmentos_por_archivo"] == {"a.md": 2, "b.md": 1}
    assert m["porcentajes_por_archivo"] == {"a.md" : ["41%", "52%", "33%"]}