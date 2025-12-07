import json

def final_dump():
    print("Dumping to dump.txt...")
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open('d:/PROJECTS/memo memry/dump.txt', 'w', encoding='utf-8') as out:
        # 1. School
        out.write("=== SCHOOL CANDIDATES ===\n")
        for conv in data:
            for node in conv.get('mapping', {}).values():
                msg = node.get('message')
                if msg and msg['author']['role'] == 'user':
                    parts = msg['content'].get('parts', [])
                    text = "".join([p for p in parts if isinstance(p, str)])
                    text_lower = text.lower()
                    
                    if "nigeria" in text_lower or ("university" in text_lower and "undergraduate" in text_lower):
                        out.write(f"\n[CONV: {conv.get('title')}]\n")
                        out.write(text + "\n")
                        out.write("-" * 50 + "\n")

        # 2. Nails
        out.write("\n\n=== NAIL DESIGNS ===\n")
        for conv in data:
            for node in conv.get('mapping', {}).values():
                msg = node.get('message')
                if msg and msg['author']['role'] == 'user':
                    parts = msg['content'].get('parts', [])
                    text = "".join([p for p in parts if isinstance(p, str)])
                    text_lower = text.lower()
                    
                    if "sister" in text_lower and "nail" in text_lower:
                        out.write(f"\n[CONV: {conv.get('title')}]\n")
                        out.write(text + "\n")
                        out.write("-" * 50 + "\n")

if __name__ == "__main__":
    final_dump()
