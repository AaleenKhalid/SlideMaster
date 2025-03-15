import unittest
import requests
from dotenv import load_dotenv

class TestSlideGenerationEndpoint(unittest.TestCase):
    def setUp(self):
        # Load environment variables
        load_dotenv()

        # Base URL for testing
        self.base_url = 'http://localhost:5000/api/slides/generate'

    def test_successful_generation(self):
        """
        Test successful slide deck generation
        """
        prompt = "Create a slide deck about AI innovation"

        response = requests.post(self.base_url, json={'prompt': prompt})
        # print(response.json())

        # Check response status code
        self.assertEqual(response.status_code, 200)

        # Check response structure
        response_data = response.json()
        self.assertIn('status', response_data)
        self.assertIn('markdown', response_data)

        # Check markdown content
        self.assertEqual(response_data['status'], 'success')
        self.assertTrue(len(response_data['markdown']) > 100)

    def test_empty_prompt(self):
        """
        Test endpoint response to empty prompt
        """
        response = requests.post(self.base_url, json={'prompt': ''})

        # Check error handling
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn('status', response_data)
        self.assertEqual(response_data['status'], 'error')

    def test_short_prompt(self):
        """
        Test endpoint response to very short prompt
        """
        short_prompt = "AI"

        response = requests.post(self.base_url, json={'prompt': short_prompt})

        # Check error handling
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertIn('status', response_data)
        self.assertEqual(response_data['status'], 'error')

if __name__ == '__main__':
    unittest.main()