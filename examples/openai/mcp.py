"""End-to-end MCP example using the OpenAI SDK through DeepintShield.

Flow:
  1. Define tools (or fetch via ``shield.mcp.list_tools(admin_token=...)``).
  2. Send a chat completion with the tools attached.
  3. ``shield.mcp.run_openai_tool_calls`` executes any tool_calls the model
     emitted and returns the corresponding ``role: tool`` messages.
  4. Send a follow-up completion so the model can produce the final answer.
"""
import os

from deepintshield import DeepintShield, Tool


shield = DeepintShield.from_env()
openai = shield.openai()

# Server name MUST match the case-sensitive client name in MCP Registry.
SERVER = os.getenv("DEEPINTSHIELD_MCP_SERVER", "DeepWiki")
MODEL = os.getenv("DEEPINTSHIELD_MODEL", "gpt-4o-mini")

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

first = openai.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=shield.mcp.to_openai(tools),
    tool_choice="required",
)
assistant = first.choices[0].message

if not assistant.tool_calls:
    print(assistant.content)
else:
    messages.append(assistant.model_dump(exclude_none=True))
    messages.extend(shield.mcp.run_openai_tool_calls(assistant.tool_calls))
    final = openai.chat.completions.create(model=MODEL, messages=messages)
    print(final.choices[0].message.content)
