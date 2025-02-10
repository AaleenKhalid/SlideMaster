import google.generativeai as genai
import os
from dotenv import load_dotenv
from dotenv import dotenv_values
import logging

logger = logging.getLogger(__name__)

class LLMEngine:
    def __init__(self):
        try:
            load_dotenv()
            config = dotenv_values(".env")  # Load environment variables manually
            print(config)  # Debug to check if the API key is being read correctly

            api_key = os.getenv('GEMINI_API_KEY') # Getting API key
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("LLM Engine initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM Engine: {str(e)}")
            raise RuntimeError(f"Failed to initialize LLM Engine: {str(e)}")

    def generate_markdown(self, prepared_prompt):
        """
        Generate markdown content using Gemini LLM.

        :param prepared_prompt: Processed prompt from PromptEngine
        :return: Generated markdown content
        """
        try:
            if not isinstance(prepared_prompt, str):
                prepared_prompt = str(prepared_prompt)

            logger.info("Generating content with Gemini")
            response = self.model.generate_content(prepared_prompt)

            if not response:
                raise ValueError("No response received from Gemini")

            if not hasattr(response, 'text'):
                raise ValueError("Invalid response format from Gemini")

            return response.text

        except Exception as e:
            logger.error(f"Error in generate_markdown: {str(e)}")
            raise RuntimeError(f"Failed to generate content: {str(e)}")