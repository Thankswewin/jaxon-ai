"""Test mem0 search to debug why school fact isn't being retrieved."""
import os
from mem0 import MemoryClient
from dotenv import load_dotenv

load_dotenv()

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

# Test queries
queries = [
    "What school did I do my undergraduate program?",
    "ISCOM",
    "undergraduate degree",
    "university benin",
    "bachelor degree biochemistry",
]

for query in queries:
    print(f"\n{'='*50}")
    print(f"QUERY: {query}")
    print(f"{'='*50}")
    
    try:
        results = client.search(query, version="v2", filters={"user_id": user_id})
        if isinstance(results, dict) and 'results' in results:
            memories = results['results']
        else:
            memories = results
        
        print(f"Found {len(memories)} memories:")
        for i, mem in enumerate(memories[:5]):  # Top 5
            memory_text = mem.get('memory', mem.get('text', 'N/A'))
            print(f"  {i+1}. {memory_text[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
