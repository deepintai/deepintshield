"""LangChain agent example using DeepintShield-managed MCP tools.

The same pattern works for LangGraph: pass the tool list to a ``ToolNode``.
"""
import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from deepintshield import DeepintShield, Tool


shield = DeepintShield.from_env()
llm = shield.langchain(model=os.getenv("DEEPINTSHIELD_MODEL", "gpt-4o-mini"))

SERVER = os.getenv("DEEPINTSHIELD_MCP_SERVER", "DeepWiki")

tool_specs = [
    Tool(
        server=SERVER,
        name="ask_question",
        description="Ask a free-form question about a public GitHub repository.",
        schema={
            "type": "object",
            "properties": {
                "repoName": {"type": "string", "description": "owner/name"},
                "question": {"type": "string"},
            },
            "required": ["repoName", "question"],
        },
    ),
]

tools = shield.mcp.to_langchain(tool_specs)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You answer questions about GitHub repositories using DeepWiki tools."),
        ("user", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

result = executor.invoke(
    {"input": "Summarize how facebook/react organizes its reconciler."}
)
print(result.get("output", ""))
