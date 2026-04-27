import os

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


DEFAULT_MODEL_NAME = "claude-haiku-4-5"
DEFAULT_BASE_URL = "https://litellm.6640.ucf.spencerlyon.com"


def build_model(model_name: str = DEFAULT_MODEL_NAME) -> OpenAIChatModel:
    """Build the OpenAI-compatible model served by the course LiteLLM gateway."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in .env to use the course LiteLLM gateway.")

    return OpenAIChatModel(
        model_name,
        provider=OpenAIProvider(
            base_url=os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL),
            api_key=api_key,
        ),
    )
