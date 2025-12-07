import json
from datetime import datetime

def find_facts():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} conversations.")
    
    # 1. First thing said
    # Collect all user messages with timestamps
    all_user_msgs = []
    for conv in data:
        mapping = conv.get('mapping', {})
        for node in mapping.values():
            if not node.get('message'): continue
            msg = node['message']
            if msg['author']['role'] == 'user' and msg.get('content'):
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                if text.strip():
                    create_time = msg.get('create_time', 0) or 0
                    all_user_msgs.append((create_time, text, conv.get('title')))
    
    all_user_msgs.sort(key=lambda x: x[0])
    if all_user_msgs:
        print("\n--- Fact 1: First thing said ---")
        print(f"Time: {datetime.fromtimestamp(all_user_msgs[0][0])}")
        print(f"Content: {all_user_msgs[0][1]}")
    
    # 2. Nail designs for sister in law
    print("\n--- Fact 2: Nail designs for sister in law ---")
    for conv in data:
        mapping = conv.get('mapping', {})
        for node in mapping.values():
            if not node.get('message'): continue
            msg = node['message']
            if not msg.get('content'): continue
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)]).lower()
            
            if "sister" in text and "nail" in text:
                print(f"Found in '{conv.get('title')}': {text[:500]}...")

    # 3. Undergraduate school and country
    print("\n--- Fact 3: Undergraduate school and country ---")
    keywords = ["undergraduate", "university", "school", "degree", "study", "graduated", "bachelor"]
    for conv in data:
        mapping = conv.get('mapping', {})
        for node in mapping.values():
            if not node.get('message'): continue
            msg = node['message']
            if msg['author']['role'] != 'user': continue
            
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)]).lower()
            
            if any(kw in text for kw in keywords) and ("nigeria" in text or "university" in text):
                 print(f"Found in '{conv.get('title')}': {text[:500]}...")

if __name__ == "__main__":
    find_facts()
