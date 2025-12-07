import sys
import os

# Add current directory to path so we can import jaxon
sys.path.append(os.getcwd())

try:
    from jaxon import get_response
    print("Successfully imported get_response from jaxon")
except ImportError as e:
    print(f"Failed to import get_response: {e}")
    sys.exit(1)

# Test the function
try:
    print("Testing get_response...")
    response = get_response("Hello, who are you?", user_id="test_user")
    print(f"Response received: {response}")
    print("Test passed!")
except Exception as e:
    print(f"Test failed with error: {e}")
    sys.exit(1)
