import json

def deep_search():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Deep searching...")
    
    for conv in data:
        mapping = conv.get('mapping', {})
        for node in mapping.values():
            if not node.get('message'): continue
            msg = node['message']
            if not msg.get('content'): continue
            
            # Only check user messages for the facts they provided
            if msg['author']['role'] != 'user': continue
            
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)])
            text_lower = text.lower()
            
            # 1. Nails
            if "sister" in text_lower and "law" in text_lower:
                print(f"\n[NAIL CANDIDATE] in '{conv.get('title')}':")
                print(text[:500])
            
            # 2. Undergraduate
            if "university" in text_lower and ("nigeria" in text_lower or "lagos" in text_lower or "abuja" in text_lower):
                print(f"\n[UNI CANDIDATE] in '{conv.get('title')}':")
                print(text[:500])

if __name__ == "__main__":
    deep_search()
