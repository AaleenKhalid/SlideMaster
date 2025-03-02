import ollama
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_chat():
    """Test direct chat with model name hardcoded to gemma:7b"""
    try:
        model_name = "gemma:2b"
        logger.info(f"Attempting direct chat with {model_name}...")

        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "user", "content": "Generate a short hello world message"}
            ]
        )

        logger.info("Response received!")
        if 'message' in response and 'content' in response['message']:
            content = response['message']['content']
            logger.info(f"Content sample: {content[:100]}...")
            return True
        else:
            logger.error(f"Unexpected response structure: {response}")
            return False

    except Exception as e:
        logger.error(f"Error in direct chat: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_direct_chat()
    if success:
        print("\n✅ Direct chat with gemma:7b successful!")
    else:
        print("\n❌ Direct chat with gemma:7b failed. See logs above.")