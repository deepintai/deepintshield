"""Gate the tools registered on a PydanticAI agent through the PDP."""
from pydantic_ai import Agent

from deepintshield import DeepintShield


shield = DeepintShield.from_env()
agent = Agent(shield.pydanticai().model("gpt-4o-mini"))


@agent.tool_plain
def charge_card(amount: float) -> str:
    return f"charged {amount}"


shield.agentic.pydanticai(agent)  # gate registered tool functions
print(agent.run_sync("charge 9.99 to the card").output)
