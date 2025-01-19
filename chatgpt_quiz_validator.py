import os
import sys

from prompts import generic_prompt

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from openai import OpenAI
# from prompts.generic_prompt import generic_prompt
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class QuizValidator:
    def __init__(self):
        """Initialize the QuizValidator with OpenAI client and environment configurations."""
        self.environment = os.getenv("ENVIRONMENT", "dev").lower()

        # Set API key based on the environment
        if self.environment == "prod":
            self.api_key = os.getenv("API_KEY")
        elif self.environment == "dev":
            self.api_key = os.getenv("API_KEY")
        else:
            logger.error("Invalid ENVIRONMENT value. Must be 'prod' or 'dev'.")
            raise ValueError("Invalid ENVIRONMENT value.")

        if not self.api_key:
            logger.error("API key is missing in the environment variables.")
            raise ValueError("API key is required.")

        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"QuizValidator initialized in {self.environment} mode.")

    def _create_prompt(self, content: str) -> str:
        """Create the prompt for the API call."""
        prompt = generic_prompt.quiz_validation.replace("{content}", content)
        return prompt

    def chatgpt_generator(self, content):
        """Generate a response from the OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model="o1-mini",
                messages=[{"role": "assistant", "content": content}]
            )
            response_content = response.choices[0].message.content
            logger.info(f"Response from OpenAI: {response_content}")
            return response_content
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            return None

    def validate_quiz(self, content):
        """Validate the quiz content."""
        logger.info("Validating quiz content.")
        return self.chatgpt_generator(self._create_prompt(content))

    def save_validated_quiz(self, file_path, validated_content):
        """Save the validated quiz content as 'validated_quiz.tex'."""
        try:
            validated_file_path = file_path.replace("raw_quiz.tex", "validated_quiz.tex")
            os.makedirs(os.path.dirname(validated_file_path), exist_ok=True)
            with open(validated_file_path, 'w', encoding='utf-8') as file:
                file.write(validated_content)
            logger.info(f"Validated quiz saved to: {validated_file_path}")
        except Exception as e:
            logger.error(f"Error saving validated quiz: {str(e)}")


def process_quiz_files():
    """
    Process all raw_quiz.tex files found in the downloads directory,
    validate them, and save the output as validated_quiz.tex in the same folder structure.
    """
    # Define the path to the downloads directory
    downloads_dir = os.path.join(os.getcwd(), "downloads", "narayana")

    # Initialize QuizValidator instance
    quiz_validator = QuizValidator()

    # Walk through the downloads directory and process raw_quiz.tex files
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file == "raw_quiz.tex":
                file_path = os.path.join(root, file)

                try:
                    # Read the content of the raw_quiz.tex file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Validate the quiz content
                    validated_content = quiz_validator.validate_quiz(content)

                    if validated_content:
                        # Save the validated quiz as 'validated_quiz.tex' in the same folder structure
                        quiz_validator.save_validated_quiz(file_path, validated_content)
                    else:
                        logger.error(f"Validation failed for {file_path}. No content to save.")
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")


# Example usage
if __name__ == "__main__":
    process_quiz_files()
