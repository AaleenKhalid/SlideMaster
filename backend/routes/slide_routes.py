from flask import Blueprint, request, jsonify
import logging
import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.prompt_engine import PromptEngine
from backend.services.llm_engine import LLMEngine
from backend.services.verification_service import VerificationService
from backend.services.export_service import ExportService


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

        show_annotations = data.get('show_annotations', True) # going to make default be true

        prompt = str(data['prompt'])  # Ensure prompt is string
        logger.info(f"Received prompt: {prompt}")

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
        logger.info("Successfully generated markdown content")

        if not isinstance(markdown_content, str):
            markdown_content = str(markdown_content)

        verified_content = ""
        verification_failed = False
        final_markdown = ""
        verification_results = None

        try:
            # 1st want to validate the structure
            verified_content, verification_results = verification_service.verify_markdown(markdown_content)

            # want to get the verification status next
            verification_success = verification_results.get("verified", False)
            logger.info(f"Verification results: {verification_success}")

            # create annotated version & figure out which one to return
            if show_annotations:
                # create markdown with verification highlights
                annotated_markdown = verification_service.annotate_markdown(verified_content, verification_results)
                final_markdown = annotated_markdown
                logger.info("Created annotated markdown with verification highlights")
            else:
                # Else use the original markdown without the annotations
                final_markdown = verified_content
                logger.info("Using original markdown")

        except Exception as verification_error:
            logger.error(f"Verification error: {str(verification_error)}")
            final_markdown = markdown_content
            verified_content = markdown_content # just setting as default
            verification_results = None
            logger.info("Using original content due to verification error")

        # # Determine which content to return based on verification results
        # if verified_content is not None:
        #     final_markdown = verified_content
        #     logger.info("Using verified content")
        # else:
        #     # Fall back to the original content if verification failed
        #     final_markdown = markdown_content
        #     logger.info("Using original unverified content due to verification failure")

        # Ensure final_markdown is a string
        if not isinstance(final_markdown, str):
            final_markdown = str(final_markdown)

        # Return generated markdown with verification info
        return jsonify({
            'status': 'success',
            'markdown': final_markdown, # this will be annotated it that setting is set
            'original_markdown': markdown_content,
            'verified': verification_results.get('verified', False) if verification_results else False,
            'verification_message': verification_results.get('message', 'Verification not performed') if verification_results else 'Verification failed',
            'verification_summary': verification_results.get('verification_summary', {}) if verification_results else {}
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


@slide_bp.route('/export_to_slides', methods=['POST'])
def export_to_slides():
    """
    Endpoint for exporting markdown content to Google Slides.
    """
    logger.info("Received request to export content to Google Slides.")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")

    try:
        # Get markdown content from request
        if not request.is_json:
            logger.error("Request is not JSON")
            logger.error(f"Request data: {request.data}")
            raise ValueError("Request must be JSON")

        data = request.get_json()
        logger.info(f"Received data keys: {list(data.keys()) if data else None}")

        if not data or 'markdown' not in data:
            raise ValueError("No markdown content provided in request")

        markdown_content = data['markdown']
        title = data.get('title', 'Generated Slide Deck')

        logger.info(f"Creating presentation with title: {title}")
        logger.info(f"Markdown content length: {len(markdown_content)}")

        slides_export_service = ExportService()

        try:
            # Create Google Slides presentation
            result = slides_export_service.create_google_slides(markdown_content, title)

            logger.info(f"Successfully created presentation: {result['presentation_id']}")

            return jsonify({
                'status': 'success',
                'presentation_id': result['presentation_id'],
                'presentation_url': result['presentation_url'],
                'slide_count': result['slide_count']
            }), 200

        except Exception as e:
            logger.error(f"Error creating Google Slides: {str(e)}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': f"Failed to create Google Slides presentation: {str(e)}"
            }), 500

    except FileNotFoundError as fe:
        logger.error(f"Google API credentials not found: {str(fe)}")
        return jsonify({
            'status': 'error',
            'message': "Google API credentials not found. Please set up Google API credentials first.",
            'error_type': 'credentials_missing'
        }), 400
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error during export: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Failed to export to Google Slides: {str(e)}"
        }), 500