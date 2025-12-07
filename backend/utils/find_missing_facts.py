import json

def find_exact_facts():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    facts = {
        "first_msg": None,
        "nails": None,
        "undergrad": None
    }
    
    # 1. First Message (Chronological)
    all_msgs = []
    for conv in data:
        for node in conv.get('mapping', {}).values():
            if node.get('message') and node['message'].get('create_time'):
                all_msgs.append(node['message'])
    all_msgs.sort(key=lambda x: x['create_time'])
    
    for msg in all_msgs:
        if msg['author']['role'] == 'user':
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)])
            if text.strip():
                facts['first_msg'] = text
                break
    
    # 2. Nails (Heuristic: Longest message with 'sister' and 'nail')
    longest_nail_msg = ""
    for conv in data:
        for node in conv.get('mapping', {}).values():
            msg = node.get('message')
            if msg and msg['author']['role'] == 'user':
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                if "sister" in text.lower() and "nail" in text.lower():
                    if len(text) > len(longest_nail_msg):
                        longest_nail_msg = text
    facts['nails'] = longest_nail_msg

    # 3. Undergrad (Heuristic: 'undergraduate' + 'nigeria' or 'university' + 'nigeria')
    for conv in data:
        for node in conv.get('mapping', {}).values():
            msg = node.get('message')
            if msg and msg['author']['role'] == 'user':
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                text_lower = text.lower()
                if "undergraduate" in text_lower and "nigeria" in text_lower:
                     facts['undergrad'] = text
                     break # Found a specific mention
                if not facts['undergrad'] and "university" in text_lower and "nigeria" in text_lower:
                     facts['undergrad'] = text # Fallback

    print("--- FOUND FACTS ---")
    print(f"First Msg: {facts['first_msg']}")
    print(f"Nails: {facts['nails'][:200]}...")
    print(f"Undergrad: {facts['undergrad']}")

if __name__ == "__main__":
    find_exact_facts()
