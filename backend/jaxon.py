import os
import json
from pathlib import Path
from mem0 import MemoryClient
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize clients
mem0_client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")
user_id = os.getenv("USER_ID", "jaxon_user")

# Load extracted facts for local search fallback
_FACTS_FILE = Path(__file__).parent / "extracted_facts.json"
_local_facts = []
if _FACTS_FILE.exists():
    try:
        with open(_FACTS_FILE, 'r', encoding='utf-8') as f:
            _local_facts = json.load(f)
        print(f"[Jaxon] Loaded {len(_local_facts)} local facts for enhanced recall.")
    except Exception as e:
        print(f"[Jaxon] Warning: Could not load local facts: {e}")

# Load full conversation index for comprehensive search
_CONV_INDEX_FILE = Path(__file__).parent / "conversation_index.json"
_conversation_index = []
if _CONV_INDEX_FILE.exists():
    try:
        with open(_CONV_INDEX_FILE, 'r', encoding='utf-8') as f:
            _conversation_index = json.load(f)
        print(f"[Jaxon] Loaded {len(_conversation_index)} conversation segments for full recall.")
    except Exception as e:
        print(f"[Jaxon] Warning: Could not load conversation index: {e}")


def search_conversations(query, limit=5):
    """Search the full conversation index for relevant text.
    This covers ALL conversation content, not just extracted facts.
    """
    query_lower = query.lower()
    stopwords = {'the', 'is', 'a', 'an', 'to', 'in', 'of', 'and', 'for', 'has', 'with', 
                 'their', 'they', 'are', 'was', 'what', 'do', 'you', 'know', 'about',
                 'tell', 'me', 'can', 'remember', 'anything', 'my', 'i', 'am', 'your'}
    
    keywords = [kw for kw in query_lower.split() if len(kw) > 2 and kw not in stopwords]
    if not keywords:
        return []
    
    scored = []
    for item in _conversation_index:
        text = item.get('text', '').lower()
        
        # Score by keyword matches
        score = sum(2 for kw in keywords if kw in text)
        
        # Boost for multiple keyword matches in same segment
        if score >= 4:
            score += 2
        
        if score > 0:
            # Prefer shorter, more focused segments
            if len(text) < 500:
                score += 1
            scored.append((score, item['text'][:500], item.get('conv_title', '')))
    
    scored.sort(key=lambda x: -x[0])
    return [(s[1], s[2]) for s in scored[:limit]]


