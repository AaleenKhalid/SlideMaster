import os
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
    def __init__(self, model_type="gemma"):
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
            if not isinstance(prepared_prompt, str):
                prepared_prompt = str(prepared_prompt)

            logger.info(f"Generating content with {self.model_type}")

            # System prompt for slide deck generation - helps "prime" model before it receives actual user request.
            system_prompt = """You are an AI slide deck generator dealing with content in the field of computer science.
            Create a professional slide deck outline in markdown format.
            Use clear headings, bullet points with detailed information, and well-structured sections.
            Create content that is engaging and visually structured."""

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
                generated_content = response.text

            else:
                raise ValueError(f"Unsupported model. Type must be either 'gemma' or 'gemini'")

        except Exception as e:
            logger.error(f"Error in generate_markdown: {str(e)}")
            raise RuntimeError(f"Failed to generate content: {str(e)}")