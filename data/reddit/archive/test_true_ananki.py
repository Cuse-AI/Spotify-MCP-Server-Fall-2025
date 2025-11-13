"""
Quick test to see what Claude responds with
"""
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

prompt = """You are Ananki. A human recommended "Goodbye Stranger" by Supertramp from a post titled "What's your favorite feel good song?"

Available sub-vibes: Happy - Feel Good, Happy - Euphoric, Happy - Sunshine, Happy - Carefree, Happy - Celebration

Which sub-vibe? Respond in JSON: {"sub_vibe": "Happy - Feel Good", "reasoning": "...", "confidence": 0.9}"""

message = client.messages.create(
    model="claude-sonnet-4-5",  # Claude Sonnet 4.5 (latest)
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}]
)

print("Claude's response:")
print(message.content[0].text)
