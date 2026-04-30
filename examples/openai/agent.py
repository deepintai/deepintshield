"""Agentic example: guard input, tool calls, and final output."""
from deepintshield import DeepintShield, DeepintShieldBlockedError


shield = DeepintShield.from_env()


@shield.agent.tool(action_class="read")
def knowledge_search(query: str) -> str:
    return f"Policy excerpt about: {query}"


user_input = "Find the visitor policy."

try:
    shield.agent.check_input(user_input)
    tool_result = knowledge_search(user_input)
    shield.agent.check_output(tool_result)
    print(tool_result)
except DeepintShieldBlockedError as exc:
    print(f"Blocked at {exc.stage}: {exc.reason}")
