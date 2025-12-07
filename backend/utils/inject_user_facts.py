import os
from mem0 import MemoryClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Mem0 client
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

# All known facts about the user that need to be in memory
user_facts = [
    # Personal Info
    "The user is 23 years old.",
    "The user is 5 feet 5 inches tall (5'5\").",
    
    # Education
    "The user did their undergraduate degree at Institut Superieur de Communication d'Organisation et de Management (ISCOM) in Nigeria.",
    "The user's field of study is Biochemistry.",
    "The user wants to do their master's degree in Food Science.",
    "The user wants to apply for a scholarship to Pusan National University in South Korea.",
    
    # Projects & Apps
    "The user's nail app is named NailMuse.",
    "I (Jaxon) helped name the nail app NailMuse.",
    
    # Nail Work
    "The user did nail designs for their sister-in-law featuring a clean acrylic base.",
]

print("Injecting comprehensive user facts...")

for i, fact in enumerate(user_facts):
    print(f"[{i+1}/{len(user_facts)}] Injecting: {fact[:60]}...")
    try:
        messages = [
            {"role": "user", "content": f"Remember this important fact about me: {fact}"},
            {"role": "assistant", "content": f"Got it! I'll remember that. {fact}"}
        ]
        client.add(messages, user_id=user_id, metadata={"source": "comprehensive_fact_injection", "type": "user_fact"})
    except Exception as e:
        print(f"Error: {e}")

print("\nAll comprehensive user facts injected!")
