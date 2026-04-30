from langchain_core.messages import HumanMessage

from deepintshield import DeepintShield


shield = DeepintShield.from_env()
llm = shield.langchain(model="gpt-4o-mini")

response = llm.invoke([HumanMessage(content="Say hello from LangChain via DeepintShield.")])
print(response.content)
