import json

def manual_read():
    print("Reading conversations.json...")
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} conversations.")
    
    # 1. First Message
    # Find the very first message in the entire history (by timestamp)
    all_msgs = []
    for conv in data:
        for node in conv.get('mapping', {}).values():
            if node.get('message') and node['message'].get('create_time'):
                all_msgs.append(node['message'])
    all_msgs.sort(key=lambda x: x['create_time'])
    
    first_user_msg = None
    for msg in all_msgs:
        if msg['author']['role'] == 'user':
            parts = msg['content'].get('parts', [])
            text = "".join([p for p in parts if isinstance(p, str)])
            if text.strip():
                first_user_msg = text
                break
    
    print("\n=== 1. FIRST MESSAGE ===")
    print(f"Text: {first_user_msg}")

    # 2. Nail Designs
    print("\n=== 2. NAIL DESIGNS ===")
    for conv in data:
        for node in conv.get('mapping', {}).values():
            msg = node.get('message')
            if msg and msg['author']['role'] == 'user':
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                if "sister" in text.lower() and "nail" in text.lower() and "design" in text.lower():
                    print(f"--- Found in '{conv.get('title')}' ---")
                    print(text[:1000]) # Print more context
                    print("-" * 20)

    # 3. Undergraduate School
    print("\n=== 3. UNDERGRADUATE SCHOOL ===")
    for conv in data:
        for node in conv.get('mapping', {}).values():
            msg = node.get('message')
            if msg and msg['author']['role'] == 'user':
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                text_lower = text.lower()
                # Look for specific keywords related to the user's question
                if "undergraduate" in text_lower and ("nigeria" in text_lower or "school" in text_lower or "university" in text_lower):
                     print(f"--- Found in '{conv.get('title')}' ---")
                     print(text[:1000])
                     print("-" * 20)

if __name__ == "__main__":
    manual_read()
