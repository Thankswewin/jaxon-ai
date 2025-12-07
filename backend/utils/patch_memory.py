import os
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

# Facts to inject
facts = [
    "The first thing the user ever said to you was '안녕하세요.' (Hello in Korean).",
    "The user did nail designs for their sister-in-law. The user described it as: 'We have a predicament. How can we fix this? My sister's nails...'",
    "The user studied at a university in Nigeria for their undergraduate degree. (Likely mentioned in context of 'National Univ' or similar)."
]

print("Injecting recovered facts...")

messages = []
for fact in facts:
    messages.append({"role": "user", "content": f"Remember this historical fact: {fact}"})
    messages.append({"role": "assistant", "content": f"Understood. I will remember that: {fact}"})

try:
    client.add(messages, user_id=user_id, metadata={"source": "manual_fact_recovery", "timestamp": "2025-11-30T12:00:00"})
    print("Recovered facts injected successfully.")
except Exception as e:
    print(f"Error injecting facts: {e}")
