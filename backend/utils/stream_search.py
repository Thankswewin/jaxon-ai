def stream_search():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        content = f.read() # Read all into memory (500MB is fine for modern RAM, usually)
        # If it's too big, this will fail. But let's try.
    
    print("File loaded. Searching...")
    
    # 1. Nails
    idx = content.find("sister")
    while idx != -1:
        snippet = content[max(0, idx-500):min(len(content), idx+1000)]
        if "nail" in snippet.lower():
            print(f"\n--- NAIL MATCH ---")
            print(snippet)
        idx = content.find("sister", idx+1)
        
    # 2. Undergraduate
    idx = content.find("undergraduate")
    while idx != -1:
        snippet = content[max(0, idx-500):min(len(content), idx+1000)]
        if "nigeria" in snippet.lower() or "university" in snippet.lower():
            print(f"\n--- UNI MATCH ---")
            print(snippet)
        idx = content.find("undergraduate", idx+1)

if __name__ == "__main__":
    stream_search()
