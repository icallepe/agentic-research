from collections.abc import Iterator
from contextlib import contextmanager

from langgraph.checkpoint.memory import InMemorySaver

from agentic_research.app.config import REDIS_URL


@contextmanager
def get_checkpointer() -> Iterator:
    """Checkpointer de LangGraph: Redis si hay REDIS_URL, memoria si no.

    Uso:
        with get_checkpointer() as saver:
            grafo = builder.compile(checkpointer=saver)
    """
    if not REDIS_URL:
        yield InMemorySaver()
        return

    from langgraph.checkpoint.redis import RedisSaver

    with RedisSaver.from_conn_string(REDIS_URL) as saver:
        saver.setup()
        yield saver
