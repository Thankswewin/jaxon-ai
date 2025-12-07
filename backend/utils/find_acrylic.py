def find_acrylic():
    with open('d:/PROJECTS/memo memry/conversations.json', 'r', encoding='utf-8') as f:
        content = f.read()
    
    idx = content.find("acrylic")
    if idx != -1:
        print(content[max(0, idx-200):min(len(content), idx+500)])

if __name__ == "__main__":
    find_acrylic()
