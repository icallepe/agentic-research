from agentic_research.app.config import K_BUSQUEDA, QUEJAS_CSV
from agentic_research.app.models import Source

print(QUEJAS_CSV, K_BUSQUEDA)
print(Source(file="queja 1", excerpt="texto", company="Acme"))
