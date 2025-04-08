import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import re

logger = logging.getLogger(__name__)

class ExportService:
    """
    Handles exporting markdown content to Google Slides
    """
    def __init__(self):
        """Initialises the Google Slides API Client"""
        self.slides_service = None
        self.drive_service = None
        self.creds = None
        self.scopes = ['https://www.googleapis.com/auth/presentations',
                       'https://www.googleapis.com/auth/drive']



    def authenticate(self):
        """Authenticates with google API"""
        # get path to credentials file
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        'credentials.json')
        token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  'token.json')

        logger.info(f"Looking for credentials at {credentials_path}")

        if not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found at {credentials_path}")
            raise FileNotFoundError(f"Google API credentials file not found at {credentials_path}")

        # if the creds exist, then load them
        if os.path.exists(token_path):
            logger.info(f"Found existing token at {token_path}")
            with open(token_path, 'r') as token_file:
                token_data = token_file.read()
                self.creds = Credentials.from_authorized_user_info(json.loads(token_data), self.scopes)
                logger.info("Loaded credentials from token file")

        # if creds don't exist/invalid
        if not self.creds or not self.creds.valid:
            logger.info("Credentials need to be refreshed or created")
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Refreshing expired credentials")
                self.creds.refresh(Request())
            else:
                logger.info("Creating new credentials")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.scopes)
                self.creds = flow.run_local_server(port=0)

            logger.info("Saving new token")
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())

        # Now build the services
        logger.info("Building API services")
        self.slides_service = build('slides', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        logger.info("Successfully authenticated with Google Slides API")


    def parse_markdown_for_slides(self, markdown_content):
        """
        Parse markdown content into slide structure.

        :param self:
        :param markdown_content: the generated markdown content
        :return: list of slide objects with title and content
        """

        logger.info("Parsing markdown content for slides")
        slides = []

        # split content by using slide separators
        # 1st going to try ---
        sections = re.split(r'\n\s*---\s*\n', markdown_content)

        # if only one section but multiple headers, try split by headers
        if len(sections) <= 1 and '#' in markdown_content: #TODO - might need to fix this
            sections = re.split(r'\n\s*(#+)\s+', markdown_content)

            # Since 1st item won't have header prefix, need to handle that
            if sections[0]:
                content = sections.pop(0).strip()
                if content:
                    slides.append({
                        'title': 'Introduction',
                        'content': content
                    })

            # want to process the rest of the sections with the header markers
            for i in range(0, len(sections), 2):
                if i +1 < len(sections):
                    header_level = sections[i] # contains the # markers
                    content = sections[i+1].strip()

                    # Extract title from 1st line
                    lines = content.split('\n', 1)
                    title = lines[0].strip()
                    body = lines[1].strip() if len(lines) > 1 else ''

                    slides.append({
                        'title': title,
                        'content': body
                    })

            return slides

        # want to process each section from -----
        for section in sections:
            lines = section.strip().split('\n')
            slide_title = None
            slide_content = []

            for line in lines:
                # look for headings as slide titles
                heading_match = re.match(r'^#+\s+(.+)$', line)
                if heading_match and not slide_title:
                    slide_title = heading_match.group(1)
                else:
                    slide_content.append(line)

            if not slide_title and slide_content:
                # if no heading found, use first line as title
                slide_title = slide_content[0]
                slide_content = slide_content[1:]

            # create the slide object
            if slide_title:
                slides.append({
                    'title': slide_title,
                    'content': '\n'.join(slide_content).strip()
                })

        # If still don't have slides, create single slide with all the content
        if not slides and markdown_content.strip():
            slides.append({
                'title': 'Generated Content',
                'content': markdown_content.strip()
            })

        logger.info(f"Successfully parsed markdown into {len(slides)} slides")
        return slides


    def format_content_for_slides(self, content):
        """
        Format markdown content for Google Slides
        Converts markdown bullet points into plaintext

        :param self:
        :param content: generated markdown content
        :return: plain text of markdown content
        """
        if not content:
            return ""

        logger.info(f"Formatting content of length {len(content)}")

        try:
            # Replace markdown bullet points with presentation-friendly bullets
            content = re.sub(r'^\s*[-*]\s+', '• ', content, flags=re.MULTILINE)

            # Remove code blocks and replace with plain text
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

            # Remove emphasis markers
            content = re.sub(r'(\*\*|__|\*|_)', '', content)

            # Remove any HTML tags
            content = re.sub(r'<.*?>', '', content)

            # Remove any markdown links but keep the text
            content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)

            # Ensure reasonable line length
            if len(content) > 10000:
                content = content[:10000] + "... (content truncated)"

            return content
        except Exception as e:
            logger.error(f"Error formatting content: {e}")

        # Return a simplified version if there's an error
        return content.replace('*', '').replace('#', '').replace('_', '')


    def create_google_slides(self, markdown_content, title="Generated Slide Deck"):
        """
        Creates a Google Slides presentation from the markdown content.

        :param self:
        :param markdown_content: generated content to convert
        :param title: the title of the presentation
        :return: dictionary containing details of created presentation
        """
        # make sure authenticated
        if not self.slides_service:
            logger.info("No slides service found, authenticating")
            self.authenticate()

        # Create new presentation
        logger.info(f"Creating new presentation with title: {title}")
        presentation = self.slides_service.presentations().create(body={'title': title}).execute()
        presentation_id = presentation.get('presentationId')
        logger.info(f"Created new presentation with ID: {presentation_id}")

        # Parse markdown into slides
        slides_data = self.parse_markdown_for_slides(markdown_content)
        logger.info(f"Parsed markdown into {len(slides_data)} slides")

        # need to track created slides
        created_slides = []

        try:
            # First, get the initial presentation to see if there's a default slide
            presentation_details = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()

            existing_slides = presentation_details.get('slides', [])
            first_slide_used = False

            # Process each slide data
            for i, slide_data in enumerate(slides_data):
                try:
                    # Format content for better display
                    formatted_content = self.format_content_for_slides(slide_data['content'])

                    # If this is the first slide and we have an existing default slide, update it
                    if i == 0 and existing_slides and not first_slide_used:
                        first_slide_used = True
                        first_slide = existing_slides[0]
                        first_slide_id = first_slide['objectId']
                        created_slides.append(first_slide_id)

                        # Find title and body elements
                        found_elements = self._find_title_and_body_elements(first_slide)
                        if found_elements:
                            title_id, body_id = found_elements
                            # Update the existing slide
                            update_requests = []

                            if title_id:
                                update_requests.append({
                                    'deleteText': {
                                        'objectId': title_id,
                                        'textRange': {
                                            'type': 'ALL'
                                        }
                                    }
                                })
                                update_requests.append({
                                    'insertText': {
                                        'objectId': title_id,
                                        'insertionIndex': 0,
                                        'text': slide_data['title']
                                    }
                                })

                            if body_id:
                                update_requests.append({
                                    'deleteText': {
                                        'objectId': body_id,
                                        'textRange': {
                                            'type': 'ALL'
                                        }
                                    }
                                })
                                update_requests.append({
                                    'insertText': {
                                        'objectId': body_id,
                                        'insertionIndex': 0,
                                        'text': formatted_content
                                    }
                                })

                            if update_requests:
                                self.slides_service.presentations().batchUpdate(
                                    presentationId=presentation_id,
                                    body={'requests': update_requests}
                                ).execute()
                                logger.info(f"Updated existing slide with title: {slide_data['title']}")
                        else:
                            logger.warning("Could not find title/body elements in default slide")
                    else:
                        # Create a new slide with basic TITLE_AND_BODY layout
                        create_request = {
                            'createSlide': {
                                'slideLayoutReference': {
                                    'predefinedLayout': 'TITLE_AND_BODY'
                                }
                            }
                        }

                        slide_response = self.slides_service.presentations().batchUpdate(
                            presentationId=presentation_id,
                            body={'requests': [create_request]}
                        ).execute()

                        # Get the new slide ID
                        if 'replies' in slide_response and len(slide_response['replies']) > 0:
                            new_slide_id = slide_response['replies'][0]['createSlide']['objectId']
                            created_slides.append(new_slide_id)

                            # Get the full slide details to find the elements
                            slide_details = self.slides_service.presentations().get(
                                presentationId=presentation_id
                            ).execute()

                            # Find the newly created slide
                            new_slide = None
                            for slide in slide_details.get('slides', []):
                                if slide['objectId'] == new_slide_id:
                                    new_slide = slide
                                    break

                            if new_slide:
                                # Find title and body elements
                                found_elements = self._find_title_and_body_elements(new_slide)
                                if found_elements:
                                    title_id, body_id = found_elements

                                    # Add content to the slide
                                    content_requests = []

                                    if title_id:
                                        content_requests.append({
                                            'insertText': {
                                                'objectId': title_id,
                                                'insertionIndex': 0,
                                                'text': slide_data['title']
                                            }
                                        })

                                    if body_id:
                                        content_requests.append({
                                            'insertText': {
                                                'objectId': body_id,
                                                'insertionIndex': 0,
                                                'text': formatted_content
                                            }
                                        })

                                    # Apply text formatting for better readability

                                    if content_requests:
                                        self.slides_service.presentations().batchUpdate(
                                            presentationId=presentation_id,
                                            body={'requests': content_requests}
                                        ).execute()
                                        logger.info(f"Added content to slide with title: {slide_data['title']}")
                                else:
                                    logger.warning(f"Could not find title/body elements in slide {new_slide_id}")
                            else:
                                logger.warning(f"Could not retrieve created slide {new_slide_id}")
                        else:
                            logger.warning("Failed to get new slide ID from response")

                except Exception as e:
                    logger.error(f"Error processing slide {i}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error during slide creation: {str(e)}", exc_info=True)
            logger.warning("Slide creation encountered errors but will return the presentation URL anyway")

        # Get presentation URL
        presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
        logger.info(f"Presentation URL: {presentation_url}")

        return {
            'presentation_id': presentation_id,
            'presentation_url': presentation_url,
            'slide_count': len(created_slides)
        }


    def _find_title_and_body_elements(self, slide):
        """
        Helper method to find title and body elements in a slide.

        :param slide: Slide object from Google Slides API
        :return: Tuple of (title_id, body_id) or None if not found
        """
        title_id = None
        body_id = None

        for element in slide.get('pageElements', []):
            shape = element.get('shape', {})
            placeholder = shape.get('placeholder', {})

            if placeholder:
                placeholder_type = placeholder.get('type')
                if placeholder_type == 'TITLE' or placeholder_type == 'CENTERED_TITLE':
                    title_id = element['objectId']
                elif placeholder_type == 'BODY' or placeholder_type == 'SUBTITLE':
                    body_id = element['objectId']

        if title_id or body_id:
            return (title_id, body_id)

        # Fallback: If no placeholder types, try to identify by shape type and index
        for element in slide.get('pageElements', []):
            shape = element.get('shape', {})
            if shape.get('shapeType') == 'TEXT_BOX':
                # Try to guess which is title/body based on position
                # Title is typically at the top
                y_position = element.get('transform', {}).get('translateY', 0)
                if not title_id and y_position < 150:  # Likely a title
                    title_id = element['objectId']
                elif not body_id and y_position >= 150:  # Likely a body
                    body_id = element['objectId']

        return (title_id, body_id) if (title_id or body_id) else None


    def create_slides_individually(self, presentation_id, slides):
        """
        Create slides one by one as fallback method
        """
        logger.info("Attempting to create slides individually")

        # Get current presentation
        presentation = self.slides_service.presentations().get(
            presentationId=presentation_id
        ).execute()

        # Get existing slides
        existing_slides = presentation.get('slides', [])

        # If there's default slide, try to reuse it for first slide
        first_slide_id = existing_slides[0]['objectId'] if existing_slides else None

        for i, slide in enumerate(slides):
            try:
                if i == 0 and first_slide_id:
                    # Update first slide
                    requests = [
                        {
                            'insertText': {
                                'objectId': f'{first_slide_id}.p',  # Title placeholder
                                'text': slide['title']
                            }
                        },
                        {
                            'insertText': {
                                'objectId': f'{first_slide_id}.c',  # Body placeholder
                                'text': self.format_content_for_slides(slide['content'])
                            }
                        }
                    ]
                else:
                    # Create new slide
                    requests = [
                        {
                            'createSlide': {
                                'slideLayoutReference': {
                                    'predefinedLayout': 'TITLE_AND_BODY'
                                }
                            }
                        }
                    ]

                    # Execute to get new slide ID
                    response = self.slides_service.presentations().batchUpdate(
                        presentationId=presentation_id,
                        body={'requests': requests}
                    ).execute()

                    # Get new slide ID
                    new_slide_id = response['replies'][0]['createSlide']['objectId']

                    # Now add content to new slide
                    text_requests = [
                        {
                            'insertText': {
                                'objectId': f'{new_slide_id}.p',  # Title placeholder
                                'text': slide['title']
                            }
                        },
                        {
                            'insertText': {
                                'objectId': f'{new_slide_id}.c',  # Body placeholder
                                'text': self.format_content_for_slides(slide['content'])
                            }
                        }
                    ]

                    # Execute text insertion
                    self.slides_service.presentations().batchUpdate(
                        presentationId=presentation_id,
                        body={'requests': text_requests}
                    ).execute()

            except Exception as e:
                logger.error(f"Error creating slide {i}: {str(e)}")
                # Continue with the next slide
                continue

        logger.info("Finished creating slides individually")

