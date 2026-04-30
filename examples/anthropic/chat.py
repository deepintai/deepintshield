import os

from deepintshield import DeepintShield


shield = DeepintShield.from_env()
anthropic = shield.anthropic()

response = anthropic.messages.create(
    model=os.getenv("DEEPINTSHIELD_ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
    max_tokens=256,
    messages=[{"role": "user", "content": "Say hello from Anthropic via DeepintShield."}],
)

print(response.content[0].text)
