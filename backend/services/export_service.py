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
        raise FileNotFoundError(f"Google API credentials file not found at {credentials_path}")

    # if the creds exist, then load them
    if os.path.exists(token_path):
        with open(token_path, 'r') as token_file:
            token_data = token_file.read()
            self.creds = Credentials.from_authorized_user_info(json.loads(token_data), self.scopes)

    # if creds don't exist/invalid
    if not self.creds or not self.creds.valid:
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.creds)
            self.creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(self.creds.to_json())

    # Now build the services
    self.slides_service = build('slides', 'v1', credentials=self.creds)
    self.drive_service = build('drive', 'v3', credentials=self.creds)
    logger.info("Successfully authenticated with Google Slides API")

def parse_markdown(self, markdown_content):
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
    # replace bullet points with plain text bullets
    content = re.sub(r'^\s*[-*]\s+', '• ', content, flags=re.MULTILINE)

    # remove code blocks and replace with plain text
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

    # remove emphasis markers -> * and _
    content = re.sub(r'(\*\*|__|\*|_)', '', content)

    return content


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
        self.authenticate()

        # Create new presentation
        presentation = self.slides_service.presentations().create(body={'title': title}).execute()
        presentation_id = presentation.get('presentationId')
        logger.info(f"Created new presentation with ID: {presentation_id}")

        # Parse markdown into slides
        slides = self.parse_markdown_for_slides(markdown_content)

        # Batch requests for slide creation
        requests = []

        # Delete default slide (1st slide)
        requests.append({
            'deleteObject': {
                'objectId': 'p'
            }
        })

        for i, slide in enumerate(slides):
            slide_id = f'slide_{i}'

            # Create new slide
            requests.append({
                'createSlide': {
                    'objectId': slide_id,
                    'slideLayoutReference': {
                        'predefinedLayout': 'TITLE_AND_BODY'
                    },
                }
            })

            # Add title to slide
            requests.append({
                'insertText': {
                    'objectId': f'{slide_id}_title',
                    'insertionIndex': 0,
                    'text': slide['title']
                }
            })

            # Format content for slides
            formatted_content = self.format_content_for_slides(slide['content'])

            # Add content to slide
            requests.append({
                'insertText': {
                    'objectId': f'{slide_id}_body',
                    'insertionIndex': 0,
                    'text': formatted_content
                }
            })

        # Execute batch update
        try:
            self.slides_service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': requests}
            ).execute()
            logger.info(f"Successfully added {len(slides)} slides to presentation")
        except Exception as e:
            logger.error(f"Error updating presentation: {str(e)}")
            # More detailed approach to slides creation if batch update fails
            self.create_slides_individually(presentation_id, slides)


        # Get presentation URL
        presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"

        return {
            'presentation_id': presentation_id,
            'presentation_url': presentation_url,
            'slide_count': len(slides)
        }


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

