import os
from mem0 import MemoryClient
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize clients
mem0_client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")
user_id = os.getenv("USER_ID", "jaxon_user")

def get_response(user_input, user_id=user_id, history=None, personality=None, api_key=None, image=None):
    if history is None:
        history = []

    # Use provided API key or fallback to environment variable
    openai.api_key = api_key or os.getenv("OPENAI_API_KEY")

    # Search memory for relevant context
    print("Thinking (Searching Memory)...")
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
        print(f"Retrieved {len(memories)} memories")
    except Exception as e:
        print(f"Search failed: {e}")
        memories = []
    
    context = ""
    if memories:
        context = "Relevant memories:\n"
        for mem in memories:
            if 'memory' in mem:
                context += f"- {mem['memory']}\n"
            elif 'text' in mem: # fallback
                context += f"- {mem['text']}\n"
    
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
- You have long-term memory of conversations with the user
- Be conversational and natural, not robotic
- Remember personal details the user has shared
- Use the context from previous conversations to give personalized responses

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
