from deepintshield import DeepintShield


shield = DeepintShield.from_env()
openai = shield.openai(passthrough=True)

response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello from OpenAI passthrough."}],
)

print(response.choices[0].message.content)
