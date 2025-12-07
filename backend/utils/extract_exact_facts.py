import json

def extract_facts():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Searching for facts...")
    
    for conv in data:
        mapping = conv.get('mapping', {})
        for node in mapping.values():
            if not node.get('message'): continue
            msg = node['message']
            if not msg.get('content'): continue
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)])
            text_lower = text.lower()
            
            # Nail Design
            if "sister" in text_lower and "nail" in text_lower and "design" in text_lower:
                print(f"\n--- Nail Design (found in '{conv.get('title')}') ---")
                print(text)
                print("-" * 50)

            # Undergraduate
            if "undergraduate" in text_lower and "nigeria" in text_lower:
                print(f"\n--- Undergraduate (found in '{conv.get('title')}') ---")
                print(text)
                print("-" * 50)

if __name__ == "__main__":
    extract_facts()
