"""
Build a searchable index from conversations.json
This creates conversation_index.json with all text snippets for fast searching.
"""
import json
import re
import sys

print("Building conversation index from conversations.json (34MB)...")
print("This will create a searchable index of ALL conversation text.")
print()

# Load conversations
print("Loading conversations.json...")
sys.stdout.flush()

with open('conversations.json', 'r', encoding='utf-8') as f:
    conversations = json.load(f)

print(f"Loaded {len(conversations)} conversations")

# Extract all text content
index = []
total_chars = 0

for conv_idx, conv in enumerate(conversations):
    conv_title = conv.get('title', 'Untitled')
    conv_id = conv.get('id', 'unknown')
    mapping = conv.get('mapping', {})
    
    for node_id, node in mapping.items():
        if not node.get('message'):
            continue
        
        msg = node['message']
        role = msg.get('author', {}).get('role', '')
        
        if role not in ['user', 'assistant']:
            continue
        
        content = msg.get('content', {})
        parts = content.get('parts', [])
        
        for part in parts:
            if isinstance(part, str) and len(part) > 20:
                # Clean the text
                clean_text = part.strip()
                if clean_text:
                    index.append({
                        'text': clean_text,
                        'role': role,
                        'conv_title': conv_title,
                        'conv_id': conv_id
                    })
                    total_chars += len(clean_text)
    
    if (conv_idx + 1) % 100 == 0:
        print(f"  Processed {conv_idx + 1}/{len(conversations)} conversations...")
        sys.stdout.flush()

print()
print(f"Indexed {len(index)} text segments")
print(f"Total characters: {total_chars:,}")

# Save index
output_file = 'conversation_index.json'
print(f"Saving to {output_file}...")

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False)

print(f"Done! Created {output_file}")
print(f"File size: {len(json.dumps(index)) / 1024 / 1024:.1f} MB")
