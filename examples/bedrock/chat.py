import os

from deepintshield import DeepintShield


shield = DeepintShield.from_env()
bedrock = shield.bedrock()

response = bedrock.converse(
    modelId=os.getenv("DEEPINTSHIELD_BEDROCK_MODEL", "anthropic.claude-3-sonnet-20240229"),
    messages=[{"role": "user", "content": [{"text": "Say hello from Bedrock via DeepintShield."}]}],
)

print(response)
