import json

def dump_convs():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    targets = ["Request for assistance", "Nigeria ADB Membership", "Reaching Past Scholarship Applicants"]
    
    for conv in data:
        title = conv.get('title')
        if title in targets:
            print(f"\n\n==================================================")
            print(f"TITLE: {title}")
            print(f"==================================================")
            
            mapping = conv.get('mapping', {})
            # Sort by create_time
            nodes = []
            for node in mapping.values():
                if node.get('message') and node['message'].get('create_time'):
                    nodes.append(node['message'])
            
            nodes.sort(key=lambda x: x['create_time'])
            
            for msg in nodes:
                role = msg['author']['role']
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                if text.strip():
                    print(f"\n[{role.upper()}]: {text}")

if __name__ == "__main__":
    dump_convs()
