import os
from mem0 import MemoryClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Mem0 client
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

print("Checking memories for user:", user_id)
print("Searching memories for user:", user_id)
try:
    # Search for the specific facts
    filters = {"user_id": user_id}
    
    results_school = client.search("ISCOM", version="v2", filters=filters)
    print("School Search Results:", results_school)

    results_nails = client.search("acrylic", version="v2", filters=filters)
    print("Nails Search Results:", results_nails)
    
except Exception as e:
    print(f"Error searching memories: {e}")
