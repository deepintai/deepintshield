"""Gate OpenAI Agents SDK function tools through the PDP."""
import asyncio

from agents import Agent, Runner, function_tool

from deepintshield import DeepintShield


shield = DeepintShield.from_env()
shield.openai_agents().apply()


@function_tool
def delete_record(record_id: str) -> str:
    return f"deleted {record_id}"


agent = Agent(name="Ops", instructions="Use the tools.", tools=[delete_record])
shield.agentic.openai_agents(agent)  # gate every FunctionTool on the agent

print(asyncio.run(Runner.run(agent, "delete record 42")).final_output)
