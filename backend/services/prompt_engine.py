class PromptEngine:
    """
    Handles prompt validation, processing, and preparation for the LLM.
    """
    def __init__(self, max_length=1000, min_length=2):  # Reduced min_length for testing
        self.max_length = max_length
        self.min_length = min_length

    def validate_prompt(self, prompt):
        """
        Validate the input prompt.
        """
        if not isinstance(prompt, str):
            prompt = str(prompt)

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if len(prompt) < self.min_length:
            raise ValueError(f"Prompt must be at least {self.min_length} characters")

        if len(prompt) > self.max_length:
            raise ValueError(f"Prompt cannot exceed {self.max_length} characters")

        return prompt.strip()

    def prepare_prompt(self, prompt):
        """
        Prepare the prompt for LLM processing.
        """
        formatted_prompt = f"""
        Create a professional markdown-formatted slide deck outline based on the following prompt:

        PROMPT: {prompt}

        GUIDELINES:
        - Create clear section headings using markdown (#, ##, ###)
        - Include bullet points for key information
        - Ensure content is well-structured and professional
        - Include an introduction and conclusion section
        - Separate the content for each slide using a slide number 
        """
        return formatted_prompt