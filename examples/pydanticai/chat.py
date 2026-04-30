from deepintshield import DeepintShield


shield = DeepintShield.from_env()
agent = shield.pydanticai(model="gpt-4o-mini", instructions="Be concise and helpful.")

result = agent.run_sync("Say hello from PydanticAI via DeepintShield.")
print(result.output)
