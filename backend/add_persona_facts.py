import os
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

# Facts to inject
facts = [
    "Your full name is Jaxon Elijah McKnight.",
    "You are 32 years old.",
    "You are from Atlanta and were raised in New Orleans.",
    "You are 6 feet 3 inches tall (6'3\").",
    "You have green eyes.",
    "The user's nail app is named NailMuse."
]

print("Injecting persona facts...")

# We'll add these as a 'system' or 'user' instruction to ensure they are memorized.
# Using 'user' role saying "Remember that..." is usually effective.
messages = []
for fact in facts:
    messages.append({"role": "user", "content": f"Remember this fact: {fact}"})
    messages.append({"role": "assistant", "content": f"Understood. {fact.replace('Your', 'My').replace('You are', 'I am').replace('The user', 'Your')}"})

try:
    # Add as a single batch or separate? 
    # Separate might be better to ensure each is distinct.
    for i in range(0, len(messages), 2):
        pair = messages[i:i+2]
        print(f"Adding: {pair[0]['content']}")
        client.add(pair, user_id=user_id, metadata={"source": "manual_persona_injection", "timestamp": "2025-11-30T12:00:00"})
    print("Persona facts injected successfully.")
except Exception as e:
    print(f"Error injecting facts: {e}")
