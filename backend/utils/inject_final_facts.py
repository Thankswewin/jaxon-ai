import os
from mem0 import MemoryClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Mem0 client
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

# Facts to inject
facts = [
    {
        "role": "user", 
        "content": "Remember this important fact about me: My undergraduate degree was obtained at Institut Superieur de Communication d'Organisation et de Management (ISCOM) in Nigeria."
    },
    {
        "role": "user",
        "content": "Remember this detail: I did nail designs for my sister-in-law. The design involved a clean acrylic base."
    }
]

print("Injecting final specific facts...")
try:
    client.add(facts, user_id=user_id)
    print("Successfully injected facts!")
except Exception as e:
    print(f"Error injecting facts: {e}")
