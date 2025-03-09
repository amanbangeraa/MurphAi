import os
import google.generativeai as genai
from dotenv import load_dotenv 




load_dotenv()
def realtime_search(text):
    try:
        # Get the API key from the environment variable
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

        # Check if the API key is set
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable must be set.")

        # Initialize the Gemini client
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")  # Or "gemini-pro-vision" if using images

        # Get user input
        user_input = text

        # Generate content using the model
        response = model.generate_content(user_input)

        # Print the generated text
        print(response.text)

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        
realtime_search("What is the capital of France?")