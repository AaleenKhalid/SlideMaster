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

            # Now to test the connection to Ollama
            # try:
            #     logger.info("Attempting to connect to Ollama")
            #     # response = ollama.list()
            #     # models = response.get('models', [])
            #     # available_models = []
            #     models = ollama.list()
            #     available_models = [model['name'] for model in models.get('models', [])]
            #     # for model in models:
            #     #     if isinstance(model, 'dict') and 'name' in model:
            #     #         available_models.append(model['name'])
            #
            #
            #     if self.model_name not in available_models:
            #         logger.warning(f"Model {self.model_name} not found in Ollama.")
            #         logger.info(f"Get the model by using the command: ollama pull {self.model_name}")
            #     else:
            #         logger.info(f"Successfully connected to Ollama with Gemma2")
            #
            # except Exception as e:
            #     raise RuntimeError(f"Failed to connect to Ollama: {str(e)}")

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
            # System prompt for slide deck generation
            system_prompt = """You are an AI slide deck generator using the Gemma model.
            Create a professional slide deck outline in markdown format.
            Use clear headings, bullet points, and well-structured sections.
            Create content that is engaging and visually structured."""

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
                options={"temperature": 0.7},
                stream=False
            )

            logger.info(response)

            if response and 'messages' in response:
                return response['messages']['content']
            else:
                raise ValueError("Invalid response format from Gemma2")

        except Exception as e:
            logger.error(f"Error in generate_markdown: {str(e)}")
            raise RuntimeError(f"Failed to generate content: {str(e)}")