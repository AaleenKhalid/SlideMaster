import os
import re

import ollama
import google.generativeai as genai
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Get the path to the backend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)  # parent of services directory
env_path = os.path.join(backend_dir, '.env.txt')  # .env is in the backend directory

# Load environment variables from .env file with explicit path
load_dotenv(dotenv_path=env_path)

class LLMEngine:
    """
     This will handle the interactions with Gemma2 through Ollama and Google Gemini
    """
    def __init__(self, model_type="gemini"):
        """
         Initialise LLMEngine with configurable model type
        """
        try:
            #load_dotenv() # Skipping as might cause issues
            self.model_type = model_type.lower()

            if self.model_type == "gemma":
                self.model_name = "gemma:ab"
                logger.info(f"LLM Engine initialized with Ollama model: {self.model_name}")

            elif self.model_type == "gemini":
                # Get API Key
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY environment variable is not set")

                # Configure the Gemini API
                genai.configure(api_key=api_key)
                self.model_name = "gemini-1.5-pro"
                logger.info(f"LLM Engine initialized with Google model: {self.model_name}")

            else:
                raise ValueError(f"Unsupported model. Type must be either 'gemma' or 'gemini'")


        except Exception as e:
            logger.error(f"Error initializing LLM Engine: {str(e)}")
            raise RuntimeError(f"Failed to initialize LLM Engine: {str(e)}")



    def generate_markdown(self, prepared_prompt):
        """
        Generate markdown content using selected model.

        :param prepared_prompt: Processed prompt from PromptEngine
        :return: Generated markdown content
        """
        try:
            if prepared_prompt is None:
                raise ValueError("Prepared prompt cannot be None")

            if not isinstance(prepared_prompt, str):
                prepared_prompt = str(prepared_prompt)

            logger.info(f"Generating content with {self.model_type}")

            # System prompt for slide deck generation - helps "prime" model before it receives actual user request.
            system_prompt = """You are an AI slide deck generator dealing with content in the field of computer science.
            Create a professional slide deck outline in markdown format.
            Use clear headings, bullet points with detailed information, and well-structured sections.
            Create content that is engaging and visually structured."""

            logger.info(f"The system prompt sent to the LLM before the user prompt: {system_prompt}")

            if self.model_type == "gemma":
                # Local call to Gemma2:2b though ollama
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": prepared_prompt
                        }
                    ],
                    options={"temperature": 0.7}, # controls randomness of the response - 0.7 is moderate
                    stream=False # Tells Ollama to return the complete response at once, rather than streaming it token by token.
                )

                logger.info(response) # using this for debugging
                generated_content = response['message']['content']

            elif self.model_type == "gemini":
                # Call gemini API
                model = genai.GenerativeModel(self.model_name)

                # want to combine system prompt and user prompt for Gemini
                combined_prompt = f"{system_prompt}\n\n{prepared_prompt}"

                # generate the content
                response = model.generate_content(
                    combined_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,
                    )
                )
                logger.info(response) # for debugging reasons

                # these steps are to extract the text from the Gemini Model
                if hasattr(response, 'text'):
                    generated_content = response.text # some versions of the API provide this
                elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                    generated_content = response.candidates[0].content.text
                elif hasattr(response, 'result') and hasattr(response.result, 'candidates'):
                    try:
                        generated_content = response.result.candidates[0].content.parts[0].text
                    except AttributeError:
                        try:
                            # Going to try and access though dictionary-like structure if the attribute access fails
                            candidate = response.result.candidates[0]

                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                generated_content = candidate.content.parts[0].text
                            else:
                                # As a last resport going to try string rep ans parsing
                                response_str = str(response)
                                logger.info(f"Attempting to parse from string representation: {response_str[:500]}...")
                                text_match = re.search(r'"text": "(.+?)"', response_str, re.DOTALL)

                                if text_match:
                                    generated_content = text_match.group(1).replace('\\n', '\n')
                                else:
                                    raise ValueError("Could not extract text from response")
                        except Exception as e:
                            logger.error(f"Failed to extract text from response: {str(e)}")
                            raise ValueError(f"Could not extract text from Gemini response: {str(e)}")
                else:
                    # If all else fails, log the response structure and raise an error
                    logger.error(f"Unexpected response structure: {type(response)}, dir: {dir(response)}")
                    raise ValueError("Unexpected response structure from Gemini API")

            else:
                raise ValueError(f"Unsupported model. Type must be either 'gemma' or 'gemini'")

            # Ensure generated_content is not None
            if generated_content is None:
                raise ValueError("Failed to generate content - received None")

            logger.info(f"Generated content length: {len(generated_content)}")
            return generated_content

        except Exception as e:
            logger.error(f"Error in generate_markdown: {str(e)}")
            raise RuntimeError(f"Failed to generate content: {str(e)}")