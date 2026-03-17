import os
from openai import OpenAI

print("OPENAI_API_KEY exists:", bool(os.getenv("OPENAI_API_KEY")))
print("OPENAI_MODEL:", os.getenv("OPENAI_MODEL", "gpt-5.4"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("Client created successfully")