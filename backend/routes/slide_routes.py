from flask import Blueprint, request, jsonify
import logging
import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.prompt_engine import PromptEngine
from backend.services.llm_engine import LLMEngine
from backend.services.verification_service import VerificationService


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

slide_bp = Blueprint('slides', __name__)

@slide_bp.route('/generate', methods=['POST'])
def generate_slides():
    """
    Endpoint for generating slide deck from user prompt.
    """
    logger.info("Received a request to generate slide content.")

    try:
        # Get prompt from request
        if not request.is_json:
            raise ValueError("Request must be JSON")

        data = request.get_json()
        if not data or 'prompt' not in data:
            raise ValueError("No prompt provided in request")

        prompt = str(data['prompt'])  # Ensure prompt is string
        logger.info(f"Received prompt: {prompt[:50]}...")

        try:
            logger.info(f"starting services")
            # Initialize services
            prompt_engine = PromptEngine()
            llm_engine = LLMEngine()
            verification_service = VerificationService()

        except Exception as init_error:
            logger.error(f"Detailed initialization error: {str(init_error)}")
            logger.error(f"Error type: {type(init_error)}")
            raise RuntimeError(f"Service initialization failed: {str(init_error)}")

        # Process prompt
        logger.info("About to validate prompt")
        validated_prompt = prompt_engine.validate_prompt(prompt)
        prepared_prompt = prompt_engine.prepare_prompt(validated_prompt)
        logger.info("Prompt validated!!")

        # Generate markdown
        markdown_content = llm_engine.generate_markdown(prepared_prompt)
        if not isinstance(markdown_content, str):
            markdown_content = str(markdown_content)

        logger.info("Successfully generated markdown content")

        # Verify content
        verified_content = verification_service.verify_markdown(markdown_content)

        # Return generated markdown
        return jsonify({
            'status': 'success',
            # 'markdown': markdown_content
            'markdown': verified_content
        }), 200

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 400

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500