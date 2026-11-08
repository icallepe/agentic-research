from agentic_research.app.config import PHOENIX_ENDPOINT


def setup_tracing() -> None:
    """Activa las trazas hacia Phoenix si esta configurado; si no, no hace nada."""
    if not PHOENIX_ENDPOINT:
        return
    from phoenix.otel import register

    register(
        project_name="research-assistant",
        endpoint=PHOENIX_ENDPOINT,
        auto_instrument=True,  # detecta LangChain/LangGraph automaticamente
    )
