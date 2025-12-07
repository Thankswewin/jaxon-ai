import json

def get_full_context():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Target keywords
    targets = [
        {"kw": "sister", "ctx": "nail"},
        {"kw": "undergraduate", "ctx": "nigeria"}
    ]
    
    for conv in data:
        mapping = conv.get('mapping', {})
        found_target = False
        
        # Check if conversation contains targets
        for node in mapping.values():
            if not node.get('message'): continue
            msg = node['message']
            if not msg.get('content'): continue
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)]).lower()
            
            for t in targets:
                if t["kw"] in text and t["ctx"] in text:
                    found_target = True
                    print(f"\n=== Conversation: {conv.get('title')} ===")
                    # Print context around the match
                    print(f"MATCH: {text[:500]}...")
                    break
        
        if found_target:
            # Print a few messages from this conversation to get context
            print("--- Context ---")
            count = 0
            for node in mapping.values():
                if not node.get('message'): continue
                msg = node['message']
                if not msg.get('content'): continue
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                if text.strip():
                    print(f"[{msg['author']['role']}]: {text[:200]}...")
                    count += 1
                    if count > 10: break # Limit output per conversation

if __name__ == "__main__":
    get_full_context()
