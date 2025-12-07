import os
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

queries = [
    "Jaxon Elijah McKnight",
    "32 years old",
    "Atlanta",
    "6'3",
    "green eyes"
]

print("Checking for persona details in Mem0...")
for q in queries:
    try:
        filters = {"user_id": user_id}
        results = client.search(q, version="v2", filters=filters)
        if isinstance(results, dict) and 'results' in results:
            memories = results['results']
        else:
            memories = results
            
        print(f"Query '{q}': Found {len(memories)} memories.")
        for m in memories[:2]:
            print(f" - {m.get('memory', 'No text')}")
            
    except Exception as e:
        print(f"Error searching '{q}': {e}")

print("\nIf counts are 0, we need to add them.")
