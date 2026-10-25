# agentic-research

Asistente de investigación multi-agente. Indexa documentos propios (RAG con ChromaDB) y un equipo de agentes coordinado por un supervisor los investiga, analiza y redacta un informe con las fuentes citadas.

## Cómo funciona

```mermaid
graph TD;
    __start__ --> supervisor
    supervisor -.-> researcher
    supervisor -.-> analyst
    supervisor -.-> synthesizer
    supervisor -.-> __end__
    researcher --> supervisor
    analyst --> supervisor
    synthesizer --> supervisor
```

Un **supervisor** (LLM + reglas en código) decide en cada paso quién actúa:

| Agente | Qué hace |
| --- | --- |
| `researcher` | Busca en los documentos indexados con la herramienta `search_documents` (2-3 consultas) y resume los hallazgos citando archivos. |
| `analyst` | Calcula métricas deterministas sobre la evidencia (fragmentos por archivo, porcentajes, etc.) y evalúa su solidez y contradicciones. |
| `synthesizer` | Redacta el informe final con las secciones y el nivel de detalle pedidos. |

Las reglas en código corrigen al LLM cuando propone un paso inválido (por ejemplo, sintetizar sin investigación previa) y el flujo se corta a los 8 pasos (`MAX_STEPS`). Cada decisión queda en `delegation_trace`.

## Requisitos

- Python 3.14 o superior
- [uv](https://docs.astral.sh/uv/)
- Una clave de OpenAI

## Instalación

```powershell
uv sync
```

Crea un archivo `.env` en la raíz con tu clave:

```
OPENAI_API_KEY=sk-...
```

Modelos usados: `gpt-4o-mini` (chat) y `text-embedding-3-small` (embeddings), configurables en `src/agentic_research/app/config.py`.

## Uso

Todo se hace desde la raíz del proyecto con el comando `agentic-research`:

```powershell
# 1. Indexar los documentos de src/agentic_research/data/
uv run agentic-research index

# 2. Investigar un tema con el equipo de agentes
uv run agentic-research research "abandono en el registro de la app"
uv run agentic-research research "abandono en el registro de la app" --detail high

# Preguntar directamente a los documentos (RAG simple)
uv run agentic-research ask "¿qué porcentaje abandona en el paso del SMS?"

# Borrar el índice
uv run agentic-research reset
```

`research` imprime la traza del supervisor (qué agente actuó y por qué) y después el borrador del informe. `--detail` acepta `low` (por defecto, breve) o `high` (con cifras y fuentes).

## Estructura

```
src/agentic_research/
├── app/
│   ├── main.py             CLI (index, reset, ask, research)
│   ├── graph.py            Grafo de LangGraph, supervisor y reglas
│   ├── agents.py           researcher, analyst y synthesizer
│   ├── supervisor_brain.py Decisión de ruta del supervisor (LLM)
│   ├── state.py            ResearchState compartido entre nodos
│   ├── models.py           Modelos Pydantic (ResearchRequest, Source, RouteDecision)
│   ├── rag.py              Indexación y búsqueda con ChromaDB
│   ├── qa.py               Preguntas y respuestas sobre los documentos
│   ├── llm.py              Cliente del LLM
│   └── config.py           Configuración y variables de entorno
├── data/                   Documentos a investigar (.md)
└── domain/                 Prácticas numeradas (practica1.py ... practica24.py)
```

Las prácticas de `domain/` son ejercicios sueltos. Se ejecutan desde la raíz con:

```powershell
uv run python src/agentic_research/domain/practica23.py
```

`practica23.py` imprime el diagrama Mermaid del grafo (guardado también en `grafo.mmd`).

## Stack

LangGraph, LangChain, ChromaDB, OpenAI y Pydantic.
