import unittest
import os
import sys
from unittest.mock import patch, MagicMock
import logging
import re

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.verification_service import VerificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestVerificationService(unittest.TestCase):
    def setUp(self):
        #logger.info('Setting up verification service')
        self.verification_service = VerificationService()

        # Sample markdown for testing
        self.valid_markdown = """
# Sample Presentation on Climate Change

## Introduction
- Climate change is a global challenge that affects everyone.
- Global temperatures have risen by approximately 1.1°C since the pre-industrial era.
- According to NASA, 97% of climate scientists agree that climate change is real and human-caused.

## Key Facts
- The Arctic is warming at twice the rate of the global average.
- Sea levels have risen about 8-9 inches since 1880.
- The last decade (2011-2020) was the warmest on record.

## Impact
* Rising sea levels threaten coastal communities worldwide.
* Extreme weather events are becoming more frequent and severe.
* Biodiversity loss is accelerating due to changing habitats.

## Solutions
1. Renewable energy adoption
2. Carbon capture technologies
3. Sustainable agriculture practices
4. Policy interventions
"""

        # Invalid markdown (too short)
        self.invalid_markdown = "# Title only"

        # Markdown with misleading patterns
        self.misleading_markdown = """
# Misleading Facts

- Everyone knows that climate change is a hoax.
- Studies show that vaccines are 100% dangerous.
- Scientists all agree that the earth is flat.
"""



    def test_verify_structure(self):
        logger.info("Testing verify Structure")
        # Should pass for valid markdown
        try:
            self.verification_service.verify_structure(self.valid_markdown)
            structure_valid = True
            logger.info("Testing verify structure - valid markdown structure")
        except ValueError:
            structure_valid = False

        self.assertTrue(structure_valid)

        # Should raise ValueError for invalid markdown
        with self.assertRaises(ValueError):
            logger.info("Testing verify structure for invalid markdown - invalid markdown structure")
            self.verification_service.verify_structure(self.invalid_markdown)



    def test_extract_key_facts(self):
        logger.info("----- Testing extract key facts-------")
        logger.info("Markdown content for testing:")

        # Test with a very simple, obvious factual statement first
        simple_markdown = "- Global temperatures have risen by approximately 1.1°C since 1900."
        logger.info(simple_markdown)
        bullet_matches = re.findall(r'^\s*[-*]\s+(.*?)$', simple_markdown, re.MULTILINE)
        print(f"FOR TEST EXTRACT KEY FACTS ----> Bullet matches: {bullet_matches}")

        facts = self.verification_service.extract_key_facts(simple_markdown)
        logger.info(f"Extracted facts: {facts}")

        # This should definitely pass
        self.assertTrue(len(facts) > 0)

        logger.info(self.valid_markdown)

        facts = self.verification_service.extract_key_facts(self.valid_markdown)

        # Debug what's returned
        logger.info(f"Extracted {len(facts)} facts")
        if facts:
            logger.info(f"First few facts: {facts[:3]}")


        # Check that we extracted facts
        self.assertTrue(len(facts) > 0)

        # Check that key facts were extracted
        logger.info("asserting fact 1 found")
        self.assertTrue(any('1.1°C' in fact for fact in facts))
        logger.info("asserting fact 2 found")
        self.assertTrue(any('97%' in fact for fact in facts))



    @patch('requests.get')
    def test_search_for_facts(self, mock_get):
        logger.info("----- Testing search for facts -----")
        logger.info("Mocking SerpAPI responses")
        # Mock the SerpAPI response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "organic_results": [
                {
                    "title": "NASA: Climate Change and Global Warming",
                    "link": "https://climate.nasa.gov/",
                    "snippet": "97% of climate scientists agree that climate change is real and human-caused.",
                    "source": "NASA"
                }
            ]
        }
        mock_get.return_value = mock_response

        # Set the API key for testing
        with patch.dict(os.environ, {'SERPAPI_KEY': 'test_key'}):
            factual_statements = ["97% of climate scientists agree that climate change is real and human-caused."]
            results = self.verification_service.search_for_facts(factual_statements)

            # Check that we got results for our statement
            self.assertIn(factual_statements[0], results)

            # Check that the mock was called with the expected URL
            mock_get.assert_called_once()
            call_args = mock_get.call_args[0][0]
            self.assertIn('test_key', call_args)
            self.assertIn('fact+check', call_args)



    def test_compare_statements_with_search_results(self):
        logger.info("-----Testing compare statements with search results------")
        # Set up test data
        factual_statements = ["Global temperatures have risen by approximately 1.1°C since the pre-industrial era."]
        search_results = {
            factual_statements[0]: {
                "organic_results": [
                    {
                        "title": "Climate Change: Global Temperature | NOAA Climate.gov",
                        "link": "https://www.climate.gov/news-features/understanding-climate/climate-change-global-temperature",
                        "snippet": "Earth's temperature has risen by an average of 1.1° Celsius (1.9° Fahrenheit) since the pre-industrial era.",
                        "source": "NOAA"
                    }
                ],
                "knowledge_graph": None,
                "answer_box": None,
                "related_questions": []
            }
        }

        # Test comparison
        results = self.verification_service.check_similarity(factual_statements, search_results)

        # Check that our statement was verified
        self.assertIn(factual_statements[0], results)
        self.assertTrue(results[factual_statements[0]]["verified"])
        self.assertGreater(results[factual_statements[0]]["confidence"], 0.3)



    @patch('backend.services.verification_service.VerificationService.extract_key_facts')
    @patch('backend.services.verification_service.VerificationService.search_for_facts')
    @patch('backend.services.verification_service.VerificationService.check_similarity')
    def test_fact_check_integration(self, mock_compare, mock_search, mock_extract):
        logger.info(" ---- Testing fact check integration ----- ")
        # Set up mocks
        mock_extract.return_value = ["Fact 1", "Fact 2"]
        mock_search.return_value = {"Fact 1": {}, "Fact 2": {}}
        mock_compare.return_value = {
            "Fact 1": {"verified": True, "confidence": 0.8, "high_confidence": True},
            "Fact 2": {"verified": True, "confidence": 0.7, "high_confidence": False}
        }

        # Test the main fact_check method
        result = self.verification_service.fact_check(self.valid_markdown)

        # Check that the result is properly structured
        self.assertIn("verified", result)
        self.assertIn("message", result)
        self.assertIn("verification_summary", result)
        self.assertIn("verification_details", result)

        # Check that the mocks were called
        mock_extract.assert_called_once()
        mock_search.assert_called_once()
        mock_compare.assert_called_once()


if __name__ == '__main__':
    unittest.main()