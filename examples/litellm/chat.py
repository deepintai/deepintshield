import os

from deepintshield import DeepintShield


shield = DeepintShield.from_env()

response = shield.litellm().completion(
    model=os.getenv("DEEPINTSHIELD_LITELLM_MODEL", "gpt-4o-mini"),
    messages=[{"role": "user", "content": "Say hello from LiteLLM via DeepintShield."}],
)

print(response.choices[0].message.content)
