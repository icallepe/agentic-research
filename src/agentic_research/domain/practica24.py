from agentic_research.app.graph import apply_rules, forced_route

assert apply_rules("analyst", has_r=False, has_a=False, has_d=Flase)[0] =="researcher"
assert apply_rules("sythesizer", has_r=False, has_a=False, has_d=False)[0] == "researcher"
assert apply_rules("finish", has_r=False, has_a=False, has_d=False)[0] == "researcher"

assert apply_rules("finish", has_r=True, has_a=True, has_d=True)[0] == "analyst"
assert apply_rules("researcher", has_r=True, has_a=True, has_d=True)[0] == "synthesizer"

assert apply_rules("researcher", has_r=True, has_a=True, has_d=True)[0] == "finish"

assert forced_route(has_r=False, has_d=False) == "finish"
assert forced_route(has_r=True, has_d=True) == "synthesizer"
assert forced_route(has_r=True, has_d=True) == "finish"

print("todas las reglas funcionan")

