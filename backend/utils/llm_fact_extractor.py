"""
LLM Fact Extractor
Scans all conversations and uses GPT to extract factual information about the user.
Saves extracted facts to a JSON file and injects them into mem0.
"""

import json
import os
import time
from mem0 import MemoryClient
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize clients
client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")
user_id = os.getenv("USER_ID", "jaxon_user")

# Extraction prompt
EXTRACTION_PROMPT = """Analyze the following conversation between a user and an AI assistant.
Extract ALL factual information about the USER (not the AI). Focus on:
- Personal details (name, age, height, location, nationality)
- Education (schools, degrees, fields of study, aspirations)
- Work/Career (job, projects, apps they're building)
- Interests and hobbies
- Relationships (mentions of family, friends)
- Specific events or experiences they mention
- Preferences and opinions

Return the facts as a JSON array of strings. Each fact should be a complete, standalone statement.
If no facts about the user are found, return an empty array [].

Example output:
["The user is 25 years old", "The user studies at Harvard", "The user is building a nail design app"]

CONVERSATION:
{conversation}

EXTRACTED FACTS (JSON array only):"""


def extract_messages_from_conversation(conv):
    """Extract messages from a conversation in the ChatGPT export format."""
    mapping = conv.get('mapping', {})
    messages = []
    
    for node_id, node in mapping.items():
        if not node.get('message'):
            continue
        msg = node['message']
        if not msg.get('content'):
            continue
        
        parts = msg['content'].get('parts', [])
        text = "".join([p for p in parts if isinstance(p, str)])
        
        if not text.strip():
            continue
        
        role = msg['author']['role']
        if role in ['user', 'assistant']:
            messages.append(f"[{role.upper()}]: {text}")
    
    return "\n".join(messages)


def extract_facts_from_conversation(conv_text, conv_title):
    """Use GPT to extract facts from a conversation."""
    # Truncate if too long (keep last 8000 chars to stay within context)
    if len(conv_text) > 8000:
        conv_text = conv_text[-8000:]
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Using mini for cost efficiency
            messages=[
                {"role": "system", "content": "You are a fact extraction assistant. Extract facts about the USER only, not the AI. Return valid JSON array of strings only."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(conversation=conv_text)}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        result = response.choices[0].message.content.strip()
        
        # Try to parse as JSON
        # Handle markdown code blocks if present
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        
        facts = json.loads(result)
        return facts if isinstance(facts, list) else []
    
    except json.JSONDecodeError:
        print(f"  JSON parse error for '{conv_title}'")
        return []
    except Exception as e:
        print(f"  Error extracting from '{conv_title}': {e}")
        return []


def main():
    # Load conversations
    conv_file = "conversations.json"
    print(f"Loading conversations from {conv_file}...")
    
    with open(conv_file, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    print(f"Found {len(conversations)} conversations.")
    
    # Load checkpoint
    checkpoint_file = "fact_extraction_checkpoint.json"
    extracted_file = "extracted_facts.json"
    
    completed = set()
    all_facts = []
    
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            completed = set(json.load(f))
        print(f"Resuming from checkpoint. {len(completed)} already processed.")
    
    if os.path.exists(extracted_file):
        with open(extracted_file, 'r') as f:
            all_facts = json.load(f)
    
    # Process conversations
    for i, conv in enumerate(conversations):
        conv_id = conv.get('id', str(i))
        conv_title = conv.get('title', 'Untitled')
        
        if conv_id in completed:
            continue
        
        print(f"[{i+1}/{len(conversations)}] Processing: {conv_title[:50]}...")
        
        # Extract messages
        conv_text = extract_messages_from_conversation(conv)
        
        if len(conv_text) < 50:  # Skip very short conversations
            print("  Skipping (too short)")
            completed.add(conv_id)
            continue
        
        # Extract facts
        facts = extract_facts_from_conversation(conv_text, conv_title)
        
        if facts:
            print(f"  Found {len(facts)} facts")
            for fact in facts:
                all_facts.append({
                    "fact": fact,
                    "source_conversation": conv_title,
                    "source_id": conv_id
                })
        
        # Save checkpoint
        completed.add(conv_id)
        with open(checkpoint_file, 'w') as f:
            json.dump(list(completed), f)
        
        with open(extracted_file, 'w', encoding='utf-8') as f:
            json.dump(all_facts, f, indent=2, ensure_ascii=False)
        
        # Rate limiting
        time.sleep(0.5)
    
    print(f"\nExtraction complete! Total unique facts: {len(all_facts)}")
    print(f"Facts saved to {extracted_file}")
    
    # Ask to inject
    print("\nDo you want to inject these facts into mem0? (y/n)")
    if input().lower() == 'y':
        inject_facts(all_facts)


def inject_facts(facts):
    """Inject extracted facts into mem0."""
    print(f"\nInjecting {len(facts)} facts into mem0...")
    
    # Deduplicate by exact match
    unique_facts = list(set(f['fact'] for f in facts))
    print(f"Unique facts after deduplication: {len(unique_facts)}")
    
    for i, fact in enumerate(unique_facts):
        print(f"[{i+1}/{len(unique_facts)}] {fact[:60]}...")
        try:
            messages = [
                {"role": "user", "content": f"Remember this about me: {fact}"},
                {"role": "assistant", "content": f"I'll remember that. {fact}"}
            ]
            client.add(messages, user_id=user_id, metadata={"source": "llm_extraction"})
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nInjection complete!")


if __name__ == "__main__":
    main()
