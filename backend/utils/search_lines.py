def search_lines():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        for line in f:
            line_lower = line.lower()
            if "sister" in line_lower and "nail" in line_lower:
                print(f"NAIL MATCH: {line[:500]}")
            if "undergraduate" in line_lower and "nigeria" in line_lower:
                print(f"UNI MATCH: {line[:500]}")
            if "university" in line_lower and "nigeria" in line_lower:
                print(f"UNI MATCH 2: {line[:500]}")

if __name__ == "__main__":
    search_lines()