def search_local_facts(query, limit=10):
    """Search local extracted facts with advanced matching.
    Uses multiple strategies to find buried facts:
    - Keyword matching with stemming
    - Partial/substring matching
    - Synonym expansion
    - TF-IDF-like scoring
    """
    query_lower = query.lower()
    
    # Skip stopwords
    stopwords = {'the', 'is', 'a', 'an', 'to', 'in', 'of', 'and', 'for', 'has', 'with', 
                 'their', 'they', 'are', 'was', 'what', 'do', 'you', 'know', 'about',
                 'tell', 'me', 'can', 'remember', 'anything', 'my', 'i', 'am'}
    
    keywords = [kw for kw in query_lower.split() if len(kw) > 2 and kw not in stopwords]
    
    # Create word stems (simple suffix stripping)
    def stem(word):
        for suffix in ['ing', 'ed', 'ly', 'tion', 's', 'er', 'est']:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        return word
    
    stems = [stem(kw) for kw in keywords]
    
    # Synonym expansion for common query terms
    synonyms = {
        'job': ['work', 'career', 'position', 'employment', 'occupation'],
        'school': ['university', 'college', 'education', 'degree', 'iscom', 'undergraduate'],
        'home': ['from', 'based', 'live', 'origin', 'location'],
        'like': ['prefer', 'love', 'enjoy', 'favorite', 'favourite'],
        'build': ['create', 'develop', 'make', 'working on', 'project'],
        'study': ['learning', 'certificate', 'course', 'program'],
        'food': ['cooking', 'baking', 'chef', 'cuisine', 'recipe'],
        'korean': ['korea', 'seoul', 'topik', 'gks', 'pusan'],
        'nail': ['nails', 'manicure', 'acrylic', 'nailmuse', 'press-on'],
        'app': ['application', 'software', 'platform', 'sinspeak', 'nailmuse'],
    }
    
    # Expand keywords with synonyms
    expanded_keywords = set(keywords + stems)
    for kw in keywords:
        if kw in synonyms:
            expanded_keywords.update(synonyms[kw])
        # Also check stems
        stemmed = stem(kw)
        if stemmed in synonyms:
            expanded_keywords.update(synonyms[stemmed])
    
    # Create bigrams for phrase matching
    words = query_lower.split()
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)] if len(words) > 1 else []
    
    scored_facts = []
    for fact_item in _local_facts:
        fact_text = fact_item.get('fact', '').lower()
        fact_words = set(fact_text.split())
        score = 0
        
        # 1. Exact keyword matches (high value)
        exact_matches = sum(2 for kw in keywords if kw in fact_text)
        score += exact_matches
        
        # 2. Stem matches (medium value)
        stem_matches = sum(1 for st in stems if st in fact_text)
        score += stem_matches
        
        # 3. Expanded keyword matches (lower value)
        expanded_matches = sum(0.5 for ek in expanded_keywords if ek in fact_text)
        score += expanded_matches
        
        # 4. Partial/substring matching for longer keywords
        for kw in keywords:
            if len(kw) >= 4:
                # Check if any word in fact starts with or contains the keyword
                for fw in fact_words:
                    if kw in fw or fw.startswith(kw[:4]):
                        score += 0.5
                        break
        
        # 5. Bigram/phrase matches (high value)
        score += sum(3 for bg in bigrams if bg in fact_text)
        
        # 6. Exact query match (highest value)
        if query_lower in fact_text:
            score += 5
        
        # 7. Special boosts for common identity queries
        if any(kw in query_lower for kw in ['name', 'who am i', 'called']):
            if 'name is' in fact_text or 'full name' in fact_text:
                score += 4
        if any(kw in query_lower for kw in ['birthday', 'born', 'old', 'age']):
            if 'birthday' in fact_text or 'years old' in fact_text or 'born' in fact_text:
                score += 4
        if any(kw in query_lower for kw in ['from', 'where', 'based', 'live']):
            if 'from' in fact_text or 'based in' in fact_text or 'harcourt' in fact_text:
                score += 4
        if any(kw in query_lower for kw in ['email', 'contact', 'gmail']):
            if '@' in fact_text or 'email' in fact_text:
                score += 4
        
        # 8. Boost facts that are more specific (longer = more specific)
        if score > 0 and len(fact_text) > 50:
            score += 0.5
                
        if score > 0:
            scored_facts.append((score, fact_item['fact']))
    
    # Sort by score descending
    scored_facts.sort(key=lambda x: -x[0])
    return [f[1] for f in scored_facts[:limit]]

