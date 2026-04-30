"""Compose individual guard nodes manually for fine-grained control."""
import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph

from deepintshield import DeepintShield


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    shield_blocked: bool
    shield_reason: str


def agent_node(state: AgentState):
    return {"messages": [AIMessage(content=f"Responding to: {state['messages'][-1].content}")]}


shield = DeepintShield.from_env()
lg = shield.langgraph()

graph = StateGraph(AgentState)
graph.add_node("input_guard", lg.input_guard)
graph.add_node("agent", agent_node)
graph.add_node("output_guard", lg.output_guard)
graph.set_entry_point("input_guard")
graph.add_conditional_edges("input_guard", lambda s: END if s.get("shield_blocked") else "agent")
graph.add_edge("agent", "output_guard")
graph.add_conditional_edges("output_guard", lambda _s: END)

app = graph.compile()
result = app.invoke({"messages": [HumanMessage(content="Summarize the policy safely.")]})
print(result["messages"][-1].content)
