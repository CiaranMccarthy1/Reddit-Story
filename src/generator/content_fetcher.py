import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

class ContentFetcher:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        self.client = genai.Client(api_key=self.api_key)

    def _get_prompt(self, filePath):
        try:
            with open(filePath, 'r') as file:
                file_content = file.read()

            return file_content
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{filePath}' was not found.")
        except IOError as e:
            raise IOError(f"An error occurred while reading the file '{filePath}': {e}")

    def generate_script(self, filePath, duration=60):
        """Fetches the story + timestamped script from Gemini."""
        base_prompt = self._get_prompt(filePath)
        
        # Inject duration instruction
        duration_instruction = f"\nPlease ensure the generated script is approximately {duration} seconds long when narrated."
        final_prompt = base_prompt + duration_instruction
        
        print(f"Fetching story from Gemini (Target Duration: {duration}s)...")

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_prompt
        )


        return response.text.strip()
