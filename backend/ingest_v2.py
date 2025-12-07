import json
import os
from mem0 import MemoryClient
from dotenv import load_dotenv
from datetime import datetime
import time
import random

# Load environment variables
load_dotenv()

# Initialize Mem0 client
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
user_id = os.getenv("USER_ID", "jaxon_user")

def ingest_data_v2(file_path):
    print(f"Loading data from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    print(f"Found {len(data)} conversations.")
    
    all_messages = []

    for conversation in data:
        conv_title = conversation.get('title', 'Untitled')
        conv_id = conversation.get('id', 'unknown')
        mapping = conversation.get('mapping', {})
        
        msgs = []
        for node_id, node in mapping.items():
            if not node.get('message'): continue
            message = node['message']
            if not message.get('content'): continue
                
            parts = message['content'].get('parts', [])
            text_content = "".join([p for p in parts if isinstance(p, str)])
            
            if not text_content.strip(): continue

            role = message['author']['role']
            if role not in ['user', 'assistant']: continue

            create_time = message.get('create_time', 0) or 0
            
            # Convert timestamp to ISO string for metadata
            try:
                timestamp_iso = datetime.fromtimestamp(create_time).isoformat()
            except:
                timestamp_iso = str(create_time)

            msgs.append({
                "role": role,
                "content": text_content,
                "timestamp": create_time,
                "metadata": {
                    "conversation_id": conv_id,
                    "conversation_title": conv_title,
                    "timestamp": timestamp_iso,
                    "source": "chatgpt_export"
                }
            })
        
        # Sort messages by timestamp
        msgs.sort(key=lambda x: x['timestamp'])
        
        # Prepare for Mem0
        # Mem0 add expects: messages=[{"role": "user", "content": "..."}]
        # But we can also pass metadata? 
        # The add method signature is add(messages, user_id=..., metadata=...)
        # If we pass a list, metadata applies to ALL? Or can we embed metadata in message?
        # Docs say: "messages: List[Dict[str, str]]".
        # If we want per-message metadata, we might need to add them one by one or check if Mem0 supports it in the dict.
        # Let's assume we can pass metadata in the message dict if the client supports it, OR we add one by one.
        # Adding one by one is slower but safer for metadata.
        # OR we group by conversation and add with conversation metadata.
        
        # Let's try adding per conversation to keep context together.
        # But Mem0 might treat a list as a single "memory" context?
        # Actually, Mem0 usually extracts memories FROM the messages.
        # So passing a conversation thread is good.
        
        # We'll chunk the conversation if it's too long, but usually passing the whole conversation (or large chunks) is best.
        
        clean_msgs = []
        for m in msgs:
            clean_msgs.append({
                "role": m["role"],
                "content": m["content"]
                # We can't easily pass per-message metadata in the list format if Mem0 doesn't support it in the dict.
                # But we can pass metadata for the whole batch.
            })
        
        if clean_msgs:
            # We will add each conversation as a batch, with the conversation title as metadata.
            all_messages.append({
                "messages": clean_msgs,
                "metadata": {"title": conv_title, "conversation_id": conv_id, "source": "chatgpt_export"}
            })

    print(f"Prepared {len(all_messages)} conversations for ingestion.")
    
    # Load checkpoint
    checkpoint_file = "ingestion_checkpoint.json"
    completed_convs = set()
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file, 'r') as f:
                completed_convs = set(json.load(f))
            print(f"Resuming from checkpoint. {len(completed_convs)} conversations already ingested.")
        except:
            print("Checkpoint file corrupted or empty. Starting fresh.")

    # Add to Mem0
    for i, item in enumerate(all_messages):
        conv_id = item['metadata']['conversation_id']
        if conv_id in completed_convs:
            print(f"Skipping conversation {i+1}/{len(all_messages)}: {item['metadata']['title']} (Already ingested)")
            continue

        print(f"Ingesting conversation {i+1}/{len(all_messages)}: {item['metadata']['title']}...")
        
        messages = item['messages']
        metadata = item['metadata']
        
        # Chunk messages using a sliding window to preserve context
        window_size = 6
        overlap = 2
        step = window_size - overlap
        
        if step <= 0: step = 1 # Prevent infinite loop if config is bad

        success = True
        for j in range(0, len(messages), step):
            chunk = messages[j:j+window_size]
            if not chunk: break
            
            # Retry logic with exponential backoff
            max_retries = 5
            chunk_success = False
            for attempt in range(max_retries):
                try:
                    # We pass the list of messages. Mem0 will extract memories.
                    client.add(chunk, user_id=user_id, metadata=metadata)
                    time.sleep(0.5) # Rate limiting to be gentle
                    chunk_success = True
                    break # Success, exit retry loop
                except Exception as e:
                    print(f"Error adding chunk starting at {j} of conversation {i+1} (Attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"Failed to add chunk starting at {j} after {max_retries} attempts. Moving to next chunk.")
                        success = False # Mark conversation as having issues
            
            if not chunk_success:
                success = False

        # Update checkpoint if conversation was fully successful (or mostly successful)
        # We'll be lenient and mark it done so we don't get stuck on one bad chunk forever, 
        # unless it crashed completely.
        if success:
            completed_convs.add(conv_id)
            with open(checkpoint_file, 'w') as f:
                json.dump(list(completed_convs), f)

    print("Ingestion v2 complete!")

if __name__ == "__main__":
    ingest_data_v2("conversations.json")