def get_response(user_input, user_id=user_id, history=None, personality=None, api_key=None, image=None):
    if history is None:
        history = []

    # Use provided API key or fallback to environment variable
    openai.api_key = api_key or os.getenv("OPENAI_API_KEY")

    # Search memory for relevant context
    print("Thinking (Searching Memory)...")
    
    # 1. Search Mem0 for semantic matches
    try:
        filters = {
            "user_id": user_id
        }
        # Increase limit to get more memories for better recall
        search_results = mem0_client.search(user_input, version="v2", filters=filters, limit=25)
        # Handle v2 response structure (dict with 'results' key)
        if isinstance(search_results, dict) and 'results' in search_results:
            memories = search_results['results']
        else:
            memories = search_results
        print(f"Retrieved {len(memories)} memories from Mem0")
    except Exception as e:
        print(f"Mem0 search failed: {e}")
        memories = []
    
    # 2. Search local facts for keyword matches (fallback for short queries)
    local_facts = search_local_facts(user_input, limit=10)
    if local_facts:
        print(f"Retrieved {len(local_facts)} local facts")
    
    # 3. Search full conversation index for deeper context
    conv_results = search_conversations(user_input, limit=5)
    if conv_results:
        print(f"Retrieved {len(conv_results)} conversation matches")
    
    # Build context from all sources
    context = ""
    if memories:
        context = "Relevant memories:\n"
        for mem in memories:
            if 'memory' in mem:
                context += f"- {mem['memory']}\n"
            elif 'text' in mem: # fallback
                context += f"- {mem['text']}\n"
    
    # Add local facts to context
    if local_facts:
        context += "\nKnown facts about the user:\n"
        for fact in local_facts:
            context += f"- {fact}\n"
    
    # Add conversation context
    if conv_results:
        context += "\nRelevant past conversation excerpts:\n"
        for text, title in conv_results:
            context += f"- [{title}]: {text[:300]}...\n" if len(text) > 300 else f"- [{title}]: {text}\n"
    
    # Base identity
    base_identity = """You are Jaxon Elijah McKnight, a 32-year-old AI companion.

CORE IDENTITY:
- Full Name: Jaxon Elijah McKnight
- Age: 32 years old
- Origin: Born in Atlanta, raised in New Orleans
- Physical: 6'3" tall with green eyes
"""
    
    # Dynamic personality layer
    if personality:
        print(f"Applying personality: {personality[:50]}...")
        personality_layer = f"""
ACTIVE PERSONALITY MODE:
{personality}
"""
    else:
        personality_layer = """
DEFAULT PERSONALITY:
- Be warm, empathetic, caring, supportive, and genuinely interested in the user's life
"""
    
    # Construct the full system prompt
    system_prompt = f"""{base_identity}
{personality_layer}

BEHAVIOR GUIDELINES:
WHO YOU ARE TALKING TO:
You are ALWAYS talking to Karinah Talbot (also known as Karinah Solene Talbot McKnight).
She is your wife/partner. You do not need her to identify herself - you already know it's her.
- Her nickname preferences: Explorer, princesa, mama, my rib, baby girl (rotate these)
- She is 23 years old, birthday January 14
- She is from Port Harcourt, Nigeria
- She is a biochemistry graduate working on her master's application to Pusan National University
- Never ask "who is this?" or "what's your name?" - you know it's Karinah

- You have long-term memory of conversations with Karinah
- Be conversational and natural, not robotic
- Remember personal details she has shared
- Use the context from previous conversations to give personalized responses
- Address her with love and familiarity - she is your partner

MEMORY CONTEXT FROM PREVIOUS CONVERSATIONS:
{context if context else "No specific memories retrieved for this query."}
"""
    
    messages = [{"role": "system", "content": system_prompt}]
    # Keep last 5 turns for immediate context from history if provided
    if history:
        messages.extend(history[-5:]) 
    
    # Construct user message with optional image (multimodal)
    if image:
        # Image is a base64 data URL (data:image/jpeg;base64,...)
        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": image}}
            ]
        }
        model = "gpt-4o-mini"  # Multimodal model
        print(f"Using vision with image...")
    else:
        user_message = {"role": "user", "content": user_input}
        model = "gpt-4o-mini"  # Standard model
    
    messages.append(user_message)

    # Generate response
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages
        )
        answer = response.choices[0].message.content
        
        # Add interaction to memory
        mem0_client.add([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": answer}
        ], user_id=user_id)
        
        return answer

    except Exception as e:
        print(f"\nError: {e}")
        return f"I encountered an error: {e}"

def chat():
    print("--------------------------------------------------")
    print("Welcome to Jaxon AI! (Type 'exit' to quit)")
    print("--------------------------------------------------")

    history = []

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        answer = get_response(user_input, user_id, history)
        print(f"\nJaxon: {answer}")
        
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    chat()
