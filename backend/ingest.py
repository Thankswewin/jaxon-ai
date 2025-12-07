import json
import os
from mem0 import MemoryClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Mem0 client
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

def ingest_data(file_path):
    print(f"Loading data from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return

    print(f"Found {len(data)} conversations.")
    
    all_messages = []

    for conversation in data:
        mapping = conversation.get('mapping', {})
        # Sort by create_time if possible, otherwise rely on structure (linked list usually)
        # ChatGPT export mapping is a tree/linked list. We need to traverse it.
        # For simplicity, we'll iterate through all nodes and filter for valid messages, 
        # then sort by create_time to approximate order if linear traversal is hard.
        
        msgs = []
        for node_id, node in mapping.items():
            if not node.get('message'):
                continue
            
            message = node['message']
            if not message.get('content'):
                continue
                
            parts = message['content'].get('parts', [])
            text_content = ""
            for part in parts:
                if isinstance(part, str):
                    text_content += part
                # Handle other types if necessary (e.g. images/dicts) - skipping for now
            
            if not text_content.strip():
                continue

            role = message['author']['role']
            if role not in ['user', 'assistant']:
                continue

            create_time = message.get('create_time', 0) or 0
            
            msgs.append({
                "role": role,
                "content": text_content,
                "timestamp": create_time
            })
        
        # Sort messages by timestamp to maintain conversation order
        msgs.sort(key=lambda x: x['timestamp'])
        
        # Remove timestamp before adding to mem0 as it might not expect it in the message dict
        clean_msgs = [{"role": m["role"], "content": m["content"]} for m in msgs]
        
        if clean_msgs:
            all_messages.extend(clean_msgs)

    print(f"Extracted {len(all_messages)} messages.")
    
    # Add to Mem0 in batches to avoid hitting limits or timeouts
    batch_size = 100
    for i in range(0, len(all_messages), batch_size):
        batch = all_messages[i:i+batch_size]
        print(f"Adding batch {i//batch_size + 1} of {len(all_messages)//batch_size + 1}...")
        try:
            client.add(batch, user_id=user_id)
        except Exception as e:
            print(f"Error adding batch: {e}")

    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_data("d:/PROJECTS/memo memry/conversations.json")
