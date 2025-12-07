import json

def find_context():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} conversations.")
    
    for conv in data:
        mapping = conv.get('mapping', {})
        for node_id, node in mapping.items():
            if not node.get('message'): continue
            msg = node['message']
            if not msg.get('content'): continue
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)])
            
            if "computer science" in text.lower():
                print(f"--- Found in conversation {conv.get('title', 'Unknown')} ---")
                print(f"Role: {msg['author']['role']}")
                print(f"Content: {text[:500]}...") # Print first 500 chars
                print("--------------------------------------------------")

if __name__ == "__main__":
    find_context()
