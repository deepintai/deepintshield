"""End-to-end MCP example using the Anthropic SDK through DeepintShield."""
import os

from deepintshield import DeepintShield, Tool


shield = DeepintShield.from_env()
anthropic = shield.anthropic()

SERVER = os.getenv("DEEPINTSHIELD_MCP_SERVER", "DeepWiki")
MODEL = os.getenv("DEEPINTSHIELD_ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

tools = [
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

messages = [
    {
        "role": "user",
        "content": "Use DeepWiki to summarize how facebook/react organizes its reconciler.",
    }
]

response = anthropic.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=shield.mcp.to_anthropic(tools),
    messages=messages,
)

if response.stop_reason == "tool_use":
    # Append the assistant turn, then the tool_results as the next user turn.
    messages.append({"role": "assistant", "content": [block.model_dump() for block in response.content]})
    messages.append(
        {"role": "user", "content": shield.mcp.run_anthropic_tool_uses(response.content)}
    )
    final = anthropic.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=shield.mcp.to_anthropic(tools),
        messages=messages,
    )
    for block in final.content:
        if getattr(block, "type", None) == "text":
            print(block.text)
else:
    for block in response.content:
        if getattr(block, "type", None) == "text":
            print(block.text)
