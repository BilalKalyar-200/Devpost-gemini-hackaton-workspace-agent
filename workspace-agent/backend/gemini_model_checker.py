from google.genai import Client
from config import config

client = Client(api_key=config.GEMINI_API_KEY)

print("Listing available models...")
for m in client.models.list():
    print(m.name)
