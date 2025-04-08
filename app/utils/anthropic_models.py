import os

import anthropic
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("CLAUDE")
client = anthropic.Anthropic(api_key=api_key)

for elem in client.models.list(limit=20):
    print(elem)