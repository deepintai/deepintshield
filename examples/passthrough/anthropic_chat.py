from deepintshield import DeepintShield


shield = DeepintShield.from_env()
anthropic = shield.anthropic(passthrough=True)

response = anthropic.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello from Anthropic passthrough."}],
)

print(response.content[0].text)
