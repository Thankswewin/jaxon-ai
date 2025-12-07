import os
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MEM0_API_KEY")
user_id = os.getenv("USER_ID", "jaxon_user")

print(f"Checking memories for User ID: {user_id}")
print(f"API Key present: {bool(api_key)}")

if not api_key:
    print("Error: MEM0_API_KEY not found in .env")
    exit()

client = MemoryClient(api_key=api_key)

try:
    # get_all is the method to retrieve all memories
    memories = client.get_all(filters={"user_id": user_id})
    print(f"Found {len(memories)} memories.")
    for i, mem in enumerate(memories[:20]): # Print first 20
        print(f"[{i}] {mem.get('memory', 'No memory text')} (ID: {mem.get('id')})")
except Exception as e:
    print(f"Error retrieving memories: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")
