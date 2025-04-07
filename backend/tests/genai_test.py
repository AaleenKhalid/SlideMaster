import unittest
import os
import sys
from dotenv import load_dotenv
import logging


# Configure logging for tests
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to import LLMEngine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # parent of tests directory
env_path = os.path.join(backend_dir, '.env.txt')  # .env is in the backend directory

# Load environment variables from .env file with explicit path
load_dotenv(dotenv_path=env_path)


from backend.services.llm_engine import LLMEngine

class GeminiAPITest(unittest.TestCase):
    """Test class for verifying Google Gemini API integration."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        # Load environment variables from .env file
        #load_dotenv()

        # Check if the API key is available
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY environment variable not set")
            raise unittest.SkipTest("GEMINI_API_KEY environment variable not set")

        logger.info("SetUpClass completed. API key found.")


    def setUp(self):
        """Set up before each test."""
        try:
            # Initialize the LLMEngine with Gemini model
            self.llm_engine = LLMEngine(model_type="gemini")
            logger.info("LLMEngine initialized with Gemini model")
        except Exception as e:
            self.fail(f"Failed to initialize LLMEngine: {str(e)}")


    def test_gemini_connectivity(self):
        """Test basic connectivity to the Gemini API."""
        try:
            # Generate a simple test prompt
            prompt = "Create a 1-slide presentation about unit testing."

            # Log the test beginning
            logger.info(f"Testing Gemini API with prompt: {prompt}")

            # Call the generate_markdown method
            response = self.llm_engine.generate_markdown(prompt)

            # Log the response
            logger.info(f"Received response of length: {len(response)}")

            # Basic validation
            self.assertIsNotNone(response)
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)

            # Optional: Check for expected markdown elements
            markdown_elements = ["#", "-", "*"]
            has_markdown = any(element in response for element in markdown_elements)
            self.assertTrue(has_markdown, "Response does not appear to contain markdown formatting")

            # Print the first 200 characters of the response for manual inspection
            logger.info(f"Response preview: {response[:200]}...")

        except Exception as e:
            self.fail(f"API call failed: {str(e)}")


    def test_gemini_content_quality(self):
        """Test that the Gemini model generates relevant content."""
        try:
            # Generate a prompt that requires specific slide content
            prompt = "Create a 3-slide presentation about Python data structures. Include slides about lists, dictionaries, and sets."

            # Call the generate_markdown method
            response = self.llm_engine.generate_markdown(prompt)

            # Check that the response contains expected keywords
            expected_keywords = ["list", "dictionary", "dictionaries", "set", "sets", "data structure"]

            # Convert to lowercase for case-insensitive comparison
            response_lower = response.lower()

            # Check for at least half of the expected keywords
            keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in response_lower)
            self.assertGreaterEqual(
                keyword_matches,
                len(expected_keywords) // 2,
                f"Response doesn't contain enough expected keywords. Found {keyword_matches} out of {len(expected_keywords)}"
            )

        except Exception as e:
            self.fail(f"Content generation test failed: {str(e)}")


    def test_error_handling(self):
        """Test that errors are properly caught and handled."""
        with self.assertRaises(Exception):
            # Intentionally trigger an error by passing None
            self.llm_engine.generate_markdown(None)


if __name__ == "__main__":
    unittest.main()