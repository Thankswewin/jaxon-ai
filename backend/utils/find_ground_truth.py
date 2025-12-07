import json

def find_ground_truth():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    keywords = ["computer science", "study", "major", "degree", "university", "college", "school"]
    
    print(f"Scanning {len(data)} conversations...")
    
    found_count = 0
    for conv in data:
        mapping = conv.get('mapping', {})
        for node in mapping.values():
            if not node.get('message'): continue
            msg = node['message']
            if not msg.get('content'): continue
            if msg['author']['role'] != 'user': continue # Only care about what user said about themselves
            
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)]).lower()
            
            if any(kw in text for kw in keywords):
                print(f"--- Match in '{conv.get('title')}' ---")
                print(f"User: {text[:300]}...")
                found_count += 1
                if found_count > 20: return # Limit output

if __name__ == "__main__":
    find_ground_truth()
