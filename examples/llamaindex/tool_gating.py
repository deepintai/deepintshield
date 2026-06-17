"""Gate LlamaIndex FunctionTools through the PDP."""
from llama_index.core.tools import FunctionTool

from deepintshield import DeepintShield


shield = DeepintShield.from_env()


def transfer_funds(amount: float) -> str:
    """Transfer funds between accounts."""
    return f"transferred {amount}"


tool = FunctionTool.from_defaults(fn=transfer_funds)
gated = shield.agentic.llamaindex([tool])  # decide() runs before .call()
print(gated[0].call(amount=10.0))
