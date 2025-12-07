import json

def extract_final():
    print("Extracting final facts...")
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. School
    print("\n--- SCHOOL CANDIDATES ---")
    for conv in data:
        for node in conv.get('mapping', {}).values():
            msg = node.get('message')
            if msg and msg['author']['role'] == 'user':
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                text_lower = text.lower()
                
                if "university" in text_lower and ("nigeria" in text_lower or "undergraduate" in text_lower):
                    # Find the sentence with University
                    sentences = text.split('.')
                    for s in sentences:
                        if "university" in s.lower():
                            print(f"Found: {s.strip()}")

    # 2. Nails
    print("\n--- NAIL DESIGN ---")
    for conv in data:
        for node in conv.get('mapping', {}).values():
            msg = node.get('message')
            if msg and msg['author']['role'] == 'user':
                parts = msg['content'].get('parts', [])
                text = "".join([p for p in parts if isinstance(p, str)])
                text_lower = text.lower()
                
                if "acrylic" in text_lower and "base" in text_lower:
                    print(f"Found: {text[:500]}") # Print first 500 chars

if __name__ == "__main__":
    extract_final()
