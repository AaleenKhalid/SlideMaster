import unittest
import sys
import os
import logging

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.prompt_engine import PromptEngine
from backend.services.llm_engine import LLMEngine
from backend.services.verification_service import VerificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestServices(unittest.TestCase):
    def test_prompt_engine(self):
        logger.info("Testing PromptEngine initialization...")
        try:
            prompt_engine = PromptEngine()
            self.assertIsNotNone(prompt_engine)
            logger.info("PromptEngine initialized successfully")
        except Exception as e:
            logger.error(f"PromptEngine initialization failed: {str(e)}")
            raise

    def test_llm_engine(self):
        logger.info("Testing LLMEngine initialization...")
        try:
            llm_engine = LLMEngine()
            self.assertIsNotNone(llm_engine)
            logger.info("LLMEngine initialized successfully")
        except Exception as e:
            logger.error(f"LLMEngine initialization failed: {str(e)}")
            raise

    def test_verification_service(self):
        logger.info("Testing VerificationService initialization...")
        try:
            verification_service = VerificationService()
            self.assertIsNotNone(verification_service)
            logger.info("VerificationService initialized successfully")
        except Exception as e:
            logger.error(f"VerificationService initialization failed: {str(e)}")
            raise

if __name__ == '__main__':
    unittest.main()