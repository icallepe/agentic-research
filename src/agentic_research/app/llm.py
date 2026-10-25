from langchain_openai import ChatOpenAI

from agentic_research.app.config import MODEL_NAME, check_config


def get_llm(temperature: float = 0) -> ChatOpenAI:
    check_config()
    return ChatOpenAI(model=MODEL_NAME, temperature=temperature)


def usage_summary(message) -> str:
    u = message.usage_metadata or {}
    return (
        f"tokens: entrada={u.get('input_tokens', 0)} "
        f"salida={u.get('output_tokens', 0)} total={u.get('total_tokens', 0)}"
    )
