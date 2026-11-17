import pytest

from agentic_research.app.graph import apply_rules, forced_route


@pytest.mark.parametrize("llm_next", ["analyst", "synthesizer", "finish"])
def test_sin_investigacion_solo_puede_investigar(llm_next):
    ruta, _ = apply_rules(llm_next, has_r=False, has_a=False, has_d=False)
    assert ruta == "researcher"

def test_con_investigacion_no_termina_sin_borrador():
    assert apply_rules("finish", has_r=True, has_a=False, has_d=False)[0] == "analyst"
    assert apply_rules("finish", has_r=True, has_a=True, has_d=False)[0] == "synthesizer"

def test_no_repite_investigacion():
    assert apply_rules("researcher", has_r=True, has_a=True, has_d=False)[0] == "synthesizer"

def test_no_repite_analisis():
    assert apply_rules("researcher", has_r=True, has_a=True, has_d=True)[0] == "finish"

def test_decision_correcta_del_llm_se_respeta():
    ruta, nota = apply_rules("analyst", has_r=True, has_a=False, has_d=False)
    assert ruta == "analyst"
    assert nota == ""

def test_limite_de_pasos():
    assert forced_route(has_r=False, has_d=False) == "finish"
    assert forced_route(has_r=True, has_d=False) == "synthesizer"
    assert forced_route(has_r=True, has_d=True) == "finish"