from deepintshield import DeepintShield


shield = DeepintShield.from_env()
genai = shield.genai(passthrough=True)

response = genai.models.generate_content(
    model="gemini-1.5-flash",
    contents="Hello from GenAI passthrough.",
)

print(response.text)
