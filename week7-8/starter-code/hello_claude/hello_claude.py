import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=256,
    system="You are a helpful assistant. Be concise.",
    messages=[{"role": "user", "content": "What is a mesh network?"}],
)

print(response.content[0].text)
