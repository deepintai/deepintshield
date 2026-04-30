# deepintshield — examples

Each subfolder has `chat.py`, `rag.py`, and (where relevant) `agent.py` that
run through the new `deepintshield` SDK. Set `DEEPINTSHIELD_VIRTUAL_KEY` first.

```bash
export DEEPINTSHIELD_VIRTUAL_KEY="sk-..."
python examples/openai/chat.py
python examples/anthropic/rag.py
python examples/langgraph/agent.py
```

Every example uses the real provider SDK. The only DeepintShield-specific line
is `shield = DeepintShield.from_env()` and `shield.<provider>()`.
