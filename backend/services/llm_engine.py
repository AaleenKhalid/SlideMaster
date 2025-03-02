import ollama
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class LLMEngine:
    """
     This will handle the interactions with Gemma2 through Ollama
    """
    def __init__(self):
        """
         Initialise LLMEngine with Gemma2
        """
        try:
            #load_dotenv() # Skipping as might cause issues
            self.model_name = "gemma:2b"
            logger.info(f"LLM Engine initialized with model: {self.model_name}")

        except Exception as e:
            logger.error(f"Error initializing LLM Engine: {str(e)}")
            raise RuntimeError(f"Failed to initialize LLM Engine: {str(e)}")



    def generate_markdown(self, prepared_prompt):
        """
        Generate markdown content using Gemma2.

        :param prepared_prompt: Processed prompt from PromptEngine
        :return: Generated markdown content
        """
        try:
            if not isinstance(prepared_prompt, str):
                prepared_prompt = str(prepared_prompt)

            logger.info("Generating content with Gemma2")

            # System prompt for slide deck generation - helps "prime" model before it receives actual user request.
            system_prompt = """You are an AI slide deck generator dealing with content in the field of computer science.
            Create a professional slide deck outline in markdown format.
            Use clear headings, bullet points with detailed information, and well-structured sections.
            Create content that is engaging and visually structured."""

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
            return generated_content

        except Exception as e:
            logger.error(f"Error in generate_markdown: {str(e)}")
            raise RuntimeError(f"Failed to generate content: {str(e)}")